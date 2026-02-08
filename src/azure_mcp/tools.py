#!/usr/bin/env python3
"""
Azure MCP Tools Module

This module provides utilities for command execution, natural language processing,
and piped commands for the Azure MCP server.
"""

import asyncio
import logging
import re
import shlex
from typing import Dict, List, Optional, TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("azure-mcp-tools")

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


# Natural language to Azure CLI command mappings
NL_COMMAND_MAPPINGS = {
    # General Azure
    "who am i": "az account show",
    "caller id": "az account show",
    "account info": "az account show",
    "show my account": "az account show",
    "show my subscription": "az account show",
    "current subscription": "az account show",
    
    # Subscription & Resource Groups
    "list subscriptions": "az account list",
    "show subscriptions": "az account list",
    "get subscriptions": "az account list",
    "subscriptions": "az account list",
    "list resource groups": "az group list",
    "show resource groups": "az group list",
    "get resource groups": "az group list",
    "resource groups": "az group list",
    "list resources": "az resource list",
    "show resources": "az resource list",
    "get resources": "az resource list",
    
    # Entra ID / Azure AD
    "list users": "az ad user list",
    "show users": "az ad user list",
    "get users": "az ad user list",
    "users": "az ad user list",
    "list roles": "az role definition list",
    "show roles": "az role definition list",
    "get roles": "az role definition list",
    "roles": "az role definition list",
    "list groups": "az ad group list",
    "show groups": "az ad group list",
    "get groups": "az ad group list",
    "groups": "az ad group list",
    
    # Storage
    "list storage accounts": "az storage account list",
    "show storage accounts": "az storage account list",
    "get storage accounts": "az storage account list",
    "storage accounts": "az storage account list",
    "list containers": "az storage container list",
    "show containers": "az storage container list",
    "get containers": "az storage container list",
    "containers": "az storage container list",
    
    # Virtual Machines
    "list vms": "az vm list",
    "show vms": "az vm list",
    "get vms": "az vm list",
    "vms": "az vm list",
    "list virtual machines": "az vm list",
    "show virtual machines": "az vm list",
    "get virtual machines": "az vm list",
    "virtual machines": "az vm list",
    
    # Network
    "list network security groups": "az network nsg list",
    "show network security groups": "az network nsg list",
    "get network security groups": "az network nsg list",
    "network security groups": "az network nsg list",
    "nsgs": "az network nsg list",
    "list vnets": "az network vnet list",
    "show vnets": "az network vnet list",
    "get vnets": "az network vnet list",
    "vnets": "az network vnet list",
    "list vpn gateways": "az network vpn-gateway list",
    "show vpn gateways": "az network vpn-gateway list",
    "get vpn gateways": "az network vpn-gateway list",
    
    # SQL & Databases
    "list sql servers": "az sql server list",
    "show sql servers": "az sql server list",
    "get sql servers": "az sql server list",
    "sql servers": "az sql server list",
    "list sql databases": "az sql db list",
    "show sql databases": "az sql db list",
    "get sql databases": "az sql db list",
    "sql databases": "az sql db list",
    "list databases": "az sql db list",
    "show databases": "az sql db list",
    "get databases": "az sql db list",
    "databases": "az sql db list",
    
    # Key Vault
    "list key vaults": "az keyvault list",
    "show key vaults": "az keyvault list",
    "get key vaults": "az keyvault list",
    "key vaults": "az keyvault list",
    "list secrets": "az keyvault secret list",
    "show secrets": "az keyvault secret list",
    "get secrets": "az keyvault secret list",
    "secrets": "az keyvault secret list",
    
    # App Services
    "list app services": "az appservice list",
    "show app services": "az appservice list",
    "get app services": "az appservice list",
    "app services": "az appservice list",
    "list web apps": "az webapp list",
    "show web apps": "az webapp list",
    "get web apps": "az webapp list",
    "web apps": "az webapp list",
}


def interpret_natural_language(query: str) -> Optional[str]:
    """
    Convert natural language query to Azure CLI command.
    
    Args:
        query: Natural language query
        
    Returns:
        Azure CLI command or None if no mapping found
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
