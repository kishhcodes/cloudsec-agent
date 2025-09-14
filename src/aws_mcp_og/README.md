# AWS MCP OG (Original)

A lightweight Model Context Protocol implementation for securely executing AWS CLI commands.

## Overview

The AWS MCP OG package provides a simplified implementation of the Model Context Protocol for executing AWS CLI commands in a controlled environment. It's designed to be easy to integrate and use with AI assistants that need to interact with AWS services.

## Features

- **AWS CLI command execution**: Execute AWS CLI commands securely
- **Command validation**: Validate commands before execution to prevent dangerous operations
- **Natural language processing**: Interpret natural language queries as AWS CLI commands
- **Command piping**: Support for piping AWS CLI output to Unix commands
- **Timeout handling**: Prevent long-running commands from consuming resources

## Usage

### As a library

```python
from src.aws_mcp_og.tools import interpret_natural_language, execute_aws_command

# Interpret natural language as AWS CLI command
command = interpret_natural_language("show my S3 buckets")
print(f"Interpreted as: {command}")  # aws s3api list-buckets

# Execute an AWS CLI command
result = execute_aws_command("aws sts get-caller-identity")
print(result)
```

### Using AWS Security Agent OG

```bash
# Activate virtual environment
source cloudagent/bin/activate

# Run the interactive agent
python aws_security_agent_og.py
```

## Security Considerations

- Commands are validated before execution to prevent dangerous operations
- Timeouts prevent resource exhaustion
- Natural language processing helps reduce the risk of typos in commands

## Components

- **tools.py**: Core utilities for command execution and validation
- **aws_security_agent_og.py**: Interactive CLI for AWS security analysis with Gemini LLM

## License

MIT
