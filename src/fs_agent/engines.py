from __future__ import annotations
from typing import Tuple

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Config
from .ui import console

class EngineFactory:
    """Builds model backends for Agent."""

    @staticmethod
    def build(engine: str, model_name: str | None, cfg: Config) -> Tuple[object, str]:
        """
        Returns (model_instance, display_provider_label).
        engine in {'local', 'gemini'}.
        """
        if engine == "gemini":
            try:
                from pydantic_ai.models.google import GoogleModel
                from pydantic_ai.providers.google import GoogleProvider
            except Exception:
                console.print(
                    "[err]Gemini provider not installed.[/err] "
                    "Install with: [bold]pip install \"pydantic-ai-slim[google]\"[/bold]\n"
                )
                raise

            if not cfg.google_api_key:
                console.print(
                    "[err]Missing GOOGLE_API_KEY (or GEMINI_API_KEY).[/err] "
                    "Create one in Google AI Studio and export it.\n"
                )
                raise RuntimeError("Missing Google API key")

            provider = GoogleProvider(api_key=cfg.google_api_key)
            model = GoogleModel(model_name or cfg.gemini_model, provider=provider)
            return model, "Google AI (Gemini)"

        # default: local (Ollama/OpenAI-compatible)
        provider = OpenAIProvider(base_url=cfg.ollama_base_url, api_key="ollama")
        model = OpenAIChatModel(model_name or cfg.ollama_model, provider=provider)
        return model, f"Ollama @ {cfg.ollama_base_url}"
