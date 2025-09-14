#!/usr/bin/env python3
"""
Test script for the SecurityPoisoningAgent to verify it works correctly with file paths.
"""

import os
import sys
from src.agents.security_analyzer.agent import SecurityPoisoningAgent

def main():
    print("Testing SecurityPoisoningAgent...")
    
    # Create agent
    agent = SecurityPoisoningAgent()
    
    # Test file path
    test_file = "data/test_config.json"
    
    # Check if file exists
    if not os.path.exists(test_file):
        print(f"Error: Test file {test_file} does not exist")
        return
    
    print(f"Analyzing file: {test_file}")
    
    # Try to analyze the file
    try:
        results = agent.analyze_file(test_file)
        print("\nAnalysis results:")
        print(f"Success: {results.get('success', False)}")
        print(f"File path: {results.get('file_path', 'N/A')}")
        print(f"Format type: {results.get('format_type', 'N/A')}")
        print(f"Risk level: {results.get('risk_level', 'N/A')}")
        print(f"Poisoning detected: {results.get('poisoning_detected', False)}")
        
        if results.get('poisoning_detected', False):
            print(f"\nFound {len(results.get('findings', []))} issues:")
            for i, finding in enumerate(results.get('findings', []), 1):
                print(f"{i}. {finding.get('type')}: {finding.get('matched_text')}")
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
