# Security Poisoning Analyzer

This tool helps detect and analyze potential security poisoning in cloud compliance configurations, benchmarks, and security policies. Security poisoning refers to malicious modifications that introduce vulnerabilities or backdoors while appearing legitimate.

## Features

- **File Analysis**: Detect security poisoning in individual configuration files
- **Directory Scanning**: Recursively scan directories for vulnerable configurations
- **Benchmark Analysis**: Check compliance benchmarks for signs of tampering
- **Configuration Comparison**: Compare configurations to detect malicious drift
- **Natural Language Interface**: Ask questions about security poisoning and get expert answers

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Google API Key for Gemini (set as environment variable `GOOGLE_API_KEY`)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Google API key:
   ```bash
   export GOOGLE_API_KEY=your_api_key_here
   ```
   Or create a `.env` file with `GOOGLE_API_KEY=your_api_key_here`

### Usage

Run the CLI:

```bash
python security_analyzer_cli.py
```

Or import the agent in your code:

```python
from src.agents.security_analyzer.agent import SecurityPoisoningAgent

agent = SecurityPoisoningAgent()
results = agent.analyze_file("path/to/config.json")
print(agent.generate_summary(results))
```

## CLI Commands

- `analyze {file_path}` - Analyze a specific file for security poisoning
- `benchmark {file_path}` - Check a benchmark document for tampering
- `compare {current_file} {reference_file}` - Compare configurations to detect drift
- `scan {directory} [--no-recursive]` - Scan a directory for vulnerable configurations
- `clear` or `cls` - Clear the screen
- `exit` or `quit` - End the session

You can also ask natural language questions about security poisoning.

## Detection Capabilities

- AWS IAM backdoors
- Excessive permissions
- Encryption weaknesses
- Credential exposure
- Suspicious benchmark modifications
- Configuration drift
- And more...

## Examples

### Analyzing a Configuration File

```
Security> analyze data/configs/aws-config.json
```

### Scanning a Directory

```
Security> scan data/configs --no-recursive
```

### Comparing Configurations

```
Security> compare data/configs/current.json data/configs/baseline.json
```

### Asking About Security Poisoning

```
Security> What is compliance poisoning and how can I detect it?
```

## License

This project is proprietary and confidential. All rights reserved.
