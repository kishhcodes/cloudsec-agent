#!/usr/bin/env python
"""
Test script for the enhanced PDF export functionality
"""

import os
import sys
from dotenv import load_dotenv
from reportlab.lib import colors
from src.agents.security_analyzer.cli import save_as_pdf

def main():
    # Load environment variables
    load_dotenv()
    
    # Set Google application credentials if available
    if os.path.exists("config/vertex.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"
    
    # Create a comprehensive test result with more data for visualization
    test_result = {
        "success": True,
        "file_path": "data/test_config.json",
        "risk_level": "critical",
        "poisoning_detected": True,
        "findings": [
            {"type": "excessive_permissions", "matched_text": "admin-access", "context": "admin-access permission granted to unauthorized user"},
            {"type": "credential_exposure", "matched_text": "password123", "context": "hardcoded password found in configuration"},
            {"type": "encryption_weaknesses", "matched_text": "disabled", "context": "encryption disabled for sensitive data storage"},
            {"type": "insecure_protocol", "matched_text": "http://", "context": "insecure HTTP protocol used instead of HTTPS"},
            {"type": "default_credentials", "matched_text": "admin/admin", "context": "default credentials detected in configuration"},
            {"type": "misconfiguration", "matched_text": "open", "context": "firewall configuration set to open access from any IP"}
        ],
        "suggested_remediations": [
            "Remove excessive admin permissions and implement least privilege principle",
            "Use AWS Secrets Manager or equivalent service instead of hardcoding credentials",
            "Enable encryption at rest and in transit for all sensitive data",
            "Use only secure HTTPS endpoints for all API communications",
            "Change all default credentials and implement strong password policies",
            "Configure firewall rules to restrict access to specific IP ranges"
        ],
        "explanation": "This configuration exhibits multiple critical security flaws that could lead to a system compromise. The most severe issue is the use of hardcoded credentials combined with excessive administrative permissions. Additionally, sensitive data is being stored without encryption, creating compliance and security risks.\n\nThe use of insecure HTTP protocol exposes communications to potential interception, while default credentials indicate poor security practices. The open firewall configuration compounds these issues by allowing unrestricted access.\n\nRemediating these issues should be prioritized based on the risk level, starting with credential management and permission restrictions."
    }
    
    # Save as PDF with enhanced styling
    print("Creating enhanced PDF...")
    pdf_path = save_as_pdf(test_result)
    print(f"PDF saved to: {pdf_path}")
    print(f"PDF exists: {os.path.exists(pdf_path)}")
    print(f"PDF size: {os.path.getsize(pdf_path)} bytes")
    
    # Also test a scan result
    scan_result = {
        "success": True,
        "directory": "data/",
        "files_analyzed": 5,
        "files_with_issues": 3,
        "analysis_results": [
            {
                "file_path": "data/test_config.json",
                "risk_level": "critical",
                "poisoning_detected": True,
                "findings": [
                    {"type": "excessive_permissions", "matched_text": "admin-access", "context": "admin-access permission granted"}
                ]
            },
            {
                "file_path": "data/test_backup.json",
                "risk_level": "high",
                "poisoning_detected": True,
                "findings": [
                    {"type": "credential_exposure", "matched_text": "password", "context": "hardcoded password found"}
                ]
            },
            {
                "file_path": "data/test_dev.json",
                "risk_level": "medium",
                "poisoning_detected": True,
                "findings": [
                    {"type": "encryption_weaknesses", "matched_text": "disabled", "context": "encryption disabled"}
                ]
            }
        ]
    }
    
    # Save scan result as PDF
    print("\nCreating scan report PDF...")
    scan_pdf_path = save_as_pdf(scan_result)
    print(f"PDF saved to: {scan_pdf_path}")
    print(f"PDF exists: {os.path.exists(scan_pdf_path)}")
    print(f"PDF size: {os.path.getsize(scan_pdf_path)} bytes")

if __name__ == "__main__":
    main()
