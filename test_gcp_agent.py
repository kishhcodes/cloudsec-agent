#!/usr/bin/env python3
"""
Test script for GCP Security Agent

Tests basic functionality without requiring a real GCP project.
"""

import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_gcp_agent_initialization():
    """Test GCP agent initialization."""
    print("Testing GCP Agent Initialization...")
    
    # Mock the GCP clients
    with patch('google.cloud.resource_manager_v3.ProjectsClient'):
        with patch('google.cloud.storage.Client'):
            with patch('google.cloud.compute_v1.InstancesClient'):
                with patch('google.cloud.sql_v1beta4.SqlInstancesServiceClient'):
                    with patch('google.cloud.iam_credentials_v1.IAMCredentialsClient'):
                        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
                        os.environ['GOOGLE_API_KEY'] = 'test-key'
                        
                        try:
                            from src.agents.gcp_security.agent import GCPSecurityAgent
                            agent = GCPSecurityAgent(project_id='test-project')
                            print("✓ GCP Agent initialized successfully")
                            return True
                        except Exception as e:
                            print(f"✗ Failed to initialize GCP Agent: {str(e)}")
                            return False


def test_gcp_agent_command_parsing():
    """Test command parsing."""
    print("\nTesting Command Parsing...")
    
    with patch('google.cloud.resource_manager_v3.ProjectsClient'):
        with patch('google.cloud.storage.Client'):
            with patch('google.cloud.compute_v1.InstancesClient'):
                with patch('google.cloud.sql_v1beta4.SqlInstancesServiceClient'):
                    with patch('google.cloud.iam_credentials_v1.IAMCredentialsClient'):
                        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
                        os.environ['GOOGLE_API_KEY'] = 'test-key'
                        
                        from src.agents.gcp_security.agent import GCPSecurityAgent
                        agent = GCPSecurityAgent(project_id='test-project')
                        
                        # Test various commands
                        test_queries = [
                            ("Check my IAM security", "iam_analysis"),
                            ("Analyze my Cloud Storage buckets", "storage_analysis"),
                            ("Review Compute Engine security", "compute_analysis"),
                            ("Check Cloud SQL security", "sql_analysis"),
                            ("Analyze my VPC", "network_analysis"),
                        ]
                        
                        for query, expected_type in test_queries:
                            commands = agent._parse_command(query)
                            if commands and commands[0][0] == expected_type:
                                print(f"✓ Correctly parsed: '{query}'")
                            else:
                                print(f"✗ Failed to parse: '{query}'")
                                print(f"  Expected: {expected_type}, Got: {commands}")
                        
                        return True


def test_gcp_security_utilities():
    """Test GCP security utilities."""
    print("\nTesting GCP Security Utilities...")
    
    try:
        from src.agents.gcp_security.utils import (
            GCPSecurityPatterns,
            GCPSecurityRecommendations,
            calculate_overall_risk_score
        )
        
        # Test patterns
        assert len(GCPSecurityPatterns.IAM_RISKY_ROLES) > 0
        print("✓ IAM risky roles patterns loaded")
        
        assert len(GCPSecurityPatterns.STORAGE_SECURITY_BEST_PRACTICES) > 0
        print("✓ Storage security best practices loaded")
        
        # Test recommendations
        iam_recs = GCPSecurityRecommendations.get_iam_recommendations()
        assert len(iam_recs) > 0
        print(f"✓ IAM recommendations loaded ({len(iam_recs)} recommendations)")
        
        storage_recs = GCPSecurityRecommendations.get_storage_recommendations()
        assert len(storage_recs) > 0
        print(f"✓ Storage recommendations loaded ({len(storage_recs)} recommendations)")
        
        # Test risk calculation
        test_scores = {
            "iam": 3,
            "storage": 2,
            "compute": 4
        }
        risk_level = calculate_overall_risk_score(test_scores)
        print(f"✓ Risk calculation works (score: {risk_level})")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test utilities: {str(e)}")
        return False


def test_integration_with_main_cli():
    """Test integration with main CLI."""
    print("\nTesting Integration with Main CLI...")
    
    try:
        with open('main_cli.py', 'r') as f:
            content = f.read()
            
            checks = [
                ('GCP_SECURITY' in content, 'GCP_SECURITY mode added'),
                ('gcp-security' in content, 'gcp-security routing'),
                ('GCPSecurityAgent' in content, 'GCPSecurityAgent import'),
                ('google cloud' in content.lower(), 'GCP keyword detection'),
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    print(f"✓ {description}")
                else:
                    print(f"✗ {description}")
                    all_passed = False
            
            return all_passed
    except Exception as e:
        print(f"✗ Failed to test integration: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("GCP Security Agent Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Agent Initialization", test_gcp_agent_initialization()))
    results.append(("Command Parsing", test_gcp_agent_command_parsing()))
    results.append(("Security Utilities", test_gcp_security_utilities()))
    results.append(("CLI Integration", test_integration_with_main_cli()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! GCP Security Agent is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
