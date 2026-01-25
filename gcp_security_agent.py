#!/usr/bin/env python3
"""
Standalone Google Cloud Platform Security Agent

Run this script to launch the GCP-specific security analysis interface.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.gcp_security.cli import main

if __name__ == "__main__":
    main()
