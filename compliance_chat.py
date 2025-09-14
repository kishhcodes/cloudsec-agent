#!/usr/bin/env python3
# compliance_chat.py - Main entry point for the Cloud Compliance Chatbot

import os
import sys

# Set environment variable for Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"

# Add project root to Python path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app
from src.agents.compliance_bot.cli import app

if __name__ == "__main__":
    app()
