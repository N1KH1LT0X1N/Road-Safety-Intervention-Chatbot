"""Search command."""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Optional, List
import json
from ..utils.api_client import get_api_client
from ..utils.formatters import format_result, format_confidence

app = typer.Typer(help="Search for interventions")
console = Console()


@app.command()
def query(
    query_text: str = typer.Argument(..., help="Search query"),
    category: Optional[List[str]] = typer.Option(None, "--category", "-c", help="Filter by category"),
    problem: Optional[List[str]] = typer.Option(None, "--problem", "-p", help="Filter by problem type"),
    speed_min: Optional[int] = typer.Option(None, "--speed-min", help="Minimum speed (km/h)"),
    speed_max: Optional[int] = typer.Option(None, "--speed-max", help="Maximum speed (km/h)"),
    strategy: str = typer.Option("auto", "--strategy", "-s", help="Search strategy"),
    max_results: int = typer.Option(5, "--max-results", "-n", help="Maximum results"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, markdown"),
):
    """Search for road safety interventions."""
    try:
        client = get_api_client()

        with console.status("[bold green]Searching..."):
            response = client.search(
                query=query_text,
                category=category,
                problem=problem,
                speed_min=speed_min,
                speed_max=speed_max,
                strategy=strategy,
                max_results=max_results,
            )

        if output_format == "json":
            console.print_json(data=response)
            return

        # Display results
        results = response["results"]
        metadata = response["metadata"]

        console.print(
            f"\n[green]✅ Found {metadata['total_results']} results in {metadata['query_time_ms']}ms[/green]\n"
        )

        if not results:
            console.print("[yellow]No interventions found. Try adjusting your query.[/yellow]")
            return

        if output_format == "markdown":
            for idx, result in enumerate(results, 1):
                console.print(Markdown(format_result(result, idx)))
                console.print("---\n")

        else:  # table format
            for idx, result in enumerate(results, 1):
                table = Table(title=f"{idx}. {result['title']}", show_header=False, border_style="cyan")

                table.add_row("Confidence", format_confidence(result["confidence"]))
                table.add_row("Category", result["category"])
                table.add_row("Problem", result["problem"])
                table.add_row("Type", result["type"])
                table.add_row("IRC Reference", f"{result['irc_reference']['code']} {result['irc_reference']['clause']}")
                table.add_row("Cost Estimate", result["cost_estimate"])

                console.print(table)
                console.print()

        # Show synthesis
        if response.get("synthesis"):
            console.print("\n[bold cyan]💬 AI Analysis:[/bold cyan]")
            console.print(Panel(Markdown(response["synthesis"]), border_style="cyan"))

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
