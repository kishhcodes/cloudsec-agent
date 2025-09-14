# AWS Security Agent with MCP OG

A secure AWS CLI assistant powered by Gemini LLM and the AWS MCP OG implementation.

## Overview

This project provides a security-focused AWS CLI assistant that can execute AWS commands securely while providing intelligent analysis of the results. It uses Gemini LLM to interpret natural language queries and analyze AWS configuration data for security issues.

## Features

- **Natural Language Understanding**: Convert natural language queries to AWS CLI commands
- **Secure Command Execution**: Validate and safely execute AWS CLI commands
- **Security Analysis**: Analyze AWS configurations for security issues and compliance
- **Interactive CLI**: User-friendly command-line interface with rich formatting

## Components

### Core AWS MCP Implementation
- **aws_security_agent_og.py**: Main interactive agent with Gemini LLM integration
- **src/aws_mcp_og/**: Core MCP implementation for AWS CLI command execution
  - **tools.py**: Command execution and natural language utilities
  - **security.py**: Command validation and security checks
  - **server.py**: JSON-RPC server implementation
  - **cli_exec.py**: AWS CLI command execution utilities

### Compliance and Security Analysis
- **main.py**: Processes AWS security benchmark PDFs into embeddings for compliance checks
- **src/data_pipeline/**: Utilities for document processing and embedding generation
- **src/agents/**: Specialized security and compliance agents
  - **compliance_bot/**: Compliance verification using RAG with security benchmarks
  - **security_analyzer/**: Detection of security poisoning in compliance frameworks with PDF export
  - **aws_audit/**: AWS infrastructure security auditing

## Setup

1. Create a Python virtual environment:
```bash
python -m venv cloudagent
source cloudagent/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
# Create .env file with your API keys
cp .env.example .env
# Edit the .env file and add your Gemini API key
```

4. Ensure AWS CLI is installed and configured:
```bash
aws configure
```

## Usage

### AWS Command Execution with MCP OG

Run the interactive agent for AWS CLI command execution:

```bash
source cloudagent/bin/activate
python aws_security_agent_og.py
```

Example commands:
- `aws sts get-caller-identity` - Direct AWS CLI command
- `who am i` - Natural language query (interpreted as AWS CLI command)
- `show my S3 buckets` - Natural language query for S3 buckets
- `analyze my EC2 security groups` - Ask for security analysis

### Processing AWS Security Benchmarks

To process AWS security benchmark PDFs and generate embeddings for compliance checks:

```bash
source cloudagent/bin/activate
python main.py
```

This will process PDF files in the `data/raw` directory and generate embeddings in `data/embeddings/index/`.

### Compliance and Security Analysis

For compliance verification and security analysis:

```bash
# Compliance Bot - for checking AWS configurations against best practices
source cloudagent/bin/activate
python -m src.agents.compliance_bot

# Security Analyzer - for detecting security poisoning in compliance frameworks
source cloudagent/bin/activate
python -m src.agents.security_analyzer

# Security Analyzer CLI with PDF export
source cloudagent/bin/activate
python security_analyzer_cli.py
```

## PDF Export Feature

The security analyzer CLI now supports exporting analysis results as PDF reports:

```bash
# Analyze a file and export as PDF
analyze path/to/file --pdf

# Scan a directory and export as PDF
scan path/to/directory --pdf

# Compare two files and export as PDF
compare file1 file2 --pdf

# Analyze a benchmark file and export as PDF
benchmark path/to/benchmark --pdf
```

PDF reports will be saved in the `reports/` directory with a timestamp in the filename.

## Security Considerations

- Commands are validated before execution
- Destructive commands (delete, remove, terminate) are blocked
- Command injection attempts are detected and rejected
- Timeouts prevent resource exhaustion

## Development

### Git Workflow

This repository uses `.gitignore` to manage which files are tracked in version control:

- Core functionality (aws_mcp_og, aws_security_agent_og.py) is tracked
- Agent modules (compliance_bot, security_analyzer) are tracked
- Data pipeline utilities are tracked
- Virtual environments and credentials are excluded
- Generated data (embeddings) is excluded but directory structure is preserved

When making changes, focus on improving the aws_mcp_og implementation and ensuring all agents can work together.

## License

MIT
