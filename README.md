# FS Agent (OOP)

![preview](https://ehsan.storage.iran.liara.space/github/fs_agent/1.gif)

FS Agent is an **AI-powered filesystem agent** with a Rich terminal UI, safe sandboxed file operations, and pluggable language models.  
It uses [pydantic-ai](https://github.com/pydantic/pydantic-ai) to expose a set of filesystem and calculator tools to an agent that can follow natural-language instructions.

---

## ✨ Features

- **Sandboxed filesystem**  
  All file/folder operations are restricted to a safe directory (`SANDBOX_DIR`).
- **Comprehensive tools**  
  - File/folder: list, read, write, append, copy, move, create, delete, rename  
  - Bulk operations: numeric sequences, regex renamer, glob delete  
  - Safe calculator for arithmetic expressions
- **Model backends**  
  - `local`: Ollama / OpenAI-compatible API  
  - `gemini`: Google Gemini models (optional, extra dependency)
- **Rich CLI experience**  
  - Interactive REPL with syntax-highlighted output  
  - `/model` command to switch engines or models on the fly  
  - Execution timing and contextual feedback

---

## 🚀 Quickstart

### 1. Clone & setup environment
```bash
git clone https://github.com/<your-user>/fs-agent.git
cd fs-agent

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Adjust `.env` for your preferred engine (Ollama or Gemini).

### 3. Run the agent
```bash
python -m fs_agent
```

You will see a Rich banner and an interactive prompt.

---

## ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable         | Description                                | Default                    |
|------------------|--------------------------------------------|----------------------------|
| `OLLAMA_BASE_URL` | Base URL for Ollama/OpenAI-compatible API  | `http://localhost:11434/v1` |
| `OLLAMA_MODEL`    | Default local model name                   | `qwen2.5:7b-instruct`      |
| `GOOGLE_API_KEY`  | API key for Gemini (optional)              | –                          |
| `GEMINI_MODEL`    | Default Gemini model                       | `gemini-1.5-flash`         |
| `SANDBOX_DIR`     | Root directory for all file operations     | `test_folder/`             |
| `LOGFIRE_CONSOLE` | Enable console logging via Logfire         | `false`                    |

---

## 🛠️ Available Tools

All tools operate **inside the sandbox directory** only.

### 🔢 Calculator

**`calculator(expression: str) -> float`**  
Evaluate an arithmetic expression safely.

- Example:
  ```
  › calculate (12 * 3.5) / 7
  6.0
  ```

---

### 📂 Directory Operations

**`list_dir(path=".", tree=True, max_depth=2) -> str`**  
List contents of a directory. Optionally show a tree view.

- Example:
  ```
  › list files in current folder
  test_folder/
  ├── notes.txt (1 KB)
  └── reports/
      └── report1.txt (2 KB)
  ```

---

### 📖 File Operations

**`read_file(path, max_bytes=200_000) -> str`**  
Read a text file (with byte-size safety limit).

- Example:
  ```
  › read file notes.txt
  This is my note content...
  ```

**`write_file(path, content) -> str`**  
Create or overwrite a file with given content.

- Example:
  ```
  › write file notes.txt with content "Hello World"
  ```

**`append_file(path, content) -> str`**  
Append content to an existing file.

- Example:
  ```
  › append "New line" to file notes.txt
  ```

**`copy_file(src, dst, overwrite=False) -> str`**  
Copy a file.

- Example:
  ```
  › copy notes.txt to backup.txt
  ```

**`move_file(src, dst, overwrite=False) -> str`**  
Move or rename a file/folder.

- Example:
  ```
  › rename notes.txt to archive.txt
  ```

**`create_file(path, content="") -> str`**  
Create a new file (optionally with content).

- Example:
  ```
  › create empty file todo.txt
  ```

**`delete_file(path) -> str`**  
Delete a single file.

- Example:
  ```
  › delete file old.txt
  ```

**`delete_glob(pattern) -> str`**  
Delete multiple files matching a glob pattern.

- Example:
  ```
  › delete all .log files in logs folder
  ```

---

### 📝 Bulk File Operations

**`create_files_sequence(prefix, suffix, start, end, zero_pad=0, content="") -> str`**  
Create many files in a numeric sequence.

- Example:
  ```
  › create files report_01.txt ... report_05.txt
  ```

**`rename_file(old_path, new_path) -> str`**  
Rename a single file.

- Example:
  ```
  › rename report1.txt to summary1.txt
  ```

**`rename_files_sequence(old_prefix, old_suffix, new_prefix, new_suffix, start, end, zero_pad=0) -> str`**  
Rename a numeric file series.

- Example:
  ```
  › rename files data01.csv...data10.csv to result01.csv...result10.csv
  ```

**`bulk_rename_regex(base_path, pattern, replacement, include_subdirs=True, test_only=False) -> str`**  
Rename multiple files by regex substitution.

- Example:
  ```
  › replace "draft" with "final" in all .txt files
  ```

---

### 📁 Folder Operations

**`create_folder(path, exist_ok=True) -> str`**  
Create a folder.

- Example:
  ```
  › create folder drafts
  ```

**`create_folders_sequence(prefix, suffix="", start=1, end=1, zero_pad=0) -> str`**  
Create multiple folders in a numeric range.

- Example:
  ```
  › create folders project01 ... project05
  ```

**`delete_folder(path, recursive=False) -> str`**  
Delete a folder. Use `recursive=True` for non-empty directories.

- Example:
  ```
  › delete folder drafts (recursive)
  ```

---

## 🧪 Testing

Install test dependencies and run the suite:

```bash
pip install pytest pytest-cov
pytest -v
```

Or with coverage:

```bash
pytest --cov=src/fs_agent --cov-report=term-missing -v
```

---

## 🤝 Contributing

Contributions are welcome!  
- Fork → Branch → Commit → Pull Request  
- Please include tests and documentation for new features.

---

## 📜 License

MIT License — see [LICENSE](LICENSE).

---
