#!/usr/bin/env python3
"""
Azure MCP Security Module

This module provides security validation for Azure CLI commands,
including validation of command structure, dangerous command detection,
and pipe command validation.
"""

import logging
import re
import shlex
from typing import Dict, List, Optional

from .tools import validate_unix_command, is_pipe_command, split_pipe_command

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("azure-mcp-security")

# Security mode (strict or permissive)
SECURITY_MODE = "strict"  # Can be "strict" or "permissive"

# Dictionary of potentially dangerous commands by security category
# Focus on commands that could lead to security incidents, privilege escalation,
# credential theft, or account takeover
DANGEROUS_COMMANDS: Dict[str, List[str]] = {
    # Identity & Access Management - core of security
    "identity": [
        "az ad user create",  # Creating new users (potential backdoor accounts)
        "az ad user delete",  # Deleting users (denial of service)
        "az ad app create",  # Creating new apps (potential backdoor)
        "az ad app delete",  # Deleting apps
        "az ad sp create",  # Creating service principals (potential backdoor)
        "az ad sp delete",  # Deleting service principals
        "az role assignment create",  # Assigning roles (privilege escalation)
        "az role assignment delete",  # Removing role assignments
    ],
    # Access Control
    "access": [
        "az role definition create",  # Creating custom roles
        "az role definition update",  # Updating role definitions
        "az role definition delete",  # Deleting role definitions
    ],
    # Key & Secret Management
    "secrets": [
        "az keyvault secret set",  # Setting secrets (potential credential injection)
        "az keyvault secret delete",  # Deleting secrets
        "az keyvault key create",  # Creating keys
        "az keyvault key delete",  # Deleting keys
        "az keyvault purge",  # Purging vault (data loss)
    ],
    # Audit & Logging - tampering with these is critical
    "logging": [
        "az monitor log-profiles delete",  # Deleting log profiles
        "az monitor log-analytics workspace delete",  # Deleting workspace
        "az eventhub namespace delete",  # Deleting event hub (losing logs)
        "az sql server audit-policy update",  # Modifying audit policy
        "az storage logging off",  # Turning off storage logging
    ],
    # Firewall & Network Security
    "network": [
        "az network firewall rule create",  # Creating firewall rules (opening access)
        "az network firewall rule delete",  # Deleting firewall rules
        "az network firewall update",  # Updating firewall
        "az network firewall delete",  # Deleting firewall
        "az network nsg rule create",  # Creating NSG rules (opening access)
        "az network nsg rule delete",  # Deleting NSG rules
    ],
    # Database Security
    "database": [
        "az sql server firewall-rule create",  # Creating SQL firewall rules
        "az sql server firewall-rule delete",  # Deleting SQL firewall rules
        "az sql server update",  # Updating SQL server (security config)
        "az sql db delete",  # Deleting databases (data loss)
        "az sql db backup delete",  # Deleting backups (data loss)
    ],
    # Storage Security
    "storage": [
        "az storage account delete",  # Deleting storage accounts (data loss)
        "az storage container delete",  # Deleting containers (data loss)
        "az storage blob delete",  # Deleting blobs
        "az storage account update",  # Updating account settings
    ],
    # Subscription & Resource Management
    "subscription": [
        "az account set",  # Switching subscriptions
        "az role assignment create --scope",  # Role assignment with scope manipulation
        "az group delete",  # Deleting resource groups (data loss)
    ],
}

# Commands that require extra caution
CAUTION_COMMANDS: Dict[str, List[str]] = {
    "modification": [
        "az vm update",
        "az vm run-command invoke",  # Running commands on VMs
        "az sql db update",
        "az sql server update",
        "az storage account update",
    ],
}


def validate_azure_command(command: str) -> None:
    """
    Validate an Azure CLI command for security issues.
    
    Args:
        command: The Azure CLI command to validate
        
    Raises:
        ValueError: If the command is invalid or dangerous
    """
    command = command.strip()
    
    # Basic validation
    if not command.startswith("az "):
        raise ValueError("Command must start with 'az'")
    
    # Check for pipe commands
    if is_pipe_command(command):
        validate_pipe_command(command)
        return
    
    # Check for dangerous commands
    command_lower = command.lower()
    for category, dangerous_cmds in DANGEROUS_COMMANDS.items():
        for dangerous_cmd in dangerous_cmds:
            if dangerous_cmd in command_lower:
                if SECURITY_MODE == "strict":
                    raise ValueError(
                        f"Command rejected for security reasons: {dangerous_cmd} "
                        f"(category: {category}). This command could compromise security."
                    )
                else:
                    logger.warning(f"Caution: {dangerous_cmd} (category: {category})")
    
    # Warn about caution commands
    for category, caution_cmds in CAUTION_COMMANDS.items():
        for caution_cmd in caution_cmds:
            if caution_cmd in command_lower:
                logger.warning(f"Caution: {caution_cmd} (category: {category})")


def validate_pipe_command(command: str) -> None:
    """
    Validate a piped command for security issues.
    
    Args:
        command: The piped command to validate
        
    Raises:
        ValueError: If any command in the pipe is invalid
    """
    parts = split_pipe_command(command)
    
    for i, part in enumerate(parts):
        part = part.strip()
        
        # First part should be Azure CLI command
        if i == 0:
            if not part.startswith("az "):
                raise ValueError("First command in pipe must be an Azure CLI command")
            validate_azure_command(part)
        else:
            # Subsequent parts should be Unix commands
            cmd_name = part.split()[0]
            if not validate_unix_command(cmd_name):
                raise ValueError(f"Unix command not allowed: {cmd_name}")


def is_read_only_command(command: str) -> bool:
    """
    Check if an Azure CLI command is read-only (safe).
    
    Args:
        command: The command to check
        
    Returns:
        True if command is read-only, False otherwise
    """
    read_only_keywords = ["list", "show", "describe", "get"]
    command_lower = command.lower()
    
    return any(keyword in command_lower for keyword in read_only_keywords)


def get_command_risk_level(command: str) -> str:
    """
    Determine the risk level of an Azure CLI command.
    
    Args:
        command: The command to analyze
        
    Returns:
        Risk level: "critical", "high", "medium", "low", or "safe"
    """
    command_lower = command.lower()
    
    # Check for read-only commands (safe)
    if is_read_only_command(command):
        return "safe"
    
    # Check for critical commands
    for dangerous_cmd in DANGEROUS_COMMANDS.get("identity", []):
        if dangerous_cmd in command_lower:
            return "critical"
    
    # Check for high-risk commands
    for category in ["logging", "secrets", "database"]:
        for cmd in DANGEROUS_COMMANDS.get(category, []):
            if cmd in command_lower:
                return "high"
    
    # Check for caution commands
    for caution_cmd in CAUTION_COMMANDS.get("modification", []):
        if caution_cmd in command_lower:
            return "medium"
    
    # Default to low risk for other commands
    return "low"
