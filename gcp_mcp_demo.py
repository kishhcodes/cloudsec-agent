#!/usr/bin/env python3
"""
GCP MCP Demo Script

This script demonstrates the capabilities of the GCP MCP module including:
- Natural language interpretation
- Security validation
- Risk assessment
- Command execution
"""

import os
import sys
import json
import logging

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.gcp_mcp import (
    GCPMCPClient,
    interpret_natural_language,
    validate_gcp_command,
)
from src.gcp_mcp.security import get_command_risk_level

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.panel import Panel
    console = Console()
except ImportError:
    console = None


def demo_natural_language_interpretation():
    """Demonstrate natural language interpretation."""
    print("\n" + "=" * 80)
    print("DEMO 1: Natural Language Interpretation")
    print("=" * 80)
    
    test_queries = [
        "list my instances",
        "show projects",
        "list sql databases",
        "list network security",
        "get firewalls",
        "list cloud functions",
    ]
    
    print("\nConverting natural language queries to gcloud commands:")
    print("-" * 80)
    
    if console:
        table = Table(title="Natural Language to CLI Command Mapping")
        table.add_column("Natural Language Query", style="cyan")
        table.add_column("gcloud Command", style="green")
        
        for query in test_queries:
            command = interpret_natural_language(query)
            if command:
                table.add_row(f"'{query}'", command)
            else:
                table.add_row(f"'{query}'", "[red]No mapping found[/red]")
        
        console.print(table)
    else:
        for query in test_queries:
            command = interpret_natural_language(query)
            if command:
                print(f"✓ '{query}' → {command}")
            else:
                print(f"✗ '{query}' → No mapping found")


def demo_security_validation():
    """Demonstrate security validation."""
    print("\n" + "=" * 80)
    print("DEMO 2: Security Validation")
    print("=" * 80)
    
    test_commands = [
        # Safe commands
        ("gcloud compute instances list", "safe"),
        ("gcloud projects list", "safe"),
        
        # Dangerous commands
        ("gcloud iam service-accounts create test", "dangerous"),
        ("gcloud projects delete", "dangerous"),
        ("gcloud secrets delete my-secret", "dangerous"),
    ]
    
    print("\nValidating command safety:")
    print("-" * 80)
    
    if console:
        table = Table(title="Command Security Validation")
        table.add_column("Command", style="cyan")
        table.add_column("Validation Result", style="yellow")
        
        for command, expected in test_commands:
            try:
                validate_gcp_command(command)
                result = "[green]✓ PASSED[/green]"
            except ValueError as e:
                result = f"[red]✗ BLOCKED[/red]\n{str(e)[:50]}..."
            
            table.add_row(command, result)
        
        console.print(table)
    else:
        for command, expected in test_commands:
            try:
                validate_gcp_command(command)
                print(f"✓ {command} - PASSED")
            except ValueError as e:
                print(f"✗ {command} - BLOCKED: {str(e)[:50]}...")


def demo_risk_assessment():
    """Demonstrate risk assessment."""
    print("\n" + "=" * 80)
    print("DEMO 3: Risk Assessment")
    print("=" * 80)
    
    test_commands = [
        "gcloud compute instances list",
        "gcloud compute instances update my-instance",
        "gcloud sql instances delete prod-db",
        "gcloud iam service-accounts create evil",
        "gcloud storage buckets create my-bucket",
    ]
    
    print("\nAssessing command risk levels:")
    print("-" * 80)
    
    if console:
        table = Table(title="Command Risk Assessment")
        table.add_column("Command", style="cyan")
        table.add_column("Risk Level", style="yellow")
        
        risk_colors = {
            "safe": "green",
            "low": "blue",
            "medium": "yellow",
            "high": "orange",
            "critical": "red",
        }
        
        for command in test_commands:
            risk = get_command_risk_level(command)
            color = risk_colors.get(risk, "white")
            table.add_row(command, f"[{color}]{risk.upper()}[/{color}]")
        
        console.print(table)
    else:
        for command in test_commands:
            risk = get_command_risk_level(command)
            print(f"{command}")
            print(f"  Risk Level: {risk.upper()}\n")


def demo_command_execution():
    """Demonstrate command execution."""
    print("\n" + "=" * 80)
    print("DEMO 4: Command Execution")
    print("=" * 80)
    
    print("\nInitializing GCP MCP Client...")
    
    client = GCPMCPClient()
    if not client.start():
        print("Failed to initialize client. Make sure gcloud CLI is installed.")
        print("Installation guide: https://cloud.google.com/sdk/docs/install")
        return
    
    print("✓ Client initialized successfully")
    
    # Get current project
    print("\nGetting current project...")
    project_info = client.get_current_project()
    if project_info:
        print(f"✓ Current project: {project_info.get('project_id')}")
    else:
        print("✗ No project configured. Run: gcloud config set project PROJECT_ID")
    
    # Try a safe read-only command
    print("\nExecuting safe command: 'gcloud config list'")
    result = client.execute_command("gcloud config list --format=json")
    
    if result["status"] == "success":
        print("✓ Command executed successfully")
        try:
            config = json.loads(result["output"])
            if console:
                console.print_json(json.dumps(config, indent=2))
            else:
                print(json.dumps(config, indent=2))
        except:
            print(result["output"][:500])
    else:
        print(f"✗ Command failed: {result['output'][:200]}")
    
    # Clean up
    client.stop()
    print("\n✓ Client stopped")


def demo_interactive_mode():
    """Demonstrate interactive mode."""
    print("\n" + "=" * 80)
    print("DEMO 5: Interactive Mode (Optional)")
    print("=" * 80)
    
    print("\nTo use the interactive shell, run:")
    print("  python -m src.gcp_mcp")
    print("\nExample commands in interactive mode:")
    print("  gcloud> list my instances")
    print("  gcloud> gcloud compute instances list")
    print("  gcloud> gcloud projects list")
    print("  gcloud> info")
    print("  gcloud> exit")


def main():
    """Run all demos."""
    if console:
        console.print(Panel.fit(
            "[bold cyan]GCP MCP Module Demo[/bold cyan]\n\nDemonstrating Model Context Protocol for gcloud CLI",
            border_style="blue"
        ))
    else:
        print("\n" + "=" * 80)
        print("GCP MCP Module Demo - Model Context Protocol for gcloud CLI")
        print("=" * 80)
    
    try:
        # Run demos
        demo_natural_language_interpretation()
        demo_security_validation()
        demo_risk_assessment()
        demo_command_execution()
        demo_interactive_mode()
        
        if console:
            console.print(Panel.fit(
                "[bold green]Demo Completed Successfully![/bold green]",
                border_style="green"
            ))
        else:
            print("\n" + "=" * 80)
            print("Demo Completed Successfully!")
            print("=" * 80)
            
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        if console:
            console.print(f"[red]Error during demo: {e}[/red]")
        else:
            print(f"Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
