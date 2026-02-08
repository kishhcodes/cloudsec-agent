#!/usr/bin/env python3
"""
GCP MCP Server Module

This module provides the core server functionality for executing gcloud CLI commands
and processing the results.
"""

import asyncio
import json
import logging
import os
import shlex
import subprocess
from typing import Dict, Any, Optional

from .tools import (
    DEFAULT_TIMEOUT, 
    MAX_OUTPUT_SIZE, 
    CommandResult,
    is_pipe_command,
    split_pipe_command,
    truncate_output,
)
from .security import (
    validate_gcp_command,
    validate_pipe_command,
    get_command_risk_level,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gcp-mcp-server")

# GCP project ID for commands that need it but don't have it specified
GCP_PROJECT = os.environ.get("GCP_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")


class CommandValidationError(Exception):
    """Exception raised when a command fails validation."""
    pass


class CommandExecutionError(Exception):
    """Exception raised when a command fails to execute."""
    pass


def is_auth_error(error_output: str) -> bool:
    """Detect if an error is related to authentication.
    
    Args:
        error_output: The error output from gcloud CLI
        
    Returns:
        True if the error is related to authentication, False otherwise
    """
    auth_error_patterns = [
        "not logged in",
        "credential",
        "authentication",
        "unauthorized",
        "permission denied",
        "access denied",
        "could not be found",
        "not configured",
        "invalid credentials",
        "Application Default Credentials",
        "Please run 'gcloud auth",
    ]
    return any(pattern in error_output for pattern in auth_error_patterns)


def execute_gcp_command(command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Execute a gcloud CLI command and return the result.
    
    Validates, executes, and processes the results of a gcloud CLI command,
    handling timeouts and output size limits.
    
    Args:
        command: The gcloud/gsutil CLI command to execute
        timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
        
    Returns:
        Dictionary with command output and status
    """
    logger.info(f"Executing gcloud command: {command}")
    
    # Check if this is a piped command
    if is_pipe_command(command):
        return execute_pipe_command(command, timeout)
        
    # Validate the command
    try:
        validate_gcp_command(command)
    except ValueError as e:
        logger.warning(f"Command validation error: {e}")
        return {"status": "error", "output": f"Command validation error: {str(e)}"}
        
    # Set timeout
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    # Add project context if available and not already specified
    if GCP_PROJECT and "--project" not in command and "gcloud" in command:
        command += f" --project {GCP_PROJECT}"
    
    # Execute the command
    try:
        logger.debug(f"Running command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout
        error = result.stderr
        
        # Check for authentication errors
        if result.returncode != 0 and is_auth_error(error or output):
            logger.error("Authentication error detected")
            return {
                "status": "error",
                "output": "Authentication error. Please run 'gcloud auth login' to authenticate.",
                "error_type": "auth_error"
            }
        
        # Process successful execution
        if result.returncode == 0:
            # Try to parse JSON output
            try:
                parsed = json.loads(output)
                return {
                    "status": "success",
                    "output": truncate_output(json.dumps(parsed, indent=2)),
                    "raw_output": parsed
                }
            except json.JSONDecodeError:
                # Not JSON, return as-is
                return {
                    "status": "success",
                    "output": truncate_output(output)
                }
        else:
            # Command failed
            error_msg = error if error else output
            logger.warning(f"Command failed: {error_msg}")
            return {
                "status": "error",
                "output": truncate_output(error_msg),
                "command": command,
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        return {
            "status": "error",
            "output": f"Command timed out after {timeout} seconds",
            "error_type": "timeout"
        }
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {
            "status": "error",
            "output": f"Error executing command: {str(e)}",
            "error_type": "execution_error"
        }


def execute_pipe_command(command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Execute a piped gcloud CLI command.
    
    Args:
        command: The piped command to execute
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary with command output and status
    """
    logger.info(f"Executing piped command: {command}")
    
    try:
        validate_pipe_command(command)
    except ValueError as e:
        logger.warning(f"Pipe command validation error: {e}")
        return {"status": "error", "output": f"Command validation error: {str(e)}"}
    
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "output": truncate_output(result.stdout)
            }
        else:
            return {
                "status": "error",
                "output": truncate_output(result.stderr or result.stdout),
                "return_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"Piped command timed out after {timeout} seconds")
        return {
            "status": "error",
            "output": f"Command timed out after {timeout} seconds",
            "error_type": "timeout"
        }
    except Exception as e:
        logger.error(f"Error executing piped command: {e}")
        return {
            "status": "error",
            "output": f"Error executing piped command: {str(e)}",
            "error_type": "execution_error"
        }


def analyze_command_safety(command: str) -> Dict[str, Any]:
    """Analyze the safety/risk level of a gcloud CLI command without executing it.
    
    Args:
        command: The command to analyze
        
    Returns:
        Dictionary with risk analysis
    """
    try:
        validate_gcp_command(command)
        risk_level = get_command_risk_level(command)
        return {
            "safe": True,
            "risk_level": risk_level,
            "command": command
        }
    except ValueError as e:
        return {
            "safe": False,
            "error": str(e),
            "command": command
        }
