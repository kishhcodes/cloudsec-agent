#!/usr/bin/env python3
"""
Test script to verify if the SecurityPoisoningAgent can handle both relative and absolute paths.
"""

import os
import sys
from src.agents.security_analyzer.agent import SecurityPoisoningAgent

def main():
    print("Testing path handling in SecurityPoisoningAgent...")
    
    # Create agent
    agent = SecurityPoisoningAgent()
    
    # Test file paths
    relative_path = "test_weak_config.json"
    absolute_path = os.path.abspath(relative_path)
    
    print(f"Relative path: {relative_path}")
    print(f"Absolute path: {absolute_path}")
    
    # Check if file exists at both paths
    if not os.path.exists(relative_path):
        print(f"Error: Test file {relative_path} does not exist")
        return
    
    if not os.path.exists(absolute_path):
        print(f"Error: Test file {absolute_path} does not exist")
        return
    
    # Test with relative path
    print("\nTesting with relative path...")
    try:
        rel_results = agent.analyze_file(relative_path)
        print(f"Success: {rel_results.get('success', False)}")
        print(f"Error: {rel_results.get('error', 'None')}")
        print(f"File path in results: {rel_results.get('file_path', 'N/A')}")
    except Exception as e:
        print(f"Error with relative path: {str(e)}")
    
    # Test with absolute path
    print("\nTesting with absolute path...")
    try:
        abs_results = agent.analyze_file(absolute_path)
        print(f"Success: {abs_results.get('success', False)}")
        print(f"Error: {abs_results.get('error', 'None')}")
        print(f"File path in results: {abs_results.get('file_path', 'N/A')}")
    except Exception as e:
        print(f"Error with absolute path: {str(e)}")

if __name__ == "__main__":
    main()
