#!/usr/bin/env python3
"""
AWS MCP Server Module

This module provides the core server functionality for executing AWS CLI commands
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
)
from .security import (
    validate_aws_command,
    validate_pipe_command,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aws-mcp-server")

# AWS Region for commands that need it but don't have it specified
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))


class CommandValidationError(Exception):
    """Exception raised when a command fails validation."""
    pass


class CommandExecutionError(Exception):
    """Exception raised when a command fails to execute."""
    pass


def is_auth_error(error_output: str) -> bool:
    """Detect if an error is related to authentication.
    
    Args:
        error_output: The error output from AWS CLI
        
    Returns:
        True if the error is related to authentication, False otherwise
    """
    auth_error_patterns = [
        "Unable to locate credentials",
        "ExpiredToken",
        "AccessDenied",
        "AuthFailure",
        "The security token included in the request is invalid",
        "The config profile could not be found",
        "UnrecognizedClientException",
        "InvalidClientTokenId",
        "InvalidAccessKeyId",
        "SignatureDoesNotMatch",
        "Your credential profile is not properly configured",
        "credentials could not be refreshed",
        "NoCredentialProviders",
    ]
    return any(pattern in error_output for pattern in auth_error_patterns)


def execute_aws_command(command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Execute an AWS CLI command and return the result.
    
    Validates, executes, and processes the results of an AWS CLI command,
    handling timeouts and output size limits.
    
    Args:
        command: The AWS CLI command to execute (must start with 'aws')
        timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
        
    Returns:
        Dictionary with command output and status
    """
    logger.info(f"Executing AWS command: {command}")
    
    # Check if this is a piped command
    if is_pipe_command(command):
        return execute_pipe_command(command, timeout)
        
    # Validate the command
    try:
        validate_aws_command(command)
    except ValueError as e:
        logger.warning(f"Command validation error: {e}")
        return {"status": "error", "output": f"Command validation error: {str(e)}"}
        
    # Set timeout
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
        
    # Check if the command needs a region and doesn't have one specified
    # Split by spaces and check for EC2 service specifically
    cmd_parts = shlex.split(command)
    is_ec2_command = len(cmd_parts) >= 2 and cmd_parts[0] == "aws" and cmd_parts[1] == "ec2"
    has_region = "--region" in cmd_parts
    
    # If it's an EC2 command and doesn't have --region
    if is_ec2_command and not has_region:
        # Add the region parameter
        command = f"{command} --region {AWS_REGION}"
        logger.debug(f"Added region to command: {command}")
        
    logger.debug(f"Executing AWS command: {command}")
    
    try:
        # Split command safely for exec
        cmd_parts = shlex.split(command)
        
        # Create subprocess
        process = subprocess.Popen(
            cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Use text mode for easier string handling
        )
        
        try:
            # Wait for the process with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            logger.debug(f"Command completed with return code: {process.returncode}")
            
            # Truncate output if necessary
            if len(stdout) > MAX_OUTPUT_SIZE:
                logger.info(f"Output truncated from {len(stdout)} to {MAX_OUTPUT_SIZE} characters")
                stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"
                
            if process.returncode != 0:
                logger.warning(f"Command failed with return code {process.returncode}: {command}")
                logger.debug(f"Command error output: {stderr}")
                
                if is_auth_error(stderr):
                    return {"status": "error", "output": f"Authentication error: {stderr}\nPlease check your AWS credentials."}
                    
                return {"status": "error", "output": stderr or "Command failed with no error output"}
                
            # Parse JSON output if possible
            try:
                # Check if output is JSON
                parsed_output = json.loads(stdout)
                return {"status": "success", "output": parsed_output}
            except json.JSONDecodeError:
                # Not JSON, return as string
                return {"status": "success", "output": stdout}
                
        except subprocess.TimeoutExpired:
            # Kill the process on timeout
            process.kill()
            logger.warning(f"Command timed out after {timeout} seconds: {command}")
            return {"status": "error", "output": f"Command timed out after {timeout} seconds"}
            
    except Exception as e:
        logger.error(f"Failed to execute command: {str(e)}")
        return {"status": "error", "output": f"Failed to execute command: {str(e)}"}


def execute_pipe_command(pipe_command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """Execute a command that contains pipes.
    
    Validates and executes a piped command where output is fed into subsequent commands.
    The first command must be an AWS CLI command, and subsequent commands must be
    allowed Unix utilities.
    
    Args:
        pipe_command: The piped command to execute
        timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)
        
    Returns:
        Dictionary with command output and status
    """
    logger.info(f"Executing piped command: {pipe_command}")
    
    # Set timeout
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
        
    # Validate the pipe command
    try:
        validate_pipe_command(pipe_command)
    except ValueError as e:
        logger.warning(f"Pipe command validation error: {e}")
        return {"status": "error", "output": f"Command validation error: {str(e)}"}
        
    try:
        # Execute the command with shell=True to handle pipes
        process = subprocess.Popen(
            pipe_command,
            shell=True,  # Required for pipes
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            # Wait for the process with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            logger.debug(f"Pipe command completed with return code: {process.returncode}")
            
            # Truncate output if necessary
            if len(stdout) > MAX_OUTPUT_SIZE:
                logger.info(f"Output truncated from {len(stdout)} to {MAX_OUTPUT_SIZE} characters")
                stdout = stdout[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"
                
            if process.returncode != 0:
                logger.warning(f"Pipe command failed with return code {process.returncode}: {pipe_command}")
                logger.debug(f"Command error output: {stderr}")
                
                if is_auth_error(stderr):
                    return {"status": "error", "output": f"Authentication error: {stderr}\nPlease check your AWS credentials."}
                    
                return {"status": "error", "output": stderr or "Command failed with no error output"}
                
            # Return the output (pipe output is typically text, not JSON)
            return {"status": "success", "output": stdout}
            
        except subprocess.TimeoutExpired:
            # Kill the process on timeout
            process.kill()
            logger.warning(f"Pipe command timed out after {timeout} seconds: {pipe_command}")
            return {"status": "error", "output": f"Command timed out after {timeout} seconds"}
            
    except Exception as e:
        logger.error(f"Failed to execute pipe command: {str(e)}")
        return {"status": "error", "output": f"Failed to execute pipe command: {str(e)}"}
