# security_analyzer_cli.py
"""
CLI interface for the Security Poisoning Analyzer.
This script provides a command-line interface for detecting security
poisoning in compliance configurations and benchmarks.
"""

import os
import sys
from dotenv import load_dotenv
from src.agents.security_analyzer.cli import app

def main():
    # Load environment variables
    load_dotenv()
    
    # Set Google application credentials if available
    if os.path.exists("config/vertex.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"
    
    # Run the CLI app
    app()

if __name__ == "__main__":
    main()
