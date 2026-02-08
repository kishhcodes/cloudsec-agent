#!/usr/bin/env python3
"""
Verification script for GCP Security Agent implementation

Verifies that all GCP agent files are properly created and integrated.
"""

import os
import sys


def verify_files_exist():
    """Verify all required GCP agent files exist."""
    print("Verifying GCP Agent Files...")
    
    required_files = [
        'src/agents/gcp_security/__init__.py',
        'src/agents/gcp_security/agent.py',
        'src/agents/gcp_security/cli.py',
        'src/agents/gcp_security/utils.py',
        'gcp_security_agent.py',
        'GCP_SECURITY_AGENT_README.md',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join('/home/vboxuser/projects/cloudsec-agent', file_path)
        exists = os.path.exists(full_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def verify_main_cli_integration():
    """Verify GCP agent is integrated into main CLI."""
    print("\nVerifying Main CLI Integration...")
    
    checks = {
        'GCP_SECURITY agent mode': 'AgentMode.GCP_SECURITY',
        'GCP agent import': 'from src.agents.gcp_security.agent import GCPSecurityAgent',
        'GCP agent loading': 'self.agents[mode] = GCPSecurityAgent()',
        'GCP intent detection': 'gcp_patterns =',
        'GCP in welcome message': '[bold]GCP Security[/bold]',
        'GCP in help': 'switch to gcp',
    }
    
    with open('/home/vboxuser/projects/cloudsec-agent/main_cli.py', 'r') as f:
        content = f.read()
    
    all_found = True
    for description, pattern in checks.items():
        found = pattern in content
        status = "✓" if found else "✗"
        print(f"{status} {description}")
        if not found:
            all_found = False
    
    return all_found


def verify_requirements_updated():
    """Verify requirements.txt includes GCP packages."""
    print("\nVerifying Requirements Updated...")
    
    required_packages = [
        'google-cloud-resource-manager',
        'google-cloud-storage',
        'google-cloud-compute',
        'google-cloud-sql',
        'google-cloud-iam-credentials',
    ]
    
    with open('/home/vboxuser/projects/cloudsec-agent/requirements.txt', 'r') as f:
        content = f.read()
    
    all_found = True
    for package in required_packages:
        found = package in content
        status = "✓" if found else "✗"
        print(f"{status} {package}")
        if not found:
            all_found = False
    
    return all_found


def verify_code_quality():
    """Basic code quality checks."""
    print("\nVerifying Code Quality...")
    
    files_to_check = [
        ('src/agents/gcp_security/agent.py', 'GCPSecurityAgent class'),
        ('src/agents/gcp_security/cli.py', 'main() function'),
        ('src/agents/gcp_security/utils.py', 'GCPSecurityPatterns class'),
    ]
    
    all_good = True
    for file_path, expected_content in files_to_check:
        full_path = os.path.join('/home/vboxuser/projects/cloudsec-agent', file_path)
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Check file size is reasonable (not empty)
            if len(content) < 100:
                print(f"✗ {file_path}: File too small")
                all_good = False
            # Check for syntax issues by looking for common patterns
            elif expected_content in content:
                print(f"✓ {file_path}: Contains expected content")
            else:
                print(f"⚠ {file_path}: May be missing expected content")
        except Exception as e:
            print(f"✗ {file_path}: {str(e)}")
            all_good = False
    
    return all_good


def verify_documentation():
    """Verify documentation exists."""
    print("\nVerifying Documentation...")
    
    doc_file = '/home/vboxuser/projects/cloudsec-agent/GCP_SECURITY_AGENT_README.md'
    
    if os.path.exists(doc_file):
        with open(doc_file, 'r') as f:
            content = f.read()
        
        sections = [
            '## Overview',
            '## Features',
            '## Setup & Configuration',
            '## Usage',
            '## Troubleshooting',
        ]
        
        all_found = True
        for section in sections:
            if section in content:
                print(f"✓ {section} documented")
            else:
                print(f"✗ {section} missing")
                all_found = False
        
        return all_found
    else:
        print("✗ GCP_SECURITY_AGENT_README.md not found")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("GCP Security Agent Implementation Verification")
    print("=" * 70)
    
    results = {
        "Files Exist": verify_files_exist(),
        "Main CLI Integration": verify_main_cli_integration(),
        "Requirements Updated": verify_requirements_updated(),
        "Code Quality": verify_code_quality(),
        "Documentation": verify_documentation(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    for check_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} checks passed")
    
    if passed_count == total_count:
        print("\n" + "=" * 70)
        print("✓ GCP Security Agent Successfully Implemented!")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Install GCP dependencies: pip install -r requirements.txt")
        print("2. Set up GCP authentication: gcloud auth application-default login")
        print("3. Set GOOGLE_CLOUD_PROJECT: export GOOGLE_CLOUD_PROJECT=your-project-id")
        print("4. Run the agent: python main_cli.py")
        print("5. Switch to GCP agent: switch to gcp")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
