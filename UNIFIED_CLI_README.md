# Cloud Security Assistant

A unified chatbot interface for cloud security operations, similar to GitHub Copilot but specialized for cloud security tasks.

## Features

- **Natural Language Understanding**: Communicate with security tools using natural language
- **Multi-Agent Architecture**: Seamlessly switch between specialized security agents
- **Contextual Mode Detection**: Automatically selects the appropriate agent based on your query
- **Interactive CLI Interface**: Rich terminal interface with color-coded output and formatting

## Available Agents

### 1. AWS Security Agent
AWS security monitoring and remediation using AWS CLI commands through natural language.

### 2. Security Analyzer
Detects security poisoning and malicious tampering in compliance configurations and benchmarks.

### 3. Compliance Chat
Answers questions about cloud security compliance standards, regulations, and best practices.

### 4. Article Search
Finds relevant security articles and publications by specific authors or topics.

### 5. General Assistant
Answers general cloud security questions and helps with navigating the system.

## Usage

### Running the Assistant

```bash
./run_assistant.sh
```

Or directly:

```bash
python main_cli.py
```

### Commands

- `switch to aws` - Switch to AWS Security Agent mode
- `switch to security` - Switch to Security Analyzer mode 
- `switch to compliance` - Switch to Compliance Chat mode
- `switch to article` - Switch to Article Search mode
- `switch to general` - Switch to General Assistant mode
- `clear` or `cls` - Clear the screen
- `help` or `?` - Display help information
- `exit` or `quit` - Exit the application

### Examples

```
aws> List all S3 buckets with public access
security> Analyze data/test_config.json
compliance> What are the CIS benchmarks for AWS?
article> Find articles by John Smith about cloud security
general> How do I secure my AWS Lambda functions?
```

## Requirements

- Python 3.8+
- Google Vertex AI API key or credentials file
- AWS CLI configured for AWS Security Agent
- Required Python packages (see requirements.txt)

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv cloudagent
   source cloudagent/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure credentials:
   - Place Google Vertex AI credentials in `config/vertex.json`
   - Set up AWS CLI credentials

4. Run the assistant:
   ```bash
   ./run_assistant.sh
   ```

## Architecture

The Cloud Security Assistant is built on a unified interface that delegates queries to specialized agents:

1. **Input Processing**: Natural language input is analyzed to determine intent
2. **Agent Selection**: The appropriate specialized agent is selected based on the query
3. **Command Execution**: The selected agent processes the command and returns results
4. **Response Formatting**: Results are formatted for display with rich text formatting

## License

This project is proprietary and confidential. All rights reserved.

## Author

KishhCodes
