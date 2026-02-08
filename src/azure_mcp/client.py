#!/usr/bin/env python3
"""
Azure MCP Client Module

This module provides a client interface for interacting with the Azure MCP server,
which executes Azure CLI commands securely and handles natural language processing.
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
logger = logging.getLogger("azure-mcp-client")


class AzureMCPClient:
    """Client for Azure Model Context Protocol server."""
    
    def __init__(self):
        """Initialize the Azure MCP Client."""
        self.subscription_id = None
        self.tenant_id = None
        self._initialized = False
        self._running = False
    
    def is_running(self) -> bool:
        """
        Check if the client is running.
        
        Returns:
            True if the client is running, False otherwise
        """
        return self._running
    
    def start(self, subscription_id: Optional[str] = None, tenant_id: Optional[str] = None) -> bool:
        """
        Initialize the Azure MCP Client with subscription and tenant IDs.
        
        Args:
            subscription_id: Optional Azure subscription ID
            tenant_id: Optional Azure tenant ID
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            # Set subscription and tenant IDs
            self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
            self.tenant_id = tenant_id or os.getenv("AZURE_TENANT_ID")
            
            # Check if Azure CLI is installed and configured
            if not self._check_azure_cli_installed():
                logger.error("Azure CLI is not installed or not in PATH.")
                return False
            
            # Check if user is logged in
            if not self._check_azure_login():
                logger.warning("Azure CLI not authenticated. User may need to run 'az login'")
                # Still allow initialization, user can login interactively
            
            # Mark as initialized and running
            self._initialized = True
            self._running = True
            logger.info("Azure MCP Client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Azure MCP Client: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the Azure MCP Client and clean up resources."""
        # Reset state
        self._initialized = False
        self._running = False
        logger.info("Azure MCP Client stopped")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute an Azure CLI command.
        
        Args:
            command: Azure CLI command to execute, can be in natural language
            
        Returns:
            Dictionary with command output and status
        """
        if not self._initialized:
            logger.warning("Azure MCP Client not initialized. Call start() first.")
            return {"status": "error", "output": "Client not initialized. Call start() first."}
        
        # Try to interpret natural language if the command doesn't start with 'az'
        if not command.strip().startswith("az "):
            interpreted_cmd = interpret_natural_language(command)
            if interpreted_cmd:
                logger.info(f"Interpreted '{command}' as '{interpreted_cmd}'")
                command = interpreted_cmd
            else:
                logger.warning(f"Could not interpret natural language command: {command}")
                return {
                    "status": "error",
                    "output": f"Could not interpret command: {command}\nPlease use Azure CLI syntax (az command) or try a different natural language query."
                }
        
        # Execute the command using the server module
        from .server import execute_azure_command
        return execute_azure_command(command)
    
    def _check_azure_cli_installed(self) -> bool:
        """
        Check if Azure CLI is installed and accessible.
        
        Returns:
            True if Azure CLI is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["az", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Azure CLI: {e}")
            return False
    
    def _check_azure_login(self) -> bool:
        """
        Check if user is logged in to Azure.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            result = subprocess.run(
                ["az", "account", "show"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Azure login: {e}")
            return False
    
    def get_current_subscription(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current subscription.
        
        Returns:
            Dictionary with subscription info or None if error
        """
        try:
            result = subprocess.run(
                ["az", "account", "show"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting subscription info: {e}")
            return None
    
    def list_subscriptions(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all subscriptions.
        
        Returns:
            List of subscription dictionaries or None if error
        """
        try:
            result = subprocess.run(
                ["az", "account", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error listing subscriptions: {e}")
            return None
