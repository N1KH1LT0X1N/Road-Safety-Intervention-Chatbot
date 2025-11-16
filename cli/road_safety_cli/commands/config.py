"""Configuration command."""
import typer
from rich.console import Console
from rich.table import Table
from ..utils.config_manager import ConfigManager

app = typer.Typer(help="Manage configuration")
console = Console()


@app.command()
def set(key: str = typer.Argument(..., help="Config key"), value: str = typer.Argument(..., help="Config value")):
    """Set configuration value."""
    config = ConfigManager()
    config.set(key, value)
    console.print(f"[green]✅ Set {key} = {value}[/green]")


@app.command()
def get(key: str = typer.Argument(..., help="Config key")):
    """Get configuration value."""
    config = ConfigManager()
    value = config.get(key)

    if value:
        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")
    else:
        console.print(f"[yellow]Config key '{key}' not found[/yellow]")


@app.command()
def show():
    """Show all configuration."""
    config = ConfigManager()
    settings = config.get_all()

    if settings:
        table = Table(title="Configuration", show_header=True)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for key, value in settings.items():
            # Mask API key
            if "key" in key.lower() and value:
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value

            table.add_row(key, display_value)

        console.print(table)
    else:
        console.print("[yellow]No configuration found[/yellow]")


@app.command()
def clear():
    """Clear all configuration."""
    config = ConfigManager()

    if typer.confirm("Are you sure you want to clear all configuration?"):
        config.clear()
        console.print("[green]✅ Configuration cleared[/green]")
    else:
        console.print("[yellow]Cancelled[/yellow]")


if __name__ == "__main__":
    app()
