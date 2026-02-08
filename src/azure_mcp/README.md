# Azure MCP - Model Context Protocol for Azure CLI

A secure implementation of Model Context Protocol (MCP) for Azure CLI commands, providing command validation, security checks, and natural language processing.

## Overview

The Azure MCP module provides:

- **Secure Command Execution**: Validates Azure CLI commands before execution
- **Security Analysis**: Detects potentially dangerous commands
- **Natural Language Processing**: Convert natural language queries to Azure CLI commands
- **Pipe Command Support**: Handle piped commands with Unix utilities
- **Authentication Management**: Handle Azure login and subscription context

## Architecture

### Components

- **client.py**: `AzureMCPClient` - Client interface for executing commands
- **server.py**: `execute_azure_command()` - Core command execution
- **tools.py**: Utilities for natural language processing and command parsing
- **security.py**: Command validation and security checks

### Command Flow

```
User Input
    ↓
interpret_natural_language() - Convert NL to Azure CLI
    ↓
validate_azure_command() - Security validation
    ↓
execute_azure_command() - Run command
    ↓
Process output (JSON parsing, truncation)
    ↓
Return result
```

## Usage

### Programmatic API

```python
from src.azure_mcp.client import AzureMCPClient

# Initialize client
client = AzureMCPClient()
client.start(subscription_id="your-subscription-id")

# Execute command
result = client.execute_command("az account show")
if result["status"] == "success":
    print(result["output"])

# Natural language support
result = client.execute_command("list my subscriptions")
print(result["output"])

# Cleanup
client.stop()
```

### Command Line Interface

```bash
# Interactive mode
python -m src.azure_mcp

# Execute single command
python -m src.azure_mcp --command "az account show"

# Specify subscription
python -m src.azure_mcp --subscription "your-subscription-id"

# Verbose logging
python -m src.azure_mcp --verbose
```

## Supported Natural Language Queries

### Account & Subscription
- "who am i" → `az account show`
- "list subscriptions" → `az account list`
- "show resources" → `az resource list`

### Identity & Access
- "list users" → `az ad user list`
- "list roles" → `az role definition list`
- "list groups" → `az ad group list`

### Storage
- "list storage accounts" → `az storage account list`
- "list containers" → `az storage container list`

### Virtual Machines
- "list vms" → `az vm list`
- "list virtual machines" → `az vm list`

### Network
- "list vnets" → `az network vnet list`
- "list network security groups" → `az network nsg list`
- "list vpn gateways" → `az network vpn-gateway list`

### Databases
- "list sql servers" → `az sql server list`
- "list databases" → `az sql db list`

### Key Vault
- "list key vaults" → `az keyvault list`
- "list secrets" → `az keyvault secret list`

### App Services
- "list web apps" → `az webapp list`

## Security Features

### Command Validation

Commands are validated to prevent dangerous operations:

- **Read-only commands**: Safe - `list`, `show`, `get`, `describe`
- **Dangerous commands**: Blocked in strict mode
  - Identity creation/deletion
  - Secret/key deletion
  - Logging/audit trail modifications
  - Firewall rule changes
  - Database/storage deletion

### Risk Levels

Commands are classified by risk:
- **safe**: Read-only operations
- **low**: Non-destructive modifications
- **medium**: Potentially risky changes
- **high**: Critical security operations
- **critical**: Identity and access changes

### Security Mode

- **strict**: Dangerous commands are blocked
- **permissive**: Dangerous commands are allowed with warnings

## Command Examples

### Safe Commands (Read-only)

```bash
az account show
az group list
az vm list
az storage account list
```

### Dangerous Commands (Blocked)

```bash
az ad user create  # Creating users
az role assignment create  # Privilege escalation
az keyvault secret delete  # Destroying secrets
az sql db delete  # Data destruction
```

## Error Handling

### Authentication Errors

```
Error: Authentication error. Please run 'az login' to authenticate.
```

### Command Not Found

```
Error: Could not interpret command: ...
Please use Azure CLI syntax (az command) or try a different natural language query.
```

### Timeout

```
Error: Command timed out after 30 seconds
```

## Configuration

### Environment Variables

- `AZURE_SUBSCRIPTION_ID`: Default subscription ID
- `AZURE_TENANT_ID`: Default tenant ID

### Constants

- `DEFAULT_TIMEOUT`: 30 seconds
- `MAX_OUTPUT_SIZE`: 1MB (output truncated if larger)

## Integration

### With Azure Security Agent

```python
from src.azure_mcp.client import AzureMCPClient
from src.agents.azure_security.agent import AzureSecurityAgent

client = AzureMCPClient()
client.start()

# Execute CLI commands for security analysis
result = client.execute_command("az vm list")

# Use with security agent
agent = AzureSecurityAgent()
# Combine MCP output with agent analysis
```

## Limitations

- Single subscription context per session
- Output limited to 1MB
- Commands timeout after 30 seconds
- Requires Azure CLI v2.40+

## Future Enhancements

- [ ] Multi-subscription support
- [ ] Command result caching
- [ ] Custom command aliases
- [ ] Output format options (JSON, CSV, table)
- [ ] Async command execution
- [ ] Command history and logging
- [ ] Custom security policies

## See Also

- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/)
- [AWS MCP Implementation](../aws_mcp/) - Reference implementation
