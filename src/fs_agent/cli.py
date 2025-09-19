from __future__ import annotations
import time
from rich.prompt import Prompt
from rich.panel import Panel

from .config import Config
from .engines import EngineFactory
from .services.filesystem import FileSandbox
from .services.calculator import CalculatorService
from .agent import AgentFactory
from .ui import console, banner, ai_panel

class FSAgentApp:
    """Text UI runner."""

    def __init__(self, cfg: Config | None = None):
        self.cfg = cfg or Config.load()
        self.sandbox = FileSandbox(self.cfg.sandbox_dir)
        self.calc = CalculatorService()
        self.engine = "local"
        self.model_name = self.cfg.ollama_model
        self.model, self.provider_label = EngineFactory.build(self.engine, self.model_name, self.cfg)
        self.agent = AgentFactory.build(self.model, self.sandbox, self.calc)

    def get_files_list(self) -> str:
        self.sandbox.ensure()
        import os
        names = sorted(os.listdir(self.sandbox.root))
        return "\n".join(names) if names else "(empty)"

    def switch_model(self, engine: str, model_name: str | None) -> None:
        new_model_name = model_name or (self.cfg.ollama_model if engine == "local" else self.cfg.gemini_model)
        self.model, self.provider_label = EngineFactory.build(engine, new_model_name, self.cfg)
        self.agent = AgentFactory.build(self.model, self.sandbox, self.calc)
        self.engine = engine
        self.model_name = new_model_name
        console.print(
            Panel.fit(
                f"Engine switched to [bold]{self.engine}[/bold]\n"
                f"Model: [bold]{self.model_name}[/bold]\n"
                f"Provider: {self.provider_label}",
                title="[ai]Model switched[/ai]", border_style="ok",
            )
        )

    def run(self) -> None:
        self.sandbox.ensure()
        banner(self.engine, self.model_name, self.provider_label)
        console.print("[muted]Type 'exit' or 'q' to quit.[/muted]\n")

        while True:
            try:
                user_input = Prompt.ask("[brand]›[/brand]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[muted]Bye.[/muted]")
                break

            user_input = (user_input or "").strip()
            if not user_input:
                continue
            if user_input in {"exit", "q"}:
                break

            # Commands
            if user_input.startswith("/model"):
                parts = user_input.split()
                if len(parts) < 2 or parts[1] not in {"local", "gemini"}:
                    console.print("[warn]Usage:[/warn] /model local [MODEL]  or  /model gemini [MODEL]\n")
                    continue
                new_engine = parts[1]
                maybe_name = " ".join(parts[2:]).strip() if len(parts) > 2 else None
                try:
                    self.switch_model(new_engine, maybe_name)
                except Exception as e:
                    console.print(f"[err]Failed to switch model:[/err] {e}\n")
                continue

            # Normal prompt
            prompt = f"{user_input}\n\nCurrent files in directory:\n{self.get_files_list()}"
            started = time.perf_counter()
            try:
                with console.status("[brand]thinking…[/brand]", spinner="dots"):
                    response = self.agent.run_sync(prompt)
            except Exception as e:
                console.print(f"[err]Error:[/err] {e}\n")
                continue

            ai_panel(response.output)
            console.print(
                f"[muted]{self.engine} · {self.model_name} · done in {time.perf_counter()-started:.2f}s[/muted]\n"
            )
