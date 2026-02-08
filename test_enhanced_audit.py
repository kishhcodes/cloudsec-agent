#!/usr/bin/env python3
"""
Audit Report Enhancement Demo

Demonstrates the new chart and compliance features in audit reports.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.audit import AWSAuditReport, ChartGenerator, ComplianceMapper


def demo_enhanced_audit():
    """Demonstrate enhanced audit report generation"""
    
    print("\n" + "="*70)
    print("ENHANCED AUDIT REPORT DEMO")
    print("="*70 + "\n")
    
    # Create AWS audit report
    print("Creating enhanced AWS audit report...")
    report = AWSAuditReport("123456789012")
    
    # Add sample IAM analysis
    iam_analysis = {
        "description": "Analysis of Identity and Access Management configurations",
        "findings": [
            {
                "severity": "CRITICAL",
                "title": "Root Account MFA Disabled",
                "description": "The root account does not have MFA enabled",
                "recommendation": "Enable MFA on the root account immediately"
            },
            {
                "severity": "HIGH",
                "title": "Overly Permissive IAM Policy",
                "description": "Some IAM policies grant excessive permissions",
                "recommendation": "Review and implement least privilege access"
            },
            {
                "severity": "MEDIUM",
                "title": "Unused IAM Users",
                "description": "Several IAM users have not been used in 90 days",
                "recommendation": "Disable or remove unused IAM users"
            },
            {
                "severity": "LOW",
                "title": "Missing Access Key Rotation",
                "description": "Some access keys have not been rotated recently",
                "recommendation": "Implement access key rotation policy"
            },
            {
                "severity": "PASS",
                "title": "Password Policy Configured",
                "description": "Strong password policy is configured",
                "recommendation": "Policy is correctly configured"
            }
        ],
        "summary": [
            "1 critical security issue requires immediate attention",
            "1 high-risk finding needs remediation within 1 week",
            "2 medium/low findings can be addressed within 1 month"
        ]
    }
    
    report.add_iam_analysis(iam_analysis)
    
    # Add storage analysis
    storage_analysis = {
        "description": "Analysis of S3 bucket security configurations",
        "findings": [
            {
                "severity": "CRITICAL",
                "title": "S3 Bucket Publicly Accessible",
                "description": "Production bucket allows public read access",
                "recommendation": "Remove public ACLs and use bucket policies"
            },
            {
                "severity": "MEDIUM",
                "title": "S3 Versioning Not Enabled",
                "description": "Bucket versioning is disabled",
                "recommendation": "Enable S3 versioning for data protection"
            }
        ],
        "summary": [
            "Critical data exposure risk identified"
        ]
    }
    
    report.add_storage_analysis(storage_analysis)
    
    # Add compute analysis
    compute_analysis = {
        "description": "Analysis of EC2 instance security",
        "findings": [
            {
                "severity": "HIGH",
                "title": "EC2 Instance Without Security Group",
                "description": "Instance lacks proper security group configuration",
                "recommendation": "Assign appropriate security groups"
            }
        ],
        "summary": [
            "Review security group rules"
        ]
    }
    
    report.add_compute_analysis(compute_analysis)
    
    # Calculate security score
    print("\nCalculating security score...")
    score = report.calculate_security_score()
    print(f"Security Score: {score:.1f}/100")
    
    # Enable charts
    print("Enabling chart generation...")
    report.include_charts = True
    
    # Enable compliance framework mapping
    print("Enabling compliance framework mapping...")
    report.enable_compliance_mapping([
        "CIS Controls v8",
        "PCI DSS",
        "ISO 27001"
    ])
    
    # Display compliance information
    print("\n" + "-"*70)
    print("COMPLIANCE FRAMEWORK COVERAGE")
    print("-"*70)
    
    compliance_mapper = ComplianceMapper()
    findings = report.get_all_findings()
    
    for framework in ["CIS Controls v8", "PCI DSS", "ISO 27001"]:
        coverage = compliance_mapper.calculate_framework_coverage(findings, framework)
        print(f"{framework}: {coverage:.1f}%")
    
    # Generate PDF report
    print("\n" + "-"*70)
    print("GENERATING ENHANCED PDF REPORT")
    print("-"*70)
    
    pdf_path = report.generate_pdf()
    print(f"\n✓ Report generated: {pdf_path}")
    
    # Display summary
    print("\n" + "-"*70)
    print("AUDIT SUMMARY")
    print("-"*70)
    report.display_summary()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_enhanced_audit()
