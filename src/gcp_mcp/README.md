# GCP MCP - Model Context Protocol for gcloud CLI

A secure implementation of Model Context Protocol (MCP) for gcloud CLI commands, providing command validation, security checks, and natural language processing.

## Overview

The GCP MCP module provides:

- **Secure Command Execution**: Validates gcloud/gsutil commands before execution
- **Security Analysis**: Detects potentially dangerous commands
- **Natural Language Processing**: Convert natural language queries to gcloud commands
- **Pipe Command Support**: Handle piped commands with Unix utilities
- **Project Management**: Handle GCP project context and switching

## Architecture

### Components

- **client.py**: `GCPMCPClient` - Client interface for executing commands
- **server.py**: `execute_gcp_command()` - Core command execution
- **tools.py**: Utilities for natural language processing and command parsing
- **security.py**: Command validation and security checks

### Command Flow

```
User Input
    ↓
interpret_natural_language() - Convert NL to gcloud command
    ↓
validate_gcp_command() - Security validation
    ↓
execute_gcp_command() - Run command
    ↓
Process output (JSON parsing, truncation)
    ↓
Return result
```

## Usage

### Programmatic API

```python
from src.gcp_mcp.client import GCPMCPClient

# Initialize client
client = GCPMCPClient()
client.start(project_id="your-project-id")

# Execute command
result = client.execute_command("gcloud compute instances list")
if result["status"] == "success":
    print(result["output"])

# Natural language support
result = client.execute_command("list my instances")
print(result["output"])

# Cleanup
client.stop()
```

### Command Line Interface

```bash
# Interactive mode
python -m src.gcp_mcp

# Execute single command
python -m src.gcp_mcp --command "gcloud compute instances list"

# Specify project
python -m src.gcp_mcp --project "your-project-id"

# Verbose logging
python -m src.gcp_mcp --verbose
```

## Supported Natural Language Queries

### Project & Account Management
- "who am i" → `gcloud auth list`
- "current project" → `gcloud config get-value project`
- "list projects" → `gcloud projects list`

### Compute Engine
- "list instances" → `gcloud compute instances list`
- "list vms" → `gcloud compute instances list`
- "list images" → `gcloud compute images list`

### Cloud Storage
- "list buckets" → `gsutil ls`
- "list storage" → `gsutil ls`

### Cloud SQL
- "list sql instances" → `gcloud sql instances list`
- "list databases" → `gcloud sql databases list`

### Networking
- "list networks" → `gcloud compute networks list`
- "list firewalls" → `gcloud compute firewall-rules list`
- "list routes" → `gcloud compute routes list`

### Other Services
- "list clusters" → `gcloud container clusters list`
- "list functions" → `gcloud functions list`
- "list services" → `gcloud services list`

## Security Features

### Command Validation

Commands are validated to prevent dangerous operations:

- **Read-only commands**: Safe - `list`, `show`, `describe`, `get`, `export`
- **Dangerous commands**: Blocked in strict mode
  - IAM creation/deletion
  - Project deletion
  - Secret deletion
  - Logging modifications
  - Firewall rule changes
  - Compute resource deletion
  - Storage deletion

### Risk Levels

Commands are classified by risk:
- **safe**: Read-only operations
- **low**: Non-destructive operations
- **medium**: Potentially risky changes (updates, deletes)
- **high**: Critical operations (secrets, logs)
- **critical**: IAM and project changes

### Security Mode

- **strict**: Dangerous commands are blocked
- **permissive**: Dangerous commands are allowed with warnings

## Command Examples

### Safe Commands (Read-only)

```bash
gcloud projects list
gcloud compute instances list
gcloud storage buckets list
```

### Dangerous Commands (Blocked)

```bash
gcloud iam service-accounts create  # Creating service accounts
gcloud projects delete  # Deleting projects
gcloud secrets delete  # Destroying secrets
```

## Error Handling

### Authentication Errors

```
Error: Authentication error. Please run 'gcloud auth login' to authenticate.
```

### Command Not Found

```
Error: Could not interpret command: ...
Please use gcloud CLI syntax (gcloud command) or try a different natural language query.
```

### Timeout

```
Error: Command timed out after 30 seconds
```

## Configuration

### Environment Variables

- `GCP_PROJECT`: Default GCP project ID
- `GOOGLE_CLOUD_PROJECT`: Alternative GCP project ID

### Constants

- `DEFAULT_TIMEOUT`: 30 seconds
- `MAX_OUTPUT_SIZE`: 1MB (output truncated if larger)

## Integration

### With GCP Security Agent

```python
from src.gcp_mcp.client import GCPMCPClient
from src.agents.gcp_security.agent import GCPSecurityAgent

client = GCPMCPClient()
client.start()

# Execute CLI commands for security analysis
result = client.execute_command("gcloud compute instances list")

# Use with security agent
agent = GCPSecurityAgent()
# Combine MCP output with agent analysis
```

## Limitations

- Single project context per session
- Output limited to 1MB
- Commands timeout after 30 seconds
- Requires gcloud CLI v350+

## Future Enhancements

- [ ] Multi-project support
- [ ] Command result caching
- [ ] Custom command aliases
- [ ] Output format options (JSON, CSV, table)
- [ ] Async command execution
- [ ] Command history and logging
- [ ] Custom security policies

## See Also

- [gcloud CLI Documentation](https://cloud.google.com/sdk/gcloud)
- [Azure MCP Implementation](../azure_mcp/) - Similar implementation
- [AWS MCP Implementation](../aws_mcp/) - Reference implementation
