#!/usr/bin/env python3
"""
AWS MCP Test Script

This script tests the AWS MCP implementation by executing various commands
and verifying the output.
"""

import json
import sys
import time
import os
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.aws_mcp.client import AWSMCPClient

# Initialize console for rich output
console = Console()

def test_command(client, command, expected_status="success"):
    """
    Test an AWS command and print the result.
    
    Args:
        client: AWSMCPClient instance
        command: Command to execute
        expected_status: Expected status (success or error)
    """
    console.print(f"[bold blue]Testing command:[/bold blue] [yellow]{command}[/yellow]")
    
    start_time = time.time()
    result = client.execute_command(command)
    elapsed_time = time.time() - start_time
    
    status_color = "green" if result["status"] == expected_status else "red"
    
    console.print(f"[bold blue]Status:[/bold blue] [{status_color}]{result['status']}[/{status_color}]")
    console.print(f"[bold blue]Time:[/bold blue] {elapsed_time:.2f}s")
    
    if isinstance(result["output"], (dict, list)):
        # Format JSON output
        console.print(Panel(
            json.dumps(result["output"], indent=2),
            title="Output",
            border_style=status_color
        ))
    else:
        # Format text output
        console.print(Panel(
            str(result["output"]),
            title="Output",
            border_style=status_color
        ))
    
    console.print("\n" + "-" * 80 + "\n")
    return result


def main():
    """Run the test script."""
    # Initialize client
    client = AWSMCPClient()
    
    # Start the client
    console.print(Panel(
        "[bold]AWS MCP Test Script[/bold]\n"
        "This script will test various AWS MCP commands",
        border_style="blue"
    ))
    
    with console.status("Initializing AWS MCP Client..."):
        if not client.start():
            console.print("[red]Error: Failed to initialize AWS MCP Client[/red]")
            return
    
    try:
        # Test 1: Get caller identity (direct AWS command)
        test_command(client, "aws sts get-caller-identity")
        
        # Test 2: Natural language command
        test_command(client, "who am i")
        
        # Test 3: List S3 buckets
        test_command(client, "aws s3api list-buckets")
        
        # Test 4: Another natural language command
        test_command(client, "show me my buckets")
        
        # Test 5: Invalid command (should return error)
        test_command(client, "aws invalidservice list-things", expected_status="error")
        
        # Test 6: Dangerous command (should be blocked)
        test_command(client, "aws iam create-user --user-name test-user", expected_status="error")
        
        # Test 7: Pipe command
        test_command(client, "aws ec2 describe-regions --query 'Regions[].RegionName' --output text | sort")
        
    finally:
        # Stop the client
        console.print("Stopping AWS MCP Client...")
        client.stop()
        console.print("[green]Done![/green]")


if __name__ == "__main__":
    main()
