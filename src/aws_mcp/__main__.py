#!/usr/bin/env python3
"""
AWS MCP Main Module

This module provides a command-line interface for the AWS MCP server.
It allows executing AWS CLI commands directly or through an interactive shell.
"""

import argparse
import logging
import os
import sys

from .client import AWSMCPClient
from .tools import interpret_natural_language

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aws-mcp")


def main():
    """Main entry point for the AWS MCP CLI."""
    parser = argparse.ArgumentParser(description="AWS MCP - Model Context Protocol for AWS CLI")
    parser.add_argument("--profile", help="AWS profile to use")
    parser.add_argument("--region", help="AWS region to use")
    parser.add_argument("--command", help="AWS CLI command to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize client
    client = AWSMCPClient()
    if not client.start(aws_profile=args.profile, aws_region=args.region):
        logger.error("Failed to initialize AWS MCP Client")
        sys.exit(1)
        
    try:
        if args.command:
            # Execute a single command
            result = client.execute_command(args.command)
            if result["status"] == "success":
                if isinstance(result["output"], (dict, list)):
                    import json
                    print(json.dumps(result["output"], indent=2))
                else:
                    print(result["output"])
                sys.exit(0)
            else:
                print(f"Error: {result['output']}", file=sys.stderr)
                sys.exit(1)
        else:
            # Interactive mode
            print("AWS MCP Interactive Shell")
            print("Type 'exit' or 'quit' to exit, or 'help' for help")
            
            while True:
                try:
                    command = input("\naws> ").strip()
                    
                    if command.lower() in ["exit", "quit"]:
                        break
                    elif command.lower() == "help":
                        print("AWS MCP Interactive Shell")
                        print("  - Enter AWS CLI commands directly (e.g., 'aws s3 ls')")
                        print("  - Use natural language (e.g., 'list my S3 buckets')")
                        print("  - Type 'exit' or 'quit' to exit")
                        continue
                    elif not command:
                        continue
                        
                    # Execute the command
                    result = client.execute_command(command)
                    if result["status"] == "success":
                        if isinstance(result["output"], (dict, list)):
                            import json
                            print(json.dumps(result["output"], indent=2))
                        else:
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
