"""Interactive mode command."""
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from ..utils.api_client import get_api_client
from ..utils.formatters import format_result, format_confidence

app = typer.Typer(help="Interactive mode")
console = Console()


@app.command()
def start():
    """Start interactive mode."""
    console.print(
        Panel(
            "[bold cyan]Road Safety Intervention AI[/bold cyan]\n"
            "Interactive Mode\n\n"
            "Type your query or 'quit' to exit",
            title="🚦 Interactive Search",
            border_style="cyan",
        )
    )

    client = get_api_client()

    while True:
        console.print()
        query = Prompt.ask("[bold green]Enter your query[/bold green]")

        if query.lower() in ["quit", "exit", "q"]:
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break

        if not query.strip():
            continue

        try:
            with console.status("[bold green]Searching..."):
                response = client.search(query=query, max_results=3)

            results = response["results"]
            metadata = response["metadata"]

            console.print(
                f"\n[green]✅ Found {metadata['total_results']} results in {metadata['query_time_ms']}ms[/green]\n"
            )

            if results:
                for idx, result in enumerate(results, 1):
                    console.print(
                        Panel(
                            f"[bold]{result['title']}[/bold]\n\n"
                            f"Confidence: {format_confidence(result['confidence'])}\n"
                            f"Category: {result['category']}\n"
                            f"Problem: {result['problem']}\n"
                            f"IRC: {result['irc_reference']['code']} {result['irc_reference']['clause']}\n"
                            f"Cost: {result['cost_estimate']}",
                            title=f"Result #{idx}",
                            border_style="cyan",
                        )
                    )

                # Show synthesis
                if response.get("synthesis"):
                    console.print("\n[bold cyan]💬 AI Analysis:[/bold cyan]")
                    # Show first 500 chars
                    synthesis_preview = response["synthesis"][:500]
                    if len(response["synthesis"]) > 500:
                        synthesis_preview += "..."
                    console.print(Markdown(synthesis_preview))

            else:
                console.print("[yellow]No results found. Try rephrasing your query.[/yellow]")

        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")


if __name__ == "__main__":
    app()
