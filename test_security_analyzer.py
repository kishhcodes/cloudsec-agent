#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the agent
from src.agents.security_analyzer.agent import SecurityPoisoningAgent

def main():
    # Load environment variables
    load_dotenv()
    
    # Set Google application credentials if available
    if os.path.exists("config/vertex.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"
    
    # Initialize agent
    agent = SecurityPoisoningAgent()
    
    # Analyze test file
    test_file = "test_weak_config.json"
    print(f"Analyzing file: {test_file}")
    
    results = agent.analyze_file(test_file)
    
    # Print results
    print("Analysis Results:")
    print(f"Success: {results.get('success')}")
    print(f"Risk Level: {results.get('risk_level')}")
    print(f"Poisoning Detected: {results.get('poisoning_detected')}")
    
    if results.get('findings'):
        print(f"\nFindings ({len(results['findings'])}):")
        for i, finding in enumerate(results['findings'], 1):
            print(f"  {i}. {finding['type']}: {finding['matched_text']}")
    
    if results.get('suggested_remediations'):
        print("\nSuggested Remediations:")
        for i, remediation in enumerate(results['suggested_remediations'], 1):
            print(f"  {i}. {remediation}")

if __name__ == "__main__":
    main()
