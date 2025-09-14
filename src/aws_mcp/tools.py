#!/usr/bin/env python3
"""
AWS MCP Tools Module

This module provides utilities for command execution, natural language processing,
and piped commands for the AWS MCP server.
"""

import asyncio
import logging
import re
import shlex
from typing import Dict, List, Optional, TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aws-mcp-tools")

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


# Natural language to AWS CLI command mappings
NL_COMMAND_MAPPINGS = {
    # General AWS
    "who am i": "aws sts get-caller-identity",
    "caller id": "aws sts get-caller-identity",
    "account info": "aws sts get-caller-identity",
    "show my account": "aws sts get-caller-identity",
    "show my identity": "aws sts get-caller-identity",
    
    # IAM
    "list users": "aws iam list-users",
    "show users": "aws iam list-users",
    "get users": "aws iam list-users",
    "users": "aws iam list-users",
    "list roles": "aws iam list-roles",
    "show roles": "aws iam list-roles",
    "get roles": "aws iam list-roles",
    "roles": "aws iam list-roles",
    "list groups": "aws iam list-groups",
    "show groups": "aws iam list-groups",
    "get groups": "aws iam list-groups",
    "groups": "aws iam list-groups",
    
    # S3
    "list buckets": "aws s3api list-buckets",
    "show buckets": "aws s3api list-buckets",
    "get buckets": "aws s3api list-buckets",
    "buckets": "aws s3api list-buckets",
    "list s3": "aws s3api list-buckets",
    
    # EC2
    "list instances": "aws ec2 describe-instances",
    "show instances": "aws ec2 describe-instances",
    "get instances": "aws ec2 describe-instances",
    "instances": "aws ec2 describe-instances",
    "list ec2": "aws ec2 describe-instances",
    "list vpcs": "aws ec2 describe-vpcs",
    "show vpcs": "aws ec2 describe-vpcs",
    "get vpcs": "aws ec2 describe-vpcs",
    "vpcs": "aws ec2 describe-vpcs",
    "list security groups": "aws ec2 describe-security-groups",
    "show security groups": "aws ec2 describe-security-groups",
    "get security groups": "aws ec2 describe-security-groups",
    "security groups": "aws ec2 describe-security-groups",
    
    # Lambda
    "list functions": "aws lambda list-functions",
    "show functions": "aws lambda list-functions",
    "get functions": "aws lambda list-functions",
    "functions": "aws lambda list-functions",
    "list lambda": "aws lambda list-functions",
    
    # RDS
    "list databases": "aws rds describe-db-instances",
    "show databases": "aws rds describe-db-instances",
    "get databases": "aws rds describe-db-instances",
    "databases": "aws rds describe-db-instances",
    "list rds": "aws rds describe-db-instances",
}


def validate_unix_command(command: str) -> bool:
    """Validate that a command is an allowed Unix command.
    
    Args:
        command: The Unix command to validate
        
    Returns:
        True if the command is valid, False otherwise
    """
    cmd_parts = shlex.split(command)
    if not cmd_parts:
        return False
        
    # Check if the command is in the allowed list
    return cmd_parts[0] in ALLOWED_UNIX_COMMANDS


def is_pipe_command(command: str) -> bool:
    """Check if a command contains a pipe operator.
    
    Args:
        command: The command to check
        
    Returns:
        True if the command contains a pipe operator, False otherwise
    """
    # Check for pipe operator that's not inside quotes
    in_single_quote = False
    in_double_quote = False
    escaped = False
    
    for char in command:
        # Handle escape sequences
        if char == "\\" and not escaped:
            escaped = True
            continue
            
        if not escaped:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == "|" and not in_single_quote and not in_double_quote:
                return True
                
        escaped = False
        
    return False


def split_pipe_command(pipe_command: str) -> List[str]:
    """Split a piped command into individual commands.
    
    Args:
        pipe_command: The piped command string
        
    Returns:
        List of individual command strings
    """
    commands = []
    current_command = ""
    in_single_quote = False
    in_double_quote = False
    escaped = False
    
    for char in pipe_command:
        # Handle escape sequences
        if char == "\\" and not escaped:
            escaped = True
            current_command += char
            continue
            
        if not escaped:
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current_command += char
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current_command += char
            elif char == "|" and not in_single_quote and not in_double_quote:
                commands.append(current_command.strip())
                current_command = ""
            else:
                current_command += char
        else:
            # Add the escaped character
            current_command += char
            escaped = False
            
    if current_command.strip():
        commands.append(current_command.strip())
        
    return commands


def interpret_natural_language(query: str) -> Optional[str]:
    """
    Interpret natural language query and convert to AWS CLI command.
    
    Args:
        query: Natural language query
        
    Returns:
        AWS CLI command or None if can't interpret
    """
    # Clean up query
    query = query.strip().lower()
    
    # Remove common filler words
    query = re.sub(r'^(please|can you|could you|would you|i want to|i need to|i would like to)\s+', '', query)
    query = re.sub(r'\s+for me$', '', query)
    
    # Check direct command mappings
    for key, command in NL_COMMAND_MAPPINGS.items():
        if key in query:
            return command
    
    # Try to extract service and action
    # Example: "list all lambda functions" -> "aws lambda list-functions"
    service_match = re.search(r"(s3|ec2|lambda|iam|rds|dynamodb|cloudformation|sts)", query)
    if service_match:
        service = service_match.group(1)
        
        # Known action mappings
        actions = {
            "list": "list",
            "show": "list",
            "get": "list",
            "describe": "describe"
        }
        
        # Resources by service
        resources = {
            "s3": "buckets",
            "ec2": "instances",
            "lambda": "functions",
            "iam": "users",
            "rds": "instances", 
            "dynamodb": "tables",
            "cloudformation": "stacks",
            "sts": "identity"
        }
        
        for action_key, action_value in actions.items():
            if action_key in query:
                # Special case for S3
                if service == "s3":
                    return f"aws s3api list-buckets"
                
                # Special case for STS
                if service == "sts" and ("identity" in query or "caller" in query or "who am i" in query):
                    return "aws sts get-caller-identity"
                    
                resource = resources.get(service, "")
                
                # Special case for EC2 describe commands
                if service == "ec2":
                    action_value = "describe"
                    
                    # Check for specific resources
                    if "vpc" in query:
                        resource = "vpcs"
                    elif "security group" in query:
                        resource = "security-groups"
                    elif "instance" in query:
                        resource = "instances"
                
                return f"aws {service} {action_value}-{resource}"
    
    # No interpretation found
    return None
