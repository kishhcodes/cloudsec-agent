"""AWS MCP Module

This module provides a Model Context Protocol (MCP) implementation for AWS CLI commands,
allowing secure command execution, validation, and natural language processing.
"""

__version__ = "0.1.0"

# Expose key functionality at the module level
from .client import AWSMCPClient
from .server import execute_aws_command
from .tools import interpret_natural_language
from .security import validate_aws_command, validate_pipe_command
