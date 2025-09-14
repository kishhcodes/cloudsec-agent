# src/agents/compliance_bot/cli.py
import os
import sys
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from dotenv import load_dotenv

from .agent import CloudComplianceAgent

# Load environment variables
load_dotenv()

# Initialize Rich components
console = Console()
app = typer.Typer()

def display_welcome():
    """Display a welcome message when the CLI starts."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Cloud Security Compliance Assistant[/bold blue]\n"
        "[dim]Your AI-powered guide to cloud security compliance[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()
    console.print("[dim]Type your questions about cloud security compliance, CIS benchmarks, and best practices.[/dim]")
    console.print("[dim]You can also ask about specific articles, like:[/dim]")
    console.print("[dim]- \"Find articles by Jane Doe about S3 security\"[/dim]")
    console.print("[dim]- \"What did John Smith write about cloud compliance?\"[/dim]")
    console.print()
    console.print("[dim]Commands:[/dim]")
    console.print("[dim]- Type [bold]'clear'[/bold] or [bold]'cls'[/bold] to clear the screen[/dim]")
    console.print("[dim]- Type [bold]'exit'[/bold] or [bold]'quit'[/bold] to end the session[/dim]")
    console.print()

def display_article_results(result):
    """Display article search results in a nicely formatted way."""
    # Display the main response
    console.print(Panel(
        Markdown(result["response"]),
        title="[bold blue]Article Search Results[/bold blue]",
        border_style="blue",
        expand=False
    ))
    
    # Display found articles
    if result.get("search_results"):
        console.print("\n[bold]Found articles:[/bold]")
        
        for i, article in enumerate(result["search_results"], 1):
            console.print(Panel(
                f"[bold cyan]{article.get('title', 'Untitled')}[/bold cyan]\n\n"
                f"{article.get('snippet', 'No snippet available')}\n\n"
                f"[dim]Source: {article.get('source', 'Unknown')}  "
                f"{('Date: ' + article['date']) if article.get('date') else ''}[/dim]\n"
                f"[link={article.get('link', '#')}]{article.get('link', 'No link available')}[/link]",
                title=f"Article {i}",
                border_style="cyan",
                expand=False
            ))

def display_response(result):
    """Display the response in a nicely formatted way."""
    # Check if this is an article search result
    if result.get("is_article_search", False):
        display_article_results(result)
        return
        
    # Display the main compliance response
    console.print(Panel(
        Markdown(result["response"]),
        title="[bold green]Response[/bold green]",
        border_style="green",
        expand=False
    ))
    
    # Option to show sources
    if console.width > 100:  # Only offer detailed view on wider terminals
        show_details = Prompt.ask("\n[dim]Show retrieved sources?[/dim]", choices=["y", "n"], default="n")
        
        if show_details.lower() == "y":
            # Display retrieved documents
            docs_table = Table(title="Retrieved Documents", box=box.ROUNDED)
            docs_table.add_column("Source", style="cyan", no_wrap=True)
            docs_table.add_column("Relevance", style="magenta")
            docs_table.add_column("Content", style="green")
            
            for doc in result["retrieved_docs"][:3]:  # Show top 3 docs
                source = doc.get("metadata", {}).get("source", "Unknown")
                score = doc.get("score", "N/A")
                score_str = f"{score:.2f}" if isinstance(score, float) else str(score)
                content = doc.get("content", "")
                # Truncate content if too long
                content = content[:200] + "..." if len(content) > 200 else content
                docs_table.add_row(source, score_str, content)
            
            console.print(docs_table)
            
            # Display search results if available
            if result.get("search_results"):
                search_table = Table(title="Search Results", box=box.ROUNDED)
                search_table.add_column("Title", style="cyan")
                search_table.add_column("Snippet", style="green")
                
                for item in result["search_results"][:2]:  # Show top 2 search results
                    title = item.get("title", "N/A")
                    snippet = item.get("snippet", "N/A")
                    search_table.add_row(title, snippet)
                
                console.print(search_table)

def clear_screen():
    """Clear the terminal screen."""
    # Clear screen - works for both Windows and Unix/Linux
    if os.name == "nt":  # For Windows
        os.system("cls")
    else:  # For Unix/Linux/MacOS
        os.system("clear")

def interactive_mode(agent: CloudComplianceAgent):
    """Run the interactive CLI mode."""
    display_welcome()
    
    while True:
        # Get user query
        query = Prompt.ask("\n[bold green]You[/bold green]")
        
        # Exit conditions
        if query.lower() in ["exit", "quit", "q", "bye"]:
            console.print("[yellow]Goodbye! Have a secure day![/yellow]")
            sys.exit(0)
            
        # Clear screen command
        if query.lower() in ["clear", "cls"]:
            clear_screen()
            display_welcome()
            continue
        
        # Skip empty queries
        if not query.strip():
            continue
            
        # Show processing indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Processing your question...[/bold blue]"),
            transient=True,
        ) as progress:
            progress.add_task("Processing...", total=None)
            
            # Process the query
            result = agent.process_query(query)
        
        # Display the response
        display_response(result)

@app.command()
def chat(
    embeddings_path: str = typer.Option(
        "data/embeddings/index",
        "--embeddings-path", "-e",
        help="Path to the embeddings index"
    ),
    use_search: bool = typer.Option(
        True,
        "--use-search/--no-search",
        help="Whether to use SERPAPI for cross-verification"
    ),
    serpapi_key: Optional[str] = typer.Option(
        None, 
        "--serpapi-key", 
        help="SERPAPI API key (overrides environment variable)"
    ),
    google_api_key: Optional[str] = typer.Option(
        None, 
        "--google-api-key", 
        help="Google API key (overrides environment variable)"
    )
):
    """Interactive Cloud Security Compliance Assistant CLI."""
    try:
        # Initialize agent
        agent = CloudComplianceAgent(
            embeddings_path=embeddings_path,
            serpapi_key=serpapi_key or os.getenv("SERPAPI_API_KEY"),
            google_api_key=google_api_key or os.getenv("GOOGLE_API_KEY"),
            use_search=use_search
        )
        
        # Start interactive mode
        interactive_mode(agent)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    app()
