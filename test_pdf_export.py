# test_pdf_export.py
"""
Simple script to demonstrate the PDF export functionality of the security analyzer.
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
    
    print("PDF Export Demo:")
    print("1. Run the following commands in the security analyzer CLI:")
    print("   - analyze data/test_config.json --pdf")
    print("   - scan data/ --pdf")
    print("   - compare data/test_config.json data/test_config.json --pdf")
    print("2. Check the 'reports/' directory for the generated PDF files")
    
    # Run the CLI app
    app()

if __name__ == "__main__":
    main()
