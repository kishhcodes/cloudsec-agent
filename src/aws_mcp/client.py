#!/usr/bin/env python3
"""
AWS MCP Client Module

This module provides a client interface for interacting with the AWS MCP server,
which executes AWS CLI commands securely and handles natural language processing.
"""

import os
import sys
import json
import logging
import subprocess
from typing import Dict, Any, Optional, List

from .tools import interpret_natural_language

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aws-mcp-client")


class AWSMCPClient:
    """Client for AWS Model Context Protocol server."""
    
    def __init__(self):
        """Initialize the AWS MCP Client."""
        self.aws_profile = None
        self.aws_region = None
        self._initialized = False
        self._running = False
    
    def is_running(self) -> bool:
        """
        Check if the client is running.
        
        Returns:
            True if the client is running, False otherwise
        """
        return self._running
    
    def start(self, aws_profile: Optional[str] = None, aws_region: Optional[str] = None) -> bool:
        """
        Initialize the AWS MCP Client with AWS profile and region.
        
        Args:
            aws_profile: Optional AWS profile name
            aws_region: Optional AWS region name
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            # Set AWS profile and region
            self.aws_profile = aws_profile
            self.aws_region = aws_region
            
            # Set environment variables if profile or region is specified
            if self.aws_profile:
                os.environ["AWS_PROFILE"] = self.aws_profile
                logger.info(f"Set AWS profile to: {self.aws_profile}")
            
            if self.aws_region:
                os.environ["AWS_REGION"] = self.aws_region
                os.environ["AWS_DEFAULT_REGION"] = self.aws_region
                logger.info(f"Set AWS region to: {self.aws_region}")
            
            # Check if AWS CLI is installed and configured
            if not self._check_aws_cli_installed():
                logger.error("AWS CLI is not installed or not in PATH.")
                return False
            
            # Mark as initialized and running
            self._initialized = True
            self._running = True
            logger.info("AWS MCP Client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing AWS MCP Client: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the AWS MCP Client and clean up resources."""
        # Reset state
        self._initialized = False
        self._running = False
        logger.info("AWS MCP Client stopped")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute an AWS CLI command.
        
        Args:
            command: AWS CLI command to execute, can be in natural language
            
        Returns:
            Dictionary with command output and status
        """
        if not self._initialized:
            logger.warning("AWS MCP Client not initialized. Call start() first.")
            return {"status": "error", "output": "Client not initialized. Call start() first."}
        
        # Try to interpret natural language if the command doesn't start with 'aws'
        if not command.strip().startswith("aws "):
            interpreted_cmd = interpret_natural_language(command)
            if interpreted_cmd:
                logger.info(f"Interpreted '{command}' as '{interpreted_cmd}'")
                command = interpreted_cmd
            else:
                logger.warning(f"Could not interpret natural language command: {command}")
                return {
                    "status": "error",
                    "output": f"Could not interpret command: {command}\nPlease use AWS CLI syntax (aws service command) or try a different natural language query."
                }
        
        # Execute the command using the server module
        from .server import execute_aws_command
        return execute_aws_command(command)
    
    def _check_aws_cli_installed(self) -> bool:
        """
        Check if AWS CLI is installed and accessible.
        
        Returns:
            True if AWS CLI is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["aws", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking AWS CLI: {e}")
            return False
