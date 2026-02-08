#!/usr/bin/env python3
"""
GCP MCP Security Module

This module provides security validation for gcloud CLI commands,
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
logger = logging.getLogger("gcp-mcp-security")

# Security mode (strict or permissive)
SECURITY_MODE = "strict"  # Can be "strict" or "permissive"

# Dictionary of potentially dangerous commands by security category
# Focus on commands that could lead to security incidents, privilege escalation,
# credential theft, or account takeover
DANGEROUS_COMMANDS: Dict[str, List[str]] = {
    # Identity & Access Management - core of security
    "iam": [
        "gcloud iam service-accounts create",  # Creating service accounts
        "gcloud iam service-accounts delete",  # Deleting service accounts
        "gcloud iam roles create",  # Creating custom roles
        "gcloud iam roles update",  # Updating roles (privilege escalation)
        "gcloud iam roles delete",  # Deleting roles
        "gcloud iam service-accounts keys create",  # Creating service account keys
        "gcloud iam service-accounts keys delete",  # Deleting keys
        "gcloud projects add-iam-policy-binding",  # Adding IAM bindings
        "gcloud projects remove-iam-policy-binding",  # Removing IAM bindings
        "gcloud projects set-iam-policy",  # Setting IAM policy
    ],
    # Project & Organization Management
    "projects": [
        "gcloud projects create",  # Creating projects
        "gcloud projects delete",  # Deleting projects
        "gcloud projects move",  # Moving projects
        "gcloud projects update",  # Updating project settings
    ],
    # Secret Management
    "secrets": [
        "gcloud secrets create",  # Creating secrets
        "gcloud secrets delete",  # Deleting secrets
        "gcloud secrets versions destroy",  # Destroying secret versions
        "gcloud secrets update",  # Updating secrets
    ],
    # Audit & Logging
    "logging": [
        "gcloud logging sinks delete",  # Deleting log sinks
        "gcloud logging sinks update",  # Updating log configuration
        "gcloud audit-logs",  # Modifying audit logs
        "gcloud alpha bq log-sink delete",  # Deleting BigQuery sinks
    ],
    # Firewall & Network Security
    "network": [
        "gcloud compute firewall-rules create",  # Creating firewall rules
        "gcloud compute firewall-rules delete",  # Deleting firewall rules
        "gcloud compute firewall-rules update",  # Updating firewall rules
        "gcloud compute networks delete",  # Deleting networks
        "gcloud compute networks update",  # Updating networks
    ],
    # Compute Resources
    "compute": [
        "gcloud compute instances delete",  # Deleting instances
        "gcloud compute disks delete",  # Deleting disks (data loss)
        "gcloud compute images delete",  # Deleting images
        "gcloud compute snapshots delete",  # Deleting snapshots
    ],
    # Storage Security
    "storage": [
        "gsutil rm -r",  # Deleting buckets/objects
        "gsutil iam delete",  # Deleting IAM bindings
        "gsutil iam set",  # Setting IAM policy
        "gcloud storage buckets delete",  # Deleting buckets
    ],
    # Database
    "sql": [
        "gcloud sql instances delete",  # Deleting SQL instances
        "gcloud sql databases delete",  # Deleting databases
        "gcloud sql backups delete",  # Deleting backups
    ],
    # Authentication
    "auth": [
        "gcloud auth revoke",  # Revoking authentication
        "gcloud auth application-default set-quota-project",  # Changing auth context
    ],
}

# Commands that require extra caution
CAUTION_COMMANDS: Dict[str, List[str]] = {
    "modification": [
        "gcloud compute instances update",
        "gcloud sql instances update",
        "gcloud compute networks update",
        "gcloud compute firewall-rules update",
    ],
}


def validate_gcp_command(command: str) -> None:
    """
    Validate a gcloud CLI command for security issues.
    
    Args:
        command: The gcloud CLI command to validate
        
    Raises:
        ValueError: If the command is invalid or dangerous
    """
    command = command.strip()
    
    # Basic validation
    if not command.startswith(("gcloud ", "gsutil ")):
        raise ValueError("Command must start with 'gcloud' or 'gsutil'")
    
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
        
        # First part should be gcloud/gsutil command
        if i == 0:
            if not part.startswith(("gcloud ", "gsutil ")):
                raise ValueError("First command in pipe must be a gcloud or gsutil command")
            validate_gcp_command(part)
        else:
            # Subsequent parts should be Unix commands
            cmd_name = part.split()[0]
            if not validate_unix_command(cmd_name):
                raise ValueError(f"Unix command not allowed: {cmd_name}")


def is_read_only_command(command: str) -> bool:
    """
    Check if a gcloud CLI command is read-only (safe).
    
    Args:
        command: The command to check
        
    Returns:
        True if command is read-only, False otherwise
    """
    read_only_keywords = ["list", "show", "describe", "get", "export"]
    command_lower = command.lower()
    
    return any(keyword in command_lower for keyword in read_only_keywords)


def get_command_risk_level(command: str) -> str:
    """
    Determine the risk level of a gcloud CLI command.
    
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
    for dangerous_cmd in DANGEROUS_COMMANDS.get("iam", []):
        if dangerous_cmd in command_lower:
            return "critical"
    
    # Check for high-risk commands
    for category in ["secrets", "logging", "storage"]:
        for cmd in DANGEROUS_COMMANDS.get(category, []):
            if cmd in command_lower:
                return "high"
    
    # Check for medium-risk commands
    for category in ["compute", "sql"]:
        for cmd in DANGEROUS_COMMANDS.get(category, []):
            if cmd in command_lower:
                return "medium"
    
    # Check for caution commands
    for caution_cmd in CAUTION_COMMANDS.get("modification", []):
        if caution_cmd in command_lower:
            return "medium"
    
    # Default to low risk for other commands
    return "low"
