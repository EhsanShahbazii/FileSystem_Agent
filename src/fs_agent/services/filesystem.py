from __future__ import annotations
import glob
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

@dataclass(slots=True)
class FileSandbox:
    """Guard filesystem operations inside a sandbox directory."""
    root: Path

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    # ---------- internal helpers ----------
    def _resolve(self, rel: str) -> Tuple[Path, Path]:
        """Return (sandbox_abs, target_abs) and ensure target is inside sandbox."""
        sandbox = self.root.resolve()
        target = (self.root / rel).resolve()
        if not (target == sandbox or str(target).startswith(str(sandbox) + self._sep())):
            raise ValueError(f"For security reasons, paths must stay inside {sandbox}. Got: {target}")
        return sandbox, target

    @staticmethod
    def _sep() -> str:
        import os
        return os.sep

    @staticmethod
    def _format_size(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024:
                return f"{n:.0f} {unit}"
            n /= 1024
        return f"{n:.0f} PB"

    def tree(self, base: Path, max_depth: int = 2) -> str:
        """Return a pretty tree for base (inside sandbox)."""
        base = base.resolve()
        lines: List[str] = [f"{base.name}/"]
        if max_depth < 0:
            return "\n".join(lines)

        def walk(dir_path: Path, prefix: str, depth: int) -> None:
            if depth > max_depth:
                return
            try:
                entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except PermissionError:
                lines.append(prefix + "└── [permission denied]")
                return

            total = len(entries)
            for i, p in enumerate(entries):
                last = (i == total - 1)
                branch = "└── " if last else "├── "
                if p.is_dir():
                    lines.append(prefix + branch + p.name + "/")
                    new_prefix = prefix + ("    " if last else "│   ")
                    walk(p, new_prefix, depth + 1)
                else:
                    try:
                        size = self._format_size(p.stat().st_size)
                    except Exception:
                        size = "?"
                    lines.append(prefix + branch + f"{p.name} ({size})")

        walk(base, "", 1)
        return "\n".join(lines)

    # ---------- public ops (1:1 with your tools) ----------
    def list_dir(self, path: str = ".", tree: bool = True, max_depth: int = 2) -> str:
        self.ensure()
        _, p = self._resolve(path)
        if not p.exists():
            raise ValueError(f"Path {path} does not exist.")
        if tree:
            return self.tree(p, max_depth=max_depth)
        if p.is_file():
            st = p.stat()
            return f"{p.name}\t{self._format_size(st.st_size)}"
        names = []
        for child in sorted(p.iterdir(), key=lambda c: (c.is_file(), c.name.lower())):
            label = child.name + ("/" if child.is_dir() else "")
            try:
                size = self._format_size(child.stat().st_size) if child.is_file() else "-"
            except Exception:
                size = "?"
            names.append(f"{label}\t{size}")
        return "\n".join(names) if names else "(empty)"

    def read_file(self, path: str, max_bytes: int = 200_000) -> str:
        self.ensure()
        _, file_path = self._resolve(path)
        if not file_path.exists() or not file_path.is_file():
            raise ValueError(f"File {path} does not exist.")
        size = file_path.stat().st_size
        if size > max_bytes:
            raise ValueError(f"File is {size} bytes; exceeds limit {max_bytes}. Increase max_bytes if needed.")
        return file_path.read_text(encoding="utf-8", errors="replace")

    def write_file(self, path: str, content: str) -> str:
        self.ensure()
        _, file_path = self._resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content or "", encoding="utf-8")
        return str(file_path)

    def append_file(self, path: str, content: str) -> str:
        self.ensure()
        _, file_path = self._resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(content or "")
        return str(file_path)

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> str:
        self.ensure()
        _, s = self._resolve(src)
        _, d = self._resolve(dst)
        if not s.exists() or not s.is_file():
            raise ValueError(f"Source file {src} does not exist.")
        if d.exists() and not overwrite:
            raise ValueError(f"Destination {dst} already exists. Use overwrite=True.")
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
        return str(d)

    def move_file(self, src: str, dst: str, overwrite: bool = False) -> str:
        self.ensure()
        _, s = self._resolve(src)
        _, d = self._resolve(dst)
        if not s.exists():
            raise ValueError(f"Source {src} does not exist.")
        if d.exists():
            if not overwrite:
                raise ValueError(f"Destination {dst} already exists. Use overwrite=True.")
            if s.is_file() and d.is_dir():
                raise ValueError("Cannot overwrite a directory with a file.")
            if s.is_dir() and d.is_file():
                raise ValueError("Cannot overwrite a file with a directory.")
            if d.is_file():
                d.unlink()
            else:
                shutil.rmtree(d)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return str(d)

    def create_file(self, path: str, content: str = "") -> str:
        self.ensure()
        _, file_path = self._resolve(path)
        if file_path.exists():
            raise ValueError(f"File {path} already exists.")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content or "", encoding="utf-8")
        return str(file_path)

    def create_files_sequence(self, prefix: str, suffix: str, start: int, end: int,
                              zero_pad: int = 0, content: str = "") -> str:
        self.ensure()
        created: List[str] = []
        skipped: List[str] = []
        for i in range(start, end + 1):
            num = str(i).zfill(zero_pad) if zero_pad > 0 else str(i)
            rel = f"{prefix}{num}{suffix}"
            _, p = self._resolve(rel)
            if p.exists():
                skipped.append(rel); continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content or "", encoding="utf-8")
            created.append(rel)
        return (
            "Created:\n" + ("\n".join(created) if created else "(none)") +
            "\n\nSkipped (already existed):\n" + ("\n".join(skipped) if skipped else "(none)")
        )

    def rename_file(self, old_path: str, new_path: str) -> str:
        self.ensure()
        _, old_file_path = self._resolve(old_path)
        _, new_file_path = self._resolve(new_path)
        if not old_file_path.exists():
            raise ValueError(f"File {old_path} does not exist.")
        new_file_path.parent.mkdir(parents=True, exist_ok=True)
        old_file_path.rename(new_file_path)
        return str(new_file_path)

    def rename_files_sequence(
        self,
        old_prefix: str, old_suffix: str,
        new_prefix: str, new_suffix: str,
        start: int, end: int, zero_pad: int = 0,
        skip_missing: bool = True, overwrite: bool = False
    ) -> str:
        self.ensure()
        renamed: List[str] = []
        missing: List[str] = []
        conflicted: List[str] = []
        for i in range(start, end + 1):
            num = str(i).zfill(zero_pad) if zero_pad > 0 else str(i)
            old_rel = f"{old_prefix}{num}{old_suffix}"
            new_rel = f"{new_prefix}{num}{new_suffix}"
            _, old_p = self._resolve(old_rel)
            _, new_p = self._resolve(new_rel)
            if not old_p.exists():
                if not skip_missing:
                    raise ValueError(f"Missing: {old_rel}")
                missing.append(old_rel); continue
            if new_p.exists():
                if not overwrite:
                    conflicted.append(new_rel); continue
                if new_p.is_file():
                    new_p.unlink()
                else:
                    shutil.rmtree(new_p)
            new_p.parent.mkdir(parents=True, exist_ok=True)
            old_p.rename(new_p)
            renamed.append(f"{old_rel} -> {new_rel}")
        return (
            "Renamed:\n" + ("\n".join(renamed) if renamed else "(none)") +
            "\n\nMissing:\n" + ("\n".join(missing) if missing else "(none)") +
            "\n\nConflicted (exists, not overwritten):\n" + ("\n".join(conflicted) if conflicted else "(none)")
        )

    def delete_file(self, path: str) -> str:
        self.ensure()
        _, file_path = self._resolve(path)
        if not file_path.exists():
            raise ValueError(f"File {path} does not exist.")
        if file_path.is_dir():
            raise ValueError("delete_file only deletes files, not directories.")
        file_path.unlink()
        return str(file_path)

    def delete_glob(self, pattern: str) -> str:
        self.ensure()
        matches: list[Path] = []
        for rel in glob.glob(str(self.root / pattern), recursive=True):
            p = Path(rel).resolve()
            sandbox = self.root.resolve()
            if not (str(p).startswith(str(sandbox) + self._sep()) or p == sandbox):
                continue
            if p.is_file():
                matches.append(p)
        if not matches:
            return "No files matched."
        for p in matches:
            p.unlink(missing_ok=True)
        return f"Deleted {len(matches)} files."

    def create_folder(self, path: str, exist_ok: bool = True) -> str:
        self.ensure()
        _, d = self._resolve(path)
        if d.exists() and not d.is_dir():
            raise ValueError(f"Path exists and is not a directory: {path}")
        d.mkdir(parents=True, exist_ok=exist_ok)
        return str(d)

    def create_folders_sequence(self, prefix: str, suffix: str = "", start: int = 1, end: int = 1, zero_pad: int = 0) -> str:
        self.ensure()
        created: List[str] = []
        skipped: List[str] = []
        for i in range(start, end + 1):
            num = str(i).zfill(zero_pad) if zero_pad > 0 else str(i)
            rel = f"{prefix}{num}{suffix}"
            _, d = self._resolve(rel)
            if d.exists():
                skipped.append(rel); continue
            d.mkdir(parents=True, exist_ok=True)
            created.append(rel)
        return (
            "Created:\n" + ("\n".join(created) if created else "(none)") +
            "\n\nSkipped (already existed):\n" + ("\n".join(skipped) if skipped else "(none)")
        )

    def delete_folder(self, path: str, recursive: bool = False) -> str:
        self.ensure()
        _, d = self._resolve(path)
        if not d.exists():
            raise ValueError(f"Folder {path} does not exist.")
        if not d.is_dir():
            raise ValueError(f"Path {path} is not a directory.")
        if recursive:
            shutil.rmtree(d)
            return f"Recursively deleted {path}"
        try:
            d.rmdir()
        except OSError:
            raise ValueError(f"Folder {path} is not empty. Use recursive=True.")
        return f"Deleted empty folder {path}"

    def bulk_rename_regex(self, base_path: str, pattern: str, replacement: str,
                          include_subdirs: bool = True, test_only: bool = False) -> str:
        self.ensure()
        _, base = self._resolve(base_path)
        if not base.exists():
            raise ValueError(f"Base path {base_path} does not exist.")
        if not base.is_dir():
            raise ValueError(f"Base path {base_path} is not a directory.")

        rx = re.compile(pattern)
        changes: List[str] = []
        walker = base.rglob("*") if include_subdirs else base.glob("*")
        for p in sorted(walker):
            if not p.is_file():
                continue
            new_name = rx.sub(replacement, p.name)
            if new_name != p.name:
                new_path = p.with_name(new_name)
                # checks security on target
                self._resolve(str(new_path.relative_to(self.root)))
                if not test_only:
                    if new_path.exists():
                        raise ValueError(f"Target already exists: {new_path.relative_to(self.root)}")
                    p.rename(new_path)
                changes.append(f"{p.relative_to(self.root)} -> {new_path.relative_to(self.root)}")
        if not changes:
            return "No matches."
        return ("Preview (no changes):\n" if test_only else "Renamed:\n") + "\n".join(changes)
