#!/usr/bin/env python3
"""
Azure MCP Demo Script

Demonstrates the capabilities of the Azure MCP module.
"""

import os
import sys
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from src.azure_mcp.client import AzureMCPClient
from src.azure_mcp.tools import interpret_natural_language
from src.azure_mcp.security import get_command_risk_level
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def main():
    """Run Azure MCP demo"""
    
    console.print("\n" + "="*70)
    console.print("[bold cyan]AZURE MCP - MODEL CONTEXT PROTOCOL DEMO[/bold cyan]")
    console.print("="*70)
    
    # Initialize client
    console.print("\n[yellow]Initializing Azure MCP Client...[/yellow]")
    client = AzureMCPClient()
    
    if not client.start():
        console.print("[red]❌ Failed to start client[/red]")
        return
    
    console.print("[green]✅ Client initialized[/green]")
    
    # Demo 1: Natural Language Interpretation
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 1: Natural Language Interpretation[/bold cyan]")
    console.print("="*70)
    
    nl_queries = [
        ("who am i", "Show current identity"),
        ("list subscriptions", "List all subscriptions"),
        ("list resource groups", "List resource groups"),
        ("list vms", "List virtual machines"),
        ("list storage accounts", "List storage accounts"),
    ]
    
    table = Table(title="Natural Language → Azure CLI Commands")
    table.add_column("Query", style="cyan")
    table.add_column("Mapped Command", style="green")
    
    for query, _ in nl_queries:
        cmd = interpret_natural_language(query)
        table.add_row(query, cmd or "(no mapping)")
    
    console.print(table)
    
    # Demo 2: Security Risk Analysis
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 2: Security Risk Level Analysis[/bold cyan]")
    console.print("="*70)
    
    test_commands = [
        ("az account show", "Safe - read account info"),
        ("az vm list", "Safe - list VMs"),
        ("az ad user create", "CRITICAL - create user"),
        ("az role assignment create", "CRITICAL - assign role"),
        ("az keyvault secret delete", "HIGH - delete secret"),
    ]
    
    table = Table(title="Command Risk Analysis")
    table.add_column("Command", style="cyan")
    table.add_column("Risk Level", style="yellow")
    table.add_column("Description", style="white")
    
    for cmd, desc in test_commands:
        risk = get_command_risk_level(cmd)
        
        # Color code risk level
        if risk == "safe":
            risk_display = f"[green]{risk}[/green]"
        elif risk in ["low", "medium"]:
            risk_display = f"[yellow]{risk}[/yellow]"
        else:
            risk_display = f"[red]{risk}[/red]"
        
        table.add_row(cmd, risk_display, desc)
    
    console.print(table)
    
    # Demo 3: Command Execution
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 3: Command Execution[/bold cyan]")
    console.print("="*70)
    
    demo_commands = [
        ("az account show", "Get current subscription info"),
        ("az group list --query \"[0]\" -o json", "List first resource group"),
    ]
    
    for cmd, description in demo_commands:
        console.print(f"\n[bold yellow]Command:[/bold yellow] {description}")
        console.print(f"[dim]{cmd}[/dim]")
        console.print("\n[cyan]Executing...[/cyan]")
        
        result = client.execute_command(cmd)
        
        if result["status"] == "success":
            console.print("[green]✅ Success[/green]")
            output = result.get("output", "")
            if output:
                # Truncate long output
                if len(output) > 500:
                    output = output[:500] + "\n... (output truncated)"
                console.print(f"\n[dim]{output}[/dim]")
        else:
            console.print(f"[red]❌ Error: {result.get('output', 'Unknown error')}[/red]")
    
    # Demo 4: Interactive Shell
    console.print("\n" + "="*70)
    console.print("[bold cyan]Demo 4: Interactive Mode[/bold cyan]")
    console.print("="*70)
    
    console.print("\nEnter Azure MCP Interactive Mode")
    console.print("Commands:")
    console.print("  • Direct: 'az account show'")
    console.print("  • Natural: 'list my subscriptions'")
    console.print("  • Type 'info' for subscription info")
    console.print("  • Type 'help' for help")
    console.print("  • Type 'exit' to quit")
    
    interactive_mode(client)
    
    # Cleanup
    client.stop()
    console.print("\n[green]✅ Demo complete![/green]")


def interactive_mode(client: AzureMCPClient):
    """Run interactive mode"""
    while True:
        try:
            cmd = input("\naz-mcp> ").strip()
            
            if cmd.lower() in ["exit", "quit"]:
                break
            elif cmd.lower() == "help":
                print("Azure MCP Interactive Shell")
                print("  • az account show - Get current account")
                print("  • az group list - List resource groups")
                print("  • list vms - Natural language for VMs")
                print("  • info - Show current subscription")
                print("  • exit - Exit shell")
                continue
            elif cmd.lower() == "info":
                info = client.get_current_subscription()
                if info:
                    print(f"Subscription: {info.get('name')}")
                    print(f"ID: {info.get('id')}")
                else:
                    print("Error getting subscription info")
                continue
            elif not cmd:
                continue
            
            result = client.execute_command(cmd)
            if result["status"] == "success":
                print(result.get("output", ""))
            else:
                print(f"Error: {result.get('output', 'Unknown error')}")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
