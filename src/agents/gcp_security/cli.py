#!/usr/bin/env python3
"""
Google Cloud Platform Security Agent CLI

Interactive CLI for GCP security analysis and recommendations.
"""

import os
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from dotenv import load_dotenv

from .agent import GCPSecurityAgent

# Load environment variables
load_dotenv()

console = Console()


def display_welcome():
    """Display welcome message."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Google Cloud Platform Security Agent[/bold blue]\n"
        "[dim]Interactive security analysis for GCP resources[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()
    console.print("[dim]Example queries:[/dim]")
    console.print("[dim]- \"Check my IAM security\"[/dim]")
    console.print("[dim]- \"Analyze my Cloud Storage buckets\"[/dim]")
    console.print("[dim]- \"Review Compute Engine security\"[/dim]")
    console.print("[dim]- \"Check network security\"[/dim]")
    console.print()
    console.print("[dim]Commands:[/dim]")
    console.print("[dim]- Type [bold]'clear'[/bold] or [bold]'cls'[/bold] to clear the screen[/dim]")
    console.print("[dim]- Type [bold]'help'[/bold] to show more commands[/dim]")
    console.print("[dim]- Type [bold]'exit'[/bold] or [bold]'quit'[/bold] to end the session[/dim]")
    console.print()


def display_help():
    """Display help information."""
    help_text = """
# GCP Security Agent Commands

## Security Analysis
- `iam` or `check iam` - Analyze IAM configuration
- `storage` or `check buckets` - Analyze Cloud Storage security
- `compute` or `check instances` - Analyze Compute Engine security
- `sql` or `check database` - Analyze Cloud SQL security
- `network` or `check vpc` - Analyze VPC and firewall security

## General Commands
- `help` - Show this help message
- `clear` or `cls` - Clear the screen
- `exit` or `quit` - Exit the application

## Example Queries
- "What are the security issues in my IAM configuration?"
- "Check my Cloud Storage buckets for encryption"
- "List all Compute Engine instances with public IPs"
- "Analyze my VPC network security"
"""
    console.print(Markdown(help_text))


def clear_screen():
    """Clear the terminal screen."""
    if os.name == "nt":  # For Windows
        os.system("cls")
    else:  # For Unix/Linux/MacOS
        os.system("clear")


def main():
    """Main entry point for GCP Security Agent CLI."""
    try:
        # Initialize agent
        agent = GCPSecurityAgent()
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("\n[yellow]Setup Instructions:[/yellow]")
        console.print("1. Set your GCP project ID: export GOOGLE_CLOUD_PROJECT=your-project-id")
        console.print("2. Authenticate with GCP: gcloud auth application-default login")
        console.print("3. Set your Google API key: export GOOGLE_API_KEY=your-api-key")
        sys.exit(1)
    
    display_welcome()
    
    while True:
        try:
            # Get user query
            query = Prompt.ask("\n[bold green]GCP Security[/bold green]")
            
            # Exit conditions
            if query.lower() in ["exit", "quit", "q", "bye"]:
                console.print("[yellow]Goodbye! Keep your GCP resources secure![/yellow]")
                sys.exit(0)
            
            # Clear screen command
            if query.lower() in ["clear", "cls"]:
                clear_screen()
                display_welcome()
                continue
            
            # Help command
            if query.lower() in ["help", "h", "?"]:
                display_help()
                continue
            
            # Skip empty queries
            if not query.strip():
                continue
            
            # Process the query
            console.print()
            result = agent.process_command(query)
            console.print(result)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            console.print("[dim]Please try again or type 'help' for assistance[/dim]")


if __name__ == "__main__":
    main()
