#!/usr/bin/env python3
"""
AWS MCP Security Module

This module provides security validation for AWS CLI commands,
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
logger = logging.getLogger("aws-mcp-security")

# Security mode (strict or permissive)
SECURITY_MODE = "strict"  # Can be "strict" or "permissive"

# Dictionary of potentially dangerous commands by security category
# Focus on commands that could lead to security incidents, privilege escalation,
# credential theft, or account takeover
DANGEROUS_COMMANDS: Dict[str, List[str]] = {
    # Identity and Access Management - core of security
    "iam": [
        "aws iam create-user",  # Creating new users (potential backdoor accounts)
        "aws iam create-access-key",  # Creating credentials (could lead to credential theft)
        "aws iam attach-user-policy",  # Attaching policies to users (privilege escalation)
        "aws iam attach-role-policy",  # Attaching policies to roles (privilege escalation)
        "aws iam attach-group-policy",  # Attaching policies to groups (privilege escalation)
        "aws iam create-policy",  # Creating new policies (potentially overprivileged)
        "aws iam put-user-policy",  # Inline policies for users (privilege escalation)
        "aws iam put-role-policy",  # Inline policies for roles (privilege escalation)
        "aws iam put-group-policy",  # Inline policies for groups (privilege escalation)
        "aws iam create-login-profile",  # Creating console passwords (potential backdoor)
        "aws iam update-access-key",  # Updating access key status (credential management)
        "aws iam update-assume-role-policy",  # Changing who can assume a role
        "aws iam remove-role-from-instance-profile",  # Removing roles (privilege escalation)
        "aws iam update-role",  # Modifying role (privilege escalation)
        "aws iam create-virtual-mfa-device",  # Creating MFA devices
        "aws iam deactivate-mfa-device",  # Disabling MFA (security circumvention)
        "aws iam delete-",  # Any IAM delete operations (potential denial of service)
    ],
    # Security, Identity & Compliance services
    "organizations": [
        "aws organizations create-account",  # Creating accounts
        "aws organizations leave-organization",  # Leaving an organization
        "aws organizations remove-account-from-organization",  # Removing accounts
        "aws organizations disable-policy-type",  # Disabling policy enforcement
        "aws organizations create-policy",  # Creating organization policies
        "aws organizations attach-policy",  # Attaching organization policies
    ],
    "sts": [
        "aws sts assume-role",  # Assuming roles with potentially higher privileges
        "aws sts get-session-token",  # Getting session tokens
        "aws sts get-federation-token",  # Getting federated tokens
    ],
    "secretsmanager": [
        "aws secretsmanager put-secret-value",  # Changing secrets
        "aws secretsmanager update-secret",  # Updating secrets
        "aws secretsmanager delete-secret",  # Deleting secrets
        "aws secretsmanager restore-secret",  # Restoring deleted secrets
    ],
    "kms": [
        "aws kms schedule-key-deletion",  # Scheduling key deletion (potential data loss)
        "aws kms disable-key",  # Disabling keys (potential data loss)
        "aws kms create-grant",  # Creating grants (key access)
        "aws kms revoke-grant",  # Revoking grants (potential denial of service)
    ],
    # Audit & Logging services - tampering with these is critical
    "cloudtrail": [
        "aws cloudtrail delete-trail",  # Deleting audit trails
        "aws cloudtrail stop-logging",  # Stopping audit logging
        "aws cloudtrail update-trail",  # Modifying audit configurations
        "aws cloudtrail put-event-selectors",  # Changing what events are logged
    ],
    "cloudwatch": [
        "aws cloudwatch delete-alarms",  # Deleting security alarms
        "aws cloudwatch disable-alarm-actions",  # Disabling alarm actions
        "aws cloudwatch delete-dashboards",  # Deleting monitoring dashboards
    ],
    "config": [
        "aws configservice delete-configuration-recorder",  # Deleting config recording
        "aws configservice stop-configuration-recorder",  # Stopping config recording
        "aws configservice delete-delivery-channel",  # Deleting config delivery
        "aws configservice delete-remediation-configuration",  # Deleting auto-remediation
    ],
    "guardduty": [
        "aws guardduty delete-detector",  # Deleting threat detection
        "aws guardduty disable-organization-admin-account",  # Disabling central security
        "aws guardduty update-detector",  # Modifying threat detection
    ],
    # Network & Data security
    "ec2": [
        "aws ec2 authorize-security-group-ingress",  # Opening inbound network access
        "aws ec2 authorize-security-group-egress",  # Opening outbound network access
        "aws ec2 modify-instance-attribute",  # Changing security attributes
        "aws ec2 terminate-instances",  # Terminating instances
        "aws ec2 stop-instances",  # Stopping instances
    ],
    "s3": [
        "aws s3api put-bucket-policy",  # Changing bucket permissions
        "aws s3api put-bucket-acl",  # Changing bucket ACLs
        "aws s3api delete-bucket-policy",  # Removing bucket policy protections
        "aws s3api delete-bucket-encryption",  # Removing encryption
        "aws s3api put-public-access-block",  # Changing public access settings
    ],
}

# Dictionary of safe patterns that override dangerous commands
# These patterns explicitly allow read-only operations that are needed for normal use
SAFE_PATTERNS: Dict[str, List[str]] = {
    # Universal safe patterns for any AWS service
    "general": [
        "--help",  # All help commands are safe
        "help",  # All help subcommands are safe
        "--version",  # Version information is safe
        "--dry-run",  # Dry run operations don't make changes
    ],
    # Identity and Access Management
    "iam": [
        "aws iam get-",  # Read-only IAM operations
        "aws iam list-",  # Listing IAM resources
        "aws iam generate-credential-report",  # Generate reports (no security impact)
        "aws iam generate-service-last-accessed-details",  # Generate access reports
        "aws iam simulate-custom-policy",  # Policy simulation (no changes)
        "aws iam simulate-principal-policy",  # Policy simulation (no changes)
    ],
    # Security, Identity & Compliance services
    "organizations": [
        "aws organizations describe-",  # Read-only Organizations operations
        "aws organizations list-",  # Listing Organization resources
    ],
    "sts": [
        "aws sts get-caller-identity",  # Checking current identity (safe)
        "aws sts decode-authorization-message",  # Decoding error messages (safe)
    ],
    "secretsmanager": [
        "aws secretsmanager get-",  # Reading secrets (note: still sensitive)
        "aws secretsmanager list-",  # Listing secrets
        "aws secretsmanager describe-",  # Reading metadata about secrets
    ],
    "kms": [
        "aws kms describe-",  # Reading key metadata
        "aws kms get-",  # Getting key information
        "aws kms list-",  # Listing keys
    ],
}


def is_service_command_safe(command: str, service: str) -> bool:
    """Check if a command is explicitly safe despite matching dangerous patterns.
    
    Args:
        command: The command to check
        service: The AWS service name
        
    Returns:
        True if the command is safe, False otherwise
    """
    # Check general safe patterns that apply to all services
    for pattern in SAFE_PATTERNS.get("general", []):
        if pattern in command:
            return True
    
    # Check service-specific safe patterns
    for pattern in SAFE_PATTERNS.get(service, []):
        if command.startswith(pattern):
            return True
    
    return False


def check_regex_rules(command: str, service: str) -> Optional[str]:
    """Check command against regex security rules.
    
    Args:
        command: The command to check
        service: The AWS service name
        
    Returns:
        Error message if the command is dangerous, None otherwise
    """
    # Check for command injection attempts (pipe, semicolon, etc.)
    command_injection_pattern = r'[;&|]'
    # Exclude pipes within quotes
    in_single_quote = False
    in_double_quote = False
    escaped = False
    
    for i, char in enumerate(command):
        # Handle escape sequences
        if char == "\\" and not escaped:
            escaped = True
            continue
            
        if not escaped:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char in [';', '&'] and not in_single_quote and not in_double_quote:
                return f"Command contains potentially dangerous character: '{char}'"
                
        escaped = False
    
    # Check for AWS specific security concerns
    if re.search(r'(--no-verify-ssl|--no-paginate)', command):
        return "Security bypass options like --no-verify-ssl are not allowed"
    
    # Check for IAM permissions
    if service == "iam" and re.search(r'iam\s+(add|attach|create|put|update)-.*permission', command):
        return "Modifying IAM permissions is restricted for security reasons"
    
    # More specific rules for s3
    if service == "s3" and re.search(r's3(api)?\s+(put|delete)-bucket-(policy|acl)', command):
        if not re.search(r'--dry-run', command):
            return "Modifying S3 bucket policies or ACLs requires --dry-run for validation"
    
    # Check for known dangerous substrings
    dangerous_terms = [
        "credent", "password", "secret", "token", "key",
        "auth", "admin", "root", "disable-", "delete-", 
        "remove-", "stop-", "terminate-"
    ]
    
    if service not in ["secretsmanager", "kms"] and any(term in command.lower() for term in dangerous_terms):
        return f"Command contains potentially sensitive operations involving: {[term for term in dangerous_terms if term in command.lower()]}"
    
    return None


def validate_aws_command(command: str) -> None:
    """Validate that the command is a proper AWS CLI command.
    
    Args:
        command: The AWS CLI command to validate
        
    Raises:
        ValueError: If the command is invalid
    """
    logger.debug(f"Validating AWS command: {command}")
    
    # Skip validation in permissive mode
    if SECURITY_MODE.lower() == "permissive":
        logger.warning(f"Running in permissive security mode, skipping validation for: {command}")
        return
        
    # Basic validation
    cmd_parts = shlex.split(command)
    if not cmd_parts or cmd_parts[0].lower() != "aws":
        raise ValueError("Commands must start with 'aws'")
        
    if len(cmd_parts) < 2:
        raise ValueError("Command must include an AWS service (e.g., aws s3)")
        
    # Get the service from the command
    service = cmd_parts[1].lower()
    
    # Check regex rules first (these apply regardless of service)
    error_message = check_regex_rules(command, service)
    if error_message:
        raise ValueError(error_message)
        
    # Check against dangerous commands for this service
    if service in DANGEROUS_COMMANDS:
        # Check each dangerous command pattern
        for dangerous_cmd in DANGEROUS_COMMANDS[service]:
            if command.startswith(dangerous_cmd):
                # If it's a dangerous command, check if it's also in safe patterns
                if is_service_command_safe(command, service):
                    return  # Command is safe despite matching dangerous pattern
                    
                # Command is dangerous, raise an error
                raise ValueError(
                    f"This command ({dangerous_cmd}) is restricted for security reasons. "
                    f"Please use a more specific, read-only command or add 'help' or '--help' to see available options."
                )
                
    logger.debug(f"Command validation successful: {command}")


def validate_pipe_command(pipe_command: str) -> None:
    """Validate a command that contains pipes.
    
    This checks both AWS CLI commands and Unix commands within a pipe chain.
    
    Args:
        pipe_command: The piped command to validate
        
    Raises:
        ValueError: If any command in the pipe is invalid
    """
    logger.debug(f"Validating pipe command: {pipe_command}")
    
    # Skip validation in permissive mode
    if SECURITY_MODE.lower() == "permissive":
        logger.warning(f"Running in permissive security mode, skipping validation for: {pipe_command}")
        return
        
    commands = split_pipe_command(pipe_command)
    
    if not commands:
        raise ValueError("Empty command")
        
    # First command must be an AWS CLI command
    validate_aws_command(commands[0])
    
    # Subsequent commands should be valid Unix commands
    for i, cmd in enumerate(commands[1:], 1):
        cmd_parts = shlex.split(cmd)
        if not cmd_parts:
            raise ValueError(f"Empty command at position {i} in pipe")
            
        if not validate_unix_command(cmd):
            raise ValueError(f"Command '{cmd_parts[0]}' at position {i} in pipe is not allowed. Only AWS commands and basic Unix utilities are permitted.")
            
    logger.debug(f"Pipe command validation successful: {pipe_command}")
