"""GCP MCP Module

This module provides a Model Context Protocol (MCP) implementation for Google Cloud CLI (gcloud) commands,
allowing secure command execution, validation, and natural language processing.
"""

__version__ = "0.1.0"

# Expose key functionality at the module level
from .client import GCPMCPClient
from .server import execute_gcp_command
from .tools import interpret_natural_language
from .security import validate_gcp_command, validate_pipe_command
