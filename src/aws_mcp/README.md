# AWS Model Context Protocol (MCP) Module

A secure, Pythonic implementation of the Model Context Protocol for executing AWS CLI commands with built-in natural language understanding.

## Overview

The AWS MCP module provides a secure interface for executing AWS CLI commands programmatically. It includes:

- **Natural Language Processing**: Convert natural language queries to AWS CLI commands
- **Command Validation**: Security checks to prevent dangerous operations
- **Command Execution**: Safely execute AWS CLI commands with proper error handling
- **Piped Commands**: Support for Unix pipes to filter and transform output

## Architecture

The module follows a clean architecture pattern with these key components:

### Client (`client.py`)

The client interface that applications use to interact with the AWS MCP server.

```python
from src.aws_mcp.client import AWSMCPClient

# Initialize the client
client = AWSMCPClient()
client.start(aws_profile="default", aws_region="us-east-1")

# Execute a command
result = client.execute_command("aws s3api list-buckets")
print(result["output"])

# Execute a natural language command
result = client.execute_command("show me my buckets")
print(result["output"])

# Clean up
client.stop()
```

### Server (`server.py`)

The core server implementation that handles command execution and processes results.

- Validates commands for security issues
- Executes AWS CLI commands with proper error handling
- Processes command output for consistent formatting
- Handles timeouts and resource limits

### Tools (`tools.py`)

Utility functions for natural language processing, command validation, and piped commands.

- Natural language to AWS CLI command mappings
- Functions to parse and validate piped commands
- Utilities for working with command output

### Security (`security.py`)

Security validation for AWS CLI commands to prevent dangerous operations.

- Checks for potentially dangerous commands
- Validates command structure and arguments
- Prevents command injection attacks
- Provides safe override patterns for common operations

## Security Features

The AWS MCP module includes several security features:

1. **Command Validation**: All commands are validated before execution to ensure they are safe.
2. **Dangerous Command Detection**: Commands that could pose security risks are blocked.
3. **Command Injection Prevention**: Special characters and patterns are detected and blocked.
4. **Timeout Protection**: Commands have timeouts to prevent resource exhaustion.
5. **Output Size Limits**: Large outputs are truncated to prevent memory issues.
6. **Authentication Error Detection**: Authentication-related errors are clearly identified.

## Natural Language Processing

The module supports converting natural language queries to AWS CLI commands:

- "who am i" → "aws sts get-caller-identity"
- "list my S3 buckets" → "aws s3api list-buckets"
- "show my EC2 instances" → "aws ec2 describe-instances"
- "get IAM users" → "aws iam list-users"

## Usage

### Basic Usage

```python
from src.aws_mcp.client import AWSMCPClient

client = AWSMCPClient()
client.start()

# Execute direct AWS CLI command
result = client.execute_command("aws sts get-caller-identity")
print(result["output"])

# Execute natural language command
result = client.execute_command("show my buckets")
print(result["output"])

client.stop()
```

### Command Line Interface

The module also provides a simple command-line interface:

```bash
# Direct execution
python -m src.aws_mcp --command "aws sts get-caller-identity"

# Interactive mode
python -m src.aws_mcp
```

## Integration with AWS Security Agent

The AWS MCP module is designed to be used with the AWS Security Agent, which adds Gemini LLM-powered security analysis:

```python
from aws_security_agent import AWSSecurityAgent

agent = AWSSecurityAgent()
agent.start()

# Execute command with LLM analysis
result = agent.execute_with_analysis("aws ec2 describe-security-groups")
print(result["analysis"])

agent.stop()
```

## Requirements

- Python 3.8+
- AWS CLI installed and configured
- Valid AWS credentials

## Security Considerations

- Commands are validated before execution
- Destructive commands (delete, remove, terminate) are blocked by default
- Command injection attempts are detected and rejected
- Set SECURITY_MODE to "permissive" to disable command validation (not recommended)
