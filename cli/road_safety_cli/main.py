"""Main CLI entry point."""
import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from .commands import search, interactive, config

app = typer.Typer(
    name="road-safety",
    help="Road Safety Intervention AI - CLI Tool",
    add_completion=False,
)

console = Console()

# Add commands
app.add_typer(search.app, name="search")
app.add_typer(interactive.app, name="interactive")
app.add_typer(config.app, name="config")


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(
        Panel(
            f"[bold cyan]Road Safety Intervention AI[/bold cyan]\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Powered by Google Gemini",
            title="🚦 Road Safety CLI",
            border_style="cyan",
        )
    )


@app.callback()
def main():
    """Road Safety Intervention AI - CLI Tool."""
    pass


if __name__ == "__main__":
    app()
