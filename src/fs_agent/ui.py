from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

THEME = Theme(
    {
        "brand": "bold bright_cyan",
        "muted": "grey62",
        "ok": "bold green",
        "warn": "bold yellow",
        "err": "bold red",
        "ai": "bold cyan",
    }
)

console = Console(theme=THEME)

def banner(engine: str, model_name: str, provider_label: str) -> None:
    console.print(Rule(style="brand"))
    console.print(
        f"[brand]FILESYSTEM AGENT[/brand]  "
        f"[muted]— Engine:[/] {engine}   "
        f"[muted]Model:[/] {model_name}   "
        f"[muted]Provider:[/] {provider_label}"
    )
    console.print(
        "[muted]Switch engine any time: type [bold]/model gemini[/bold] "
        "or [bold]/model local[/bold]. You can also set a model, e.g. "
        "[/muted][bold]/model local llama3.2:3b[/bold][muted].[/muted]"
    )
    console.print(Rule(style="brand"))

def ai_panel(text: str) -> None:
    console.print(Panel.fit(Markdown(text), title="[ai]Assistant[/ai]", border_style="brand"))
