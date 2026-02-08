"""Azure MCP Module

This module provides a Model Context Protocol (MCP) implementation for Azure CLI commands,
allowing secure command execution, validation, and natural language processing.
"""

__version__ = "0.1.0"

# Expose key functionality at the module level
from .client import AzureMCPClient
from .server import execute_azure_command
from .tools import interpret_natural_language
from .security import validate_azure_command, validate_pipe_command
