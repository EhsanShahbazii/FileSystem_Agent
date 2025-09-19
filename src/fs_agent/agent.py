from __future__ import annotations
from pydantic_ai import Agent, RunContext

from .services.filesystem import FileSandbox
from .services.calculator import CalculatorService

INSTRUCTIONS = (
    "You are a helpful assistant with access to these tools.\n\n"
    "Tools:\n"
    "- calculator: Calculates a math expression.\n"
    "- list_dir: List files/folders; optionally as a tree with depth.\n"
    "- read_file: Read a text file (with byte limit).\n"
    "- write_file: Create/overwrite a file with content.\n"
    "- append_file: Append content to a file.\n"
    "- copy_file: Copy a file.\n"
    "- move_file: Move/rename a file or folder.\n"
    "- create_file: Create a file (empty or with content).\n"
    "- create_files_sequence: Create many files for a numeric range.\n"
    "- rename_file: Rename a single file.\n"
    "- rename_files_sequence: Rename a numeric file series (swap prefix/suffix).\n"
    "- delete_file: Delete a single file.\n"
    "- delete_glob: Delete multiple files by glob pattern.\n"
    "- create_folder: Create a folder (parents ok).\n"
    "- create_folders_sequence: Create many folders for a numeric range.\n"
    "- delete_folder: Delete a folder; use recursive=true for non-empty.\n"
    "- bulk_rename_regex: Regex-based rename of files under a path.\n\n"
    "Usage guidance:\n"
    "• If asked to use the calculator, return only the numeric result (e.g., 2+2=4.0).\n"
    "• If asked to create files/folders without content, create them empty.\n"
    "• For patterns like '1_name.txt ... 10_name.txt', use create_files_sequence.\n"
    "• To retitle a numeric run (e.g., foo001.txt→bar001.txt), use rename_files_sequence.\n"
    "• For many renames not fitting the numeric pattern, use bulk_rename_regex.\n"
    "• If asked to remove all files, list current files then delete them.\n"
    "• Prefer the safest tool that matches the request; explain limits if a task isn't possible.\n"
)

class AgentFactory:
    """Creates an Agent and binds tools from our services."""

    @staticmethod
    def build(model, fs: FileSandbox, calc: CalculatorService) -> Agent:
        agent = Agent(model, instructions=INSTRUCTIONS, retries=3)

        @agent.tool
        async def calculator(ctx: RunContext[None], expression: str) -> float:
            return calc.evaluate(expression)

        @agent.tool
        async def list_dir(ctx: RunContext[None], path: str = ".", tree: bool = True, max_depth: int = 2) -> str:
            return fs.list_dir(path=path, tree=tree, max_depth=max_depth)

        @agent.tool
        async def read_file(ctx: RunContext[None], path: str, max_bytes: int = 200_000) -> str:
            return fs.read_file(path=path, max_bytes=max_bytes)

        @agent.tool
        async def write_file(ctx: RunContext[None], path: str, content: str) -> str:
            return fs.write_file(path=path, content=content)

        @agent.tool
        async def append_file(ctx: RunContext[None], path: str, content: str) -> str:
            return fs.append_file(path=path, content=content)

        @agent.tool
        async def copy_file(ctx: RunContext[None], src: str, dst: str, overwrite: bool = False) -> str:
            return fs.copy_file(src=src, dst=dst, overwrite=overwrite)

        @agent.tool
        async def move_file(ctx: RunContext[None], src: str, dst: str, overwrite: bool = False) -> str:
            return fs.move_file(src=src, dst=dst, overwrite=overwrite)

        @agent.tool
        async def create_file(ctx: RunContext[None], path: str, content: str = "") -> str:
            return fs.create_file(path=path, content=content)

        @agent.tool
        async def create_files_sequence(
            ctx: RunContext[None], prefix: str, suffix: str, start: int, end: int, zero_pad: int = 0, content: str = ""
        ) -> str:
            return fs.create_files_sequence(prefix=prefix, suffix=suffix, start=start, end=end, zero_pad=zero_pad, content=content)

        @agent.tool
        async def rename_file(ctx: RunContext[None], old_path: str, new_path: str) -> str:
            return fs.rename_file(old_path=old_path, new_path=new_path)

        @agent.tool
        async def rename_files_sequence(
            ctx: RunContext[None],
            old_prefix: str, old_suffix: str,
            new_prefix: str, new_suffix: str,
            start: int, end: int, zero_pad: int = 0,
            skip_missing: bool = True, overwrite: bool = False
        ) -> str:
            return fs.rename_files_sequence(
                old_prefix=old_prefix, old_suffix=old_suffix,
                new_prefix=new_prefix, new_suffix=new_suffix,
                start=start, end=end, zero_pad=zero_pad,
                skip_missing=skip_missing, overwrite=overwrite
            )

        @agent.tool
        async def delete_file(ctx: RunContext[None], path: str) -> str:
            return fs.delete_file(path=path)

        @agent.tool
        async def delete_glob(ctx: RunContext[None], pattern: str) -> str:
            return fs.delete_glob(pattern=pattern)

        @agent.tool
        async def create_folder(ctx: RunContext[None], path: str, exist_ok: bool = True) -> str:
            return fs.create_folder(path=path, exist_ok=exist_ok)

        @agent.tool
        async def create_folders_sequence(
            ctx: RunContext[None], prefix: str, suffix: str = "", start: int = 1, end: int = 1, zero_pad: int = 0
        ) -> str:
            return fs.create_folders_sequence(prefix=prefix, suffix=suffix, start=start, end=end, zero_pad=zero_pad)

        @agent.tool
        async def delete_folder(ctx: RunContext[None], path: str, recursive: bool = False) -> str:
            return fs.delete_folder(path=path, recursive=recursive)

        @agent.tool
        async def bulk_rename_regex(
            ctx: RunContext[None], base_path: str, pattern: str, replacement: str,
            include_subdirs: bool = True, test_only: bool = False
        ) -> str:
            return fs.bulk_rename_regex(
                base_path=base_path, pattern=pattern, replacement=replacement,
                include_subdirs=include_subdirs, test_only=test_only
            )

        return agent
