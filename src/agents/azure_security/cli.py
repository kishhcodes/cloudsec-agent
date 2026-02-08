#!/usr/bin/env python3
"""
Azure Security Agent CLI

Interactive command-line interface for Azure security analysis and auditing.
"""

import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from .agent import AzureSecurityAgent

# Load environment variables
load_dotenv()

app = typer.Typer(help="Azure Security Agent CLI")
console = Console()


def display_welcome():
    """Display welcome message."""
    console.print(Panel(
        "[bold blue]Azure Security Agent[/bold blue]\n"
        "[dim]Powered by Gemini LLM and Azure APIs[/dim]",
        border_style="blue"
    ))
    console.print("[dim]Type [bold]help[/bold] to see available commands[/dim]")
    console.print("[dim]You can also use natural language like [italic]'Check my Entra ID security'[/italic][/dim]")
    console.print()


def display_help():
    """Display available commands."""
    table = Table(title="Available Commands")
    table.add_column("Command", style="green")
    table.add_column("Description")
    
    table.add_row("entra", "Analyze Entra ID security")
    table.add_row("storage", "Analyze Storage Account security")
    table.add_row("compute", "Analyze Virtual Machine security")
    table.add_row("database", "Analyze Database security")
    table.add_row("network", "Analyze Network security")
    table.add_row("audit", "Perform full Azure audit (generates PDF)")
    table.add_row("clear", "Clear the screen")
    table.add_row("help", "Show this help message")
    table.add_row("exit", "Exit the application")
    table.add_row("[natural language]", "Ask anything in natural language")
    
    console.print(table)
    console.print()
    console.print("[bold cyan]Natural Language Examples:[/bold cyan]")
    console.print("  • 'Check my Entra ID security'")
    console.print("  • 'Review storage account settings'")
    console.print("  • 'Audit virtual machine configuration'")
    console.print("  • 'Check network security groups'")
    console.print()


def main():
    """Main CLI entry point."""
    # Get subscription ID from environment
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    
    if not subscription_id:
        console.print("[yellow]⚠️  Warning: AZURE_SUBSCRIPTION_ID not set[/yellow]")
        subscription_id = Prompt.ask("Enter your Azure Subscription ID (or press Enter to continue)")
    
    # Create the agent
    try:
        agent = AzureSecurityAgent(subscription_id=subscription_id)
    except Exception as e:
        console.print(f"[red]Error initializing Azure Security Agent: {str(e)}[/red]")
        return
    
    display_welcome()
    
    # Main command loop
    try:
        while True:
            # Get command
            command = Prompt.ask("[bold blue]Azure Security>[/bold blue]")
            
            if command.lower() in ["exit", "quit"]:
                break
            elif command.lower() in ["help", "?"]:
                display_help()
            elif command.lower() in ["clear", "cls"]:
                console.clear()
                display_welcome()
            elif command.lower() == "entra":
                result = agent.analyze_entra_id_security()
                console.print(result)
            elif command.lower() == "storage":
                result = agent.analyze_storage_security()
                console.print(result)
            elif command.lower() == "compute":
                result = agent.analyze_compute_security()
                console.print(result)
            elif command.lower() == "database":
                result = agent.analyze_database_security()
                console.print(result)
            elif command.lower() == "network":
                result = agent.analyze_network_security()
                console.print(result)
            elif command.lower() == "audit":
                with console.status("Running full Azure audit..."):
                    audit_result = agent.perform_full_audit(export_pdf=True)
                console.print()
                console.print(Panel(
                    f"[green]✓ Audit Complete![/green]\n"
                    f"Subscription: {audit_result['subscription_id']}\n"
                    f"PDF Report: {audit_result['pdf_path']}",
                    border_style="green"
                ))
            else:
                # Process as natural language
                with console.status("Analyzing your query..."):
                    result = agent.process_command(command)
                console.print(result)
            
            console.print()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def run(
    subscription_id: Optional[str] = typer.Option(
        None,
        "--subscription",
        "-s",
        help="Azure subscription ID"
    )
):
    """Run the Azure Security Agent CLI."""
    if subscription_id:
        os.environ["AZURE_SUBSCRIPTION_ID"] = subscription_id
    
    main()


if __name__ == "__main__":
    app()
