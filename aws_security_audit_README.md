# AWS Security Audit Tool

This tool provides command-line utilities to audit AWS environments for security issues.

## Features

- Analyze security configurations
- Detect potential misconfigurations
- Scan for compliance violations
- Generate detailed reports
- Export results as PDF reports

## Components

- `aws_security_audit_cli.py`: Main command-line interface
- `aws_security_audit_launcher.py`: Script to launch the audit tool
- `aws_security_agent.py`: AWS security agent for interactive analysis
- `security_analyzer_cli.py`: Security poisoning analyzer CLI with PDF export

## Usage

```bash
# Run the CLI tool
python aws_security_audit_cli.py

# Or use the launcher script
./run_aws_audit.sh

# Run the security analyzer CLI with PDF export
python security_analyzer_cli.py
```

## Security Analyzer CLI with PDF Export

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

## Requirements

See `requirements.txt` for required Python packages.
