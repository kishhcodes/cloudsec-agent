"""Command execution utilities for AWS MCP Server.

This module provides utilities for validating and executing commands, including:
- AWS CLI commands
- Basic Unix commands
- Command pipes (piping output from one command to another)
- Natural language processing for AWS commands
"""

import asyncio
import logging
import shlex
from typing import List, TypedDict

# Define constants for our implementation
DEFAULT_TIMEOUT = 30  # 30 seconds
MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB

# Configure module logger
logger = logging.getLogger(__name__)

# List of allowed Unix commands that can be used in a pipe
ALLOWED_UNIX_COMMANDS = [
    # File operations
    "cat",
    "ls",
    "cd",
    "pwd",
    "cp",
    "mv",
    "rm",
    "mkdir",
    "touch",
    "chmod",
    "chown",
    # Text processing
    "grep",
    "sed",
    "awk",
    "cut",
    "sort",
    "uniq",
    "wc",
    "head",
    "tail",
    "tr",
    "find",
    # System information
    "ps",
    "top",
    "df",
    "du",
    "uname",
    "whoami",
    "date",
    "which",
    "echo",
    # Networking
    "ping",
    "ifconfig",
    "netstat",
    "curl",
    "wget",
    "dig",
    "nslookup",
    "ssh",
    "scp",
    # Other utilities
    "man",
    "less",
    "tar",
    "gzip",
    "gunzip",
    "zip",
    "unzip",
    "xargs",
    "jq",
    "tee",
]


class CommandResult(TypedDict):
    """Type definition for command execution results."""

    status: str
    output: str


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

    for _, char in enumerate(command):
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

    for _, char in enumerate(pipe_command):
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


async def execute_piped_command(pipe_command: str, timeout: int | None = None) -> CommandResult:
    """Execute a command that contains pipes.

    Args:
        pipe_command: The piped command to execute
        timeout: Optional timeout in seconds (defaults to DEFAULT_TIMEOUT)

    Returns:
        CommandResult containing output and status
    """
    # Set timeout
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    logger.debug(f"Executing piped command: {pipe_command}")

    try:
        # Split the pipe_command into individual commands
        commands = split_pipe_command(pipe_command)

        # For each command, split it into command parts for subprocess_exec
        command_parts_list = [shlex.split(cmd) for cmd in commands]

        if len(commands) == 0:
            return CommandResult(status="error", output="Empty command")

        # Execute the first command
        first_cmd = command_parts_list[0]
        first_process = await asyncio.create_subprocess_exec(*first_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        current_process = first_process
        current_stdout = None
        current_stderr = None

        # For each additional command in the pipe, execute it with the previous command's output
        for cmd_parts in command_parts_list[1:]:
            try:
                # Wait for the previous command to complete with timeout
                current_stdout, current_stderr = await asyncio.wait_for(current_process.communicate(), timeout)

                if current_process.returncode != 0:
                    # If previous command failed, stop the pipe execution
                    stderr_str = current_stderr.decode("utf-8", errors="replace")
                    logger.warning(f"Piped command failed with return code {current_process.returncode}: {pipe_command}")
                    logger.debug(f"Command error output: {stderr_str}")
                    return CommandResult(status="error", output=stderr_str or "Command failed with no error output")

                # Create the next process with the previous output as input
                next_process = await asyncio.create_subprocess_exec(
                    *cmd_parts, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                # Pass the output of the previous command to the input of the next command
                stdout, stderr = await asyncio.wait_for(next_process.communicate(input=current_stdout), timeout)

                current_process = next_process
                current_stdout = stdout
                current_stderr = stderr

            except asyncio.TimeoutError:
                logger.warning(f"Piped command timed out after {timeout} seconds: {pipe_command}")
                try:
                    # process.kill() is synchronous, not a coroutine
                    current_process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                return CommandResult(status="error", output=f"Command timed out after {timeout} seconds")

        # Wait for the final command to complete if it hasn't already
        if current_stdout is None:
            try:
                current_stdout, current_stderr = await asyncio.wait_for(current_process.communicate(), timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Piped command timed out after {timeout} seconds: {pipe_command}")
                try:
                    current_process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                return CommandResult(status="error", output=f"Command timed out after {timeout} seconds")

        # Process output
        stdout_str = current_stdout.decode("utf-8", errors="replace")
        stderr_str = current_stderr.decode("utf-8", errors="replace")

        # Truncate output if necessary
        if len(stdout_str) > MAX_OUTPUT_SIZE:
            logger.info(f"Output truncated from {len(stdout_str)} to {MAX_OUTPUT_SIZE} characters")
            stdout_str = stdout_str[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

        if current_process.returncode != 0:
            logger.warning(f"Piped command failed with return code {current_process.returncode}: {pipe_command}")
            logger.debug(f"Command error output: {stderr_str}")
            return CommandResult(status="error", output=stderr_str or "Command failed with no error output")

        return CommandResult(status="success", output=stdout_str)
    except Exception as e:
        logger.error(f"Failed to execute piped command: {str(e)}")
        return CommandResult(status="error", output=f"Failed to execute command: {str(e)}")


# Natural language processing for AWS commands
# Dictionary mapping natural language phrases to AWS CLI commands
NL_COMMAND_MAPPINGS = {
    # Identity and Account
    "caller id": "aws sts get-caller-identity",
    "who am i": "aws sts get-caller-identity",
    "account info": "aws sts get-caller-identity",
    "account information": "aws sts get-caller-identity",
    "my identity": "aws sts get-caller-identity",
    
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

# Function to interpret natural language as AWS CLI commands
def interpret_natural_language(query: str) -> str | None:
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
    import re
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