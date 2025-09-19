import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logfire

class Config(BaseModel):
    """Application configuration loaded from environment."""
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct"))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    google_api_key: str | None = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    sandbox_dir: Path = Field(default_factory=lambda: Path(os.getenv("SANDBOX_DIR", "test_folder")))
    logfire_console: bool = Field(default_factory=lambda: os.getenv("LOGFIRE_CONSOLE", "false").lower() == "true")

    @classmethod
    def load(cls) -> "Config":
        load_dotenv()
        # basic logfire config
        os.environ.setdefault("LOGFIRE_CONSOLE", "false")
        logfire.configure(send_to_logfire="if-token-present")
        logfire.instrument_pydantic_ai()
        return cls()

