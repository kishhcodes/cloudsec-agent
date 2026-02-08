#!/usr/bin/env python3
"""
Azure Security Agent Demo
Shows what the agent can analyze and recommend
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from src.agents.azure_security.agent import AzureSecurityAgent
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    """Run Azure agent demo"""
    
    # Initialize agent
    agent = AzureSecurityAgent()
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]AZURE SECURITY AGENT - INTERACTIVE DEMO[/bold cyan]")
    console.print("="*70)
    
    # Demo queries
    queries = [
        "Check my Entra ID security",
        "Review storage account settings",
        "Analyze VM security configuration",
        "Check SQL database security",
        "Review network security"
    ]
    
    console.print("\n[bold yellow]Available Demo Queries:[/bold yellow]")
    for i, query in enumerate(queries, 1):
        console.print(f"  {i}. {query}")
    
    console.print("\n[bold yellow]Full Audit:[/bold yellow]")
    console.print("  0. Perform a complete security audit (generates PDF report)")
    
    console.print("\n[bold yellow]Other Options:[/bold yellow]")
    console.print("  q. Quit")
    console.print("  c. Custom query")
    
    while True:
        try:
            choice = console.input("\n[bold green]Select option[/bold green] (0-5, q, c): ").strip().lower()
            
            if choice == 'q':
                console.print("[yellow]Exiting...[/yellow]")
                break
            
            elif choice == 'c':
                custom_query = console.input("[bold green]Enter your question[/bold green]: ").strip()
                if custom_query:
                    console.print("\n[cyan]Processing your query...[/cyan]\n")
                    response = agent.process_command(custom_query)
                    console.print(response)
            
            elif choice == '0':
                console.print("\n[cyan]Performing full audit (this may take a moment)...[/cyan]\n")
                try:
                    result = agent.perform_full_audit(export_pdf=True)
                    pdf_path = result.get('pdf_path', 'reports/audit.pdf')
                    console.print(f"\n[green]✅ Audit complete![/green]")
                    console.print(f"[cyan]Report saved to: {pdf_path}[/cyan]")
                except Exception as e:
                    console.print(f"[red]❌ Audit error: {e}[/red]")
            
            elif choice in ['1', '2', '3', '4', '5']:
                idx = int(choice) - 1
                if idx < len(queries):
                    query = queries[idx]
                    console.print(f"\n[cyan]Query: {query}[/cyan]\n")
                    response = agent.process_command(query)
                    console.print(response)
                else:
                    console.print("[red]Invalid selection[/red]")
            
            else:
                console.print("[red]Invalid option. Please try again.[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()
