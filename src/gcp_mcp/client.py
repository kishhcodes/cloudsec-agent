#!/usr/bin/env python3
"""
GCP MCP Client Module

This module provides a client interface for interacting with the GCP MCP server,
which executes gcloud CLI commands securely and handles natural language processing.
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
logger = logging.getLogger("gcp-mcp-client")


class GCPMCPClient:
    """Client for GCP Model Context Protocol server."""
    
    def __init__(self):
        """Initialize the GCP MCP Client."""
        self.project_id = None
        self._initialized = False
        self._running = False
    
    def is_running(self) -> bool:
        """
        Check if the client is running.
        
        Returns:
            True if the client is running, False otherwise
        """
        return self._running
    
    def start(self, project_id: Optional[str] = None) -> bool:
        """
        Initialize the GCP MCP Client with project ID.
        
        Args:
            project_id: Optional GCP project ID
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            # Set project ID
            self.project_id = project_id or os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
            
            # Check if gcloud CLI is installed and configured
            if not self._check_gcloud_installed():
                logger.error("gcloud CLI is not installed or not in PATH.")
                return False
            
            # Check if user is logged in
            if not self._check_gcloud_login():
                logger.warning("gcloud CLI not authenticated. User may need to run 'gcloud auth login'")
                # Still allow initialization, user can login interactively
            
            # Mark as initialized and running
            self._initialized = True
            self._running = True
            logger.info("GCP MCP Client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing GCP MCP Client: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the GCP MCP Client and clean up resources."""
        # Reset state
        self._initialized = False
        self._running = False
        logger.info("GCP MCP Client stopped")
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a gcloud CLI command.
        
        Args:
            command: gcloud/gsutil CLI command to execute, can be in natural language
            
        Returns:
            Dictionary with command output and status
        """
        if not self._initialized:
            logger.warning("GCP MCP Client not initialized. Call start() first.")
            return {"status": "error", "output": "Client not initialized. Call start() first."}
        
        # Try to interpret natural language if the command doesn't start with gcloud/gsutil
        if not command.strip().startswith(("gcloud ", "gsutil ")):
            interpreted_cmd = interpret_natural_language(command)
            if interpreted_cmd:
                logger.info(f"Interpreted '{command}' as '{interpreted_cmd}'")
                command = interpreted_cmd
            else:
                logger.warning(f"Could not interpret natural language command: {command}")
                return {
                    "status": "error",
                    "output": f"Could not interpret command: {command}\nPlease use gcloud CLI syntax (gcloud command) or try a different natural language query."
                }
        
        # Execute the command using the server module
        from .server import execute_gcp_command
        return execute_gcp_command(command)
    
    def _check_gcloud_installed(self) -> bool:
        """
        Check if gcloud CLI is installed and accessible.
        
        Returns:
            True if gcloud CLI is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["gcloud", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking gcloud CLI: {e}")
            return False
    
    def _check_gcloud_login(self) -> bool:
        """
        Check if user is logged in to gcloud.
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking gcloud login: {e}")
            return False
    
    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current project.
        
        Returns:
            Dictionary with project info or None if error
        """
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            project_id = result.stdout.strip()
            return {"project_id": project_id} if project_id else None
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return None
    
    def list_projects(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all GCP projects.
        
        Returns:
            List of project dictionaries or None if error
        """
        try:
            result = subprocess.run(
                ["gcloud", "projects", "list", "--format=json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return None
