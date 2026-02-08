#!/usr/bin/env python3
"""
GCP MCP Tools Module

This module provides utilities for command execution, natural language processing,
and piped commands for the GCP MCP server.
"""

import asyncio
import logging
import re
import shlex
from typing import Dict, List, Optional, TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gcp-mcp-tools")

# Constants
DEFAULT_TIMEOUT = 30  # 30 seconds
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB

# List of allowed Unix commands that can be used in a pipe
ALLOWED_UNIX_COMMANDS = [
    # File operations
    "cat", "ls", "cd", "pwd", "cp", "mv", "rm", "mkdir", "touch", "chmod", "chown",
    # Text processing
    "grep", "sed", "awk", "cut", "sort", "uniq", "wc", "head", "tail", "tr", "find",
    # System information
    "ps", "top", "df", "du", "uname", "whoami", "date", "which", "echo",
    # Networking
    "ping", "ifconfig", "netstat", "curl", "wget", "dig", "nslookup", "ssh", "scp",
    # Other utilities
    "man", "less", "tar", "gzip", "gunzip", "zip", "unzip", "xargs", "jq", "tee",
]


class CommandResult(TypedDict):
    """Type definition for command execution results."""
    
    status: str
    output: str


# Natural language to gcloud CLI command mappings
NL_COMMAND_MAPPINGS = {
    # General GCP
    "who am i": "gcloud auth list",
    "current account": "gcloud config get-value account",
    "current project": "gcloud config get-value project",
    "show my account": "gcloud auth list",
    "show my project": "gcloud config get-value project",
    "get current project": "gcloud config get-value project",
    
    # Projects & Accounts
    "list projects": "gcloud projects list",
    "show projects": "gcloud projects list",
    "get projects": "gcloud projects list",
    "projects": "gcloud projects list",
    "list accounts": "gcloud auth list",
    "show accounts": "gcloud auth list",
    "get accounts": "gcloud auth list",
    "accounts": "gcloud auth list",
    
    # IAM & Access
    "list iam policies": "gcloud projects get-iam-policy",
    "show iam policies": "gcloud projects get-iam-policy",
    "get iam policies": "gcloud projects get-iam-policy",
    "list roles": "gcloud iam roles list",
    "show roles": "gcloud iam roles list",
    "get roles": "gcloud iam roles list",
    "roles": "gcloud iam roles list",
    "list members": "gcloud projects get-iam-policy",
    "show members": "gcloud projects get-iam-policy",
    
    # Compute Engine
    "list instances": "gcloud compute instances list",
    "show instances": "gcloud compute instances list",
    "get instances": "gcloud compute instances list",
    "instances": "gcloud compute instances list",
    "list vms": "gcloud compute instances list",
    "show vms": "gcloud compute instances list",
    "get vms": "gcloud compute instances list",
    "vms": "gcloud compute instances list",
    "list images": "gcloud compute images list",
    "show images": "gcloud compute images list",
    "images": "gcloud compute images list",
    
    # Cloud Storage
    "list buckets": "gsutil ls",
    "show buckets": "gsutil ls",
    "get buckets": "gsutil ls",
    "buckets": "gsutil ls",
    "list storage": "gsutil ls",
    "show storage": "gsutil ls",
    "get storage": "gsutil ls",
    
    # Cloud SQL
    "list sql instances": "gcloud sql instances list",
    "show sql instances": "gcloud sql instances list",
    "get sql instances": "gcloud sql instances list",
    "sql instances": "gcloud sql instances list",
    "list databases": "gcloud sql databases list",
    "show databases": "gcloud sql databases list",
    "get databases": "gcloud sql databases list",
    "databases": "gcloud sql databases list",
    
    # Networking
    "list networks": "gcloud compute networks list",
    "show networks": "gcloud compute networks list",
    "get networks": "gcloud compute networks list",
    "networks": "gcloud compute networks list",
    "list vpcs": "gcloud compute networks list",
    "show vpcs": "gcloud compute networks list",
    "get vpcs": "gcloud compute networks list",
    "vpcs": "gcloud compute networks list",
    "list firewalls": "gcloud compute firewall-rules list",
    "show firewalls": "gcloud compute firewall-rules list",
    "get firewalls": "gcloud compute firewall-rules list",
    "firewall rules": "gcloud compute firewall-rules list",
    "list routes": "gcloud compute routes list",
    "show routes": "gcloud compute routes list",
    "get routes": "gcloud compute routes list",
    "routes": "gcloud compute routes list",
    
    # Kubernetes
    "list clusters": "gcloud container clusters list",
    "show clusters": "gcloud container clusters list",
    "get clusters": "gcloud container clusters list",
    "clusters": "gcloud container clusters list",
    "list gke clusters": "gcloud container clusters list",
    
    # Cloud Functions
    "list functions": "gcloud functions list",
    "show functions": "gcloud functions list",
    "get functions": "gcloud functions list",
    "functions": "gcloud functions list",
    "list cloud functions": "gcloud functions list",
    
    # Other Services
    "list services": "gcloud services list",
    "show services": "gcloud services list",
    "get services": "gcloud services list",
    "services": "gcloud services list",
}


def interpret_natural_language(query: str) -> Optional[str]:
    """
    Convert natural language query to gcloud CLI command.
    
    Args:
        query: Natural language query
        
    Returns:
        gcloud CLI command or None if no mapping found
    """
    query_lower = query.lower().strip()
    
    # Direct mapping lookup
    if query_lower in NL_COMMAND_MAPPINGS:
        return NL_COMMAND_MAPPINGS[query_lower]
    
    # Partial matching for more flexible queries
    for key, value in NL_COMMAND_MAPPINGS.items():
        if key in query_lower:
            return value
    
    return None


def validate_unix_command(command: str) -> bool:
    """
    Validate that a Unix command is in the allowed list.
    
    Args:
        command: The Unix command to validate
        
    Returns:
        True if command is allowed, False otherwise
    """
    cmd_name = command.split()[0] if command else ""
    return cmd_name in ALLOWED_UNIX_COMMANDS


def is_pipe_command(command: str) -> bool:
    """
    Check if a command contains pipe operators.
    
    Args:
        command: The command to check
        
    Returns:
        True if command contains pipes, False otherwise
    """
    return "|" in command or ">" in command or "<" in command


def split_pipe_command(command: str) -> List[str]:
    """
    Split a piped command into individual commands.
    
    Args:
        command: The piped command
        
    Returns:
        List of individual commands
    """
    # Simple split on pipe
    parts = command.split("|")
    return [part.strip() for part in parts]


async def execute_command_async(cmd: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, str]:
    """
    Asynchronously execute a command.
    
    Args:
        cmd: Command to execute
        timeout: Command timeout in seconds
        
    Returns:
        Dictionary with command output and status
    """
    import subprocess
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""
            
            if process.returncode == 0:
                return {"status": "success", "output": output}
            else:
                return {"status": "error", "output": error or output}
                
        except asyncio.TimeoutError:
            process.kill()
            return {"status": "error", "output": f"Command timed out after {timeout} seconds"}
            
    except Exception as e:
        return {"status": "error", "output": str(e)}


def truncate_output(output: str, max_size: int = MAX_OUTPUT_SIZE) -> str:
    """
    Truncate output if it exceeds maximum size.
    
    Args:
        output: The output string to truncate
        max_size: Maximum allowed size
        
    Returns:
        Truncated output with warning if needed
    """
    if len(output) > max_size:
        return output[:max_size] + f"\n\n[Output truncated - exceeded {max_size} bytes]"
    return output
