#!/usr/bin/env python3
"""
GCP MCP Main Module

This module provides a command-line interface for the GCP MCP server.
It allows executing gcloud CLI commands directly or through an interactive shell.
"""

import argparse
import logging
import os
import sys

from .client import GCPMCPClient
from .tools import interpret_natural_language

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gcp-mcp")


def main():
    """Main entry point for the GCP MCP CLI."""
    parser = argparse.ArgumentParser(description="GCP MCP - Model Context Protocol for gcloud CLI")
    parser.add_argument("--project", help="GCP project ID to use")
    parser.add_argument("--command", help="gcloud CLI command to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize client
    client = GCPMCPClient()
    if not client.start(project_id=args.project):
        logger.error("Failed to initialize GCP MCP Client")
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
            print("GCP MCP Interactive Shell")
            print("Type 'exit' or 'quit' to exit, or 'help' for help")
            print("Type 'info' to see current project\n")
            
            while True:
                try:
                    command = input("\ngcloud> ").strip()
                    
                    if command.lower() in ["exit", "quit"]:
                        break
                    elif command.lower() == "help":
                        print("GCP MCP Interactive Shell")
                        print("  - Enter gcloud/gsutil commands directly (e.g., 'gcloud compute instances list')")
                        print("  - Use natural language (e.g., 'list my instances')")
                        print("  - Type 'info' to see current project")
                        print("  - Type 'exit' or 'quit' to exit")
                        continue
                    elif command.lower() == "info":
                        info = client.get_current_project()
                        if info:
                            print(f"\nCurrent Project: {info.get('project_id')}")
                        else:
                            print("Error getting project info")
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
