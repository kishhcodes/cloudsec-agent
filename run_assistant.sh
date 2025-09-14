#!/bin/bash
# Run the unified cloud security assistant

# Activate virtual environment if it exists
if [ -d "cloudagent" ]; then
    source cloudagent/bin/activate
fi

# Set Google credentials if available
if [ -f "config/vertex.json" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="config/vertex.json"
fi

# Run the main CLI
python main_cli.py

# Handle exit
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "Error: Cloud Security Assistant exited with code $exit_code"
    exit $exit_code
fi
