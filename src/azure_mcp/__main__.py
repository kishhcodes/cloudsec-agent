#!/usr/bin/env python3
"""
Azure MCP Main Module

This module provides a command-line interface for the Azure MCP server.
It allows executing Azure CLI commands directly or through an interactive shell.
"""

import argparse
import logging
import os
import sys

from .client import AzureMCPClient
from .tools import interpret_natural_language

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("azure-mcp")


def main():
    """Main entry point for the Azure MCP CLI."""
    parser = argparse.ArgumentParser(description="Azure MCP - Model Context Protocol for Azure CLI")
    parser.add_argument("--subscription", help="Azure subscription ID to use")
    parser.add_argument("--tenant", help="Azure tenant ID to use")
    parser.add_argument("--command", help="Azure CLI command to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize client
    client = AzureMCPClient()
    if not client.start(subscription_id=args.subscription, tenant_id=args.tenant):
        logger.error("Failed to initialize Azure MCP Client")
        sys.exit(1)
        
    try:
        if args.command:
            # Execute a single command
            result = client.execute_command(args.command)
            if result["status"] == "success":
                if isinstance(result.get("output"), str):
                    print(result["output"])
                sys.exit(0)
            else:
                print(f"Error: {result['output']}", file=sys.stderr)
                sys.exit(1)
        else:
            # Interactive mode
            print("Azure MCP Interactive Shell")
            print("Type 'exit' or 'quit' to exit, or 'help' for help")
            print("Type 'info' to see current subscription\n")
            
            while True:
                try:
                    command = input("\naz> ").strip()
                    
                    if command.lower() in ["exit", "quit"]:
                        break
                    elif command.lower() == "help":
                        print("Azure MCP Interactive Shell")
                        print("  - Enter Azure CLI commands directly (e.g., 'az account show')")
                        print("  - Use natural language (e.g., 'list my subscriptions')")
                        print("  - Type 'info' to see current subscription")
                        print("  - Type 'exit' or 'quit' to exit")
                        continue
                    elif command.lower() == "info":
                        info = client.get_current_subscription()
                        if info:
                            print(f"\nCurrent Subscription: {info.get('name')}")
                            print(f"Subscription ID: {info.get('id')}")
                            print(f"Tenant ID: {info.get('tenantId')}")
                        else:
                            print("Error getting subscription info")
                        continue
                    elif not command:
                        continue
                        
                    # Execute the command
                    result = client.execute_command(command)
                    if result["status"] == "success":
                        print(result["output"])
                    else:
                        print(f"Error: {result['output']}", file=sys.stderr)
                        
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                except EOFError:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error: {str(e)}", file=sys.stderr)
                    
    finally:
        # Clean up
        client.stop()


if __name__ == "__main__":
    main()
