#!/usr/bin/env python3
"""
Test: Multi-Format Export + Remediation Playbooks

Demonstrates exporting audit reports in multiple formats and
executing automated remediation playbooks.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from src.audit.exporters import (
    JSONExporter, CSVExporter, HTMLExporter, EmailService
)
from src.remediation import (
    RemediationPlaybook, PlaybookExecutor, PlaybookLibrary, PlaybookStatus
)


def create_sample_report_data() -> dict:
    """Create sample audit report data."""
    return {
        "account_id": "123456789012",
        "account_name": "Production AWS Account",
        "security_score": 72.5,
        "findings": [
            {
                "id": "FIND-001",
                "title": "S3 Bucket Public Access",
                "description": "S3 bucket allows public read/write access",
                "severity": "CRITICAL",
                "category": "Storage",
                "resource": "arn:aws:s3:::company-data-bucket",
                "remediation": "Enable S3 Block Public Access and update bucket policy"
            },
            {
                "id": "FIND-002",
                "title": "Unencrypted EBS Volume",
                "description": "EBS volume does not have encryption enabled",
                "severity": "HIGH",
                "category": "Compute",
                "resource": "vol-0123456789abcdef",
                "remediation": "Enable encryption for the EBS volume"
            },
            {
                "id": "FIND-003",
                "title": "CloudTrail Not Enabled",
                "description": "CloudTrail logging is not enabled for the region",
                "severity": "HIGH",
                "category": "Compliance",
                "resource": "us-east-1",
                "remediation": "Enable CloudTrail for all regions"
            },
            {
                "id": "FIND-004",
                "title": "Overly Permissive Security Group",
                "description": "Security group allows unrestricted SSH access",
                "severity": "MEDIUM",
                "category": "Network",
                "resource": "sg-0123456789abcdef",
                "remediation": "Restrict SSH access to known IP ranges"
            }
        ],
        "compliance": {
            "CIS Controls v8": {
                "coverage": 75,
                "covered_controls": 15,
                "total_controls": 20,
                "status": "REVIEW",
                "gap_count": 5
            },
            "PCI DSS": {
                "coverage": 65,
                "covered_controls": 13,
                "total_controls": 20,
                "status": "REVIEW",
                "gap_count": 7
            }
        },
        "recommendations": [
            "Enable encryption on all data stores",
            "Implement network segmentation",
            "Enable comprehensive logging and monitoring",
            "Regular security awareness training"
        ]
    }


def demo_json_export():
    """Demonstrate JSON export."""
    print("\n" + "=" * 70)
    print("📊 JSON EXPORT DEMO")
    print("=" * 70)
    
    exporter = JSONExporter()
    report_data = create_sample_report_data()
    
    # Export full report
    output_path = "reports/export_demo_report.json"
    json_str = exporter.export_report(
        report_data,
        output_path=output_path,
        pretty=True
    )
    
    print(f"✅ Report exported to: {output_path}")
    print(f"\n📝 JSON Preview (first 500 chars):\n")
    print(json_str[:500] + "...\n")
    
    # Export for CI/CD pipeline
    pipeline_json = exporter.export_for_pipeline(report_data, "github")
    print("✅ Pipeline-optimized JSON generated")
    
    # Export findings only
    findings_json = exporter.export_findings(
        report_data.get("findings", []),
        output_path="reports/export_demo_findings.json"
    )
    
    print("✅ Findings exported separately")


def demo_csv_export():
    """Demonstrate CSV export."""
    print("\n" + "=" * 70)
    print("📊 CSV EXPORT DEMO")
    print("=" * 70)
    
    exporter = CSVExporter()
    report_data = create_sample_report_data()
    
    # Export findings
    csv_path = exporter.export_findings_to_csv(
        report_data.get("findings", []),
        "reports/export_demo_findings.csv"
    )
    print(f"✅ Findings exported to CSV: {csv_path}")
    
    # Export report summary
    summary_path = exporter.export_report_summary_to_csv(
        report_data,
        "reports/export_demo_summary.csv"
    )
    print(f"✅ Summary exported to CSV: {summary_path}")
    
    # Export remediation tracker
    tracker_path = exporter.export_remediation_tracker_to_csv(
        report_data.get("findings", []),
        "reports/export_demo_tracker.csv"
    )
    print(f"✅ Remediation tracker exported: {tracker_path}")
    
    # Export compliance summary
    compliance_path = exporter.export_compliance_summary_to_csv(
        report_data.get("compliance", {}),
        "reports/export_demo_compliance.csv"
    )
    print(f"✅ Compliance summary exported: {compliance_path}")


def demo_html_export():
    """Demonstrate HTML export."""
    print("\n" + "=" * 70)
    print("🌐 HTML EXPORT DEMO")
    print("=" * 70)
    
    exporter = HTMLExporter()
    report_data = create_sample_report_data()
    
    # Export full report
    report_path = exporter.export_report_to_html(
        report_data,
        "reports/export_demo_report.html"
    )
    print(f"✅ Full report exported to HTML: {report_path}")
    
    # Export email template
    email_path = exporter.export_email_template(
        report_data,
        "reports/export_demo_email.html",
        recipient_name="Alice Johnson"
    )
    print(f"✅ Email template exported: {email_path}")
    
    # Export executive summary
    summary_path = exporter.export_executive_summary_html(
        report_data,
        "reports/export_demo_executive.html"
    )
    print(f"✅ Executive summary exported: {summary_path}")


def demo_email_service():
    """Demonstrate email service configuration."""
    print("\n" + "=" * 70)
    print("📧 EMAIL SERVICE DEMO")
    print("=" * 70)
    
    email_service = EmailService()
    
    # Check if email is configured
    if email_service.sender_email:
        print(f"✅ Email service configured")
        print(f"   From: {email_service.sender_email}")
        
        # Test connection (requires valid credentials)
        # if email_service.test_connection():
        #     print("✅ SMTP connection successful")
        # else:
        #     print("⚠️  SMTP connection failed")
        
        print("⚠️  Email credentials found in environment")
        print("   To send emails, ensure SENDER_EMAIL and SENDER_PASSWORD are set")
    else:
        print("⚠️  Email service not configured")
        print("   Set SENDER_EMAIL and SENDER_PASSWORD environment variables")


def demo_playbook_execution():
    """Demonstrate remediation playbook execution."""
    print("\n" + "=" * 70)
    print("🔧 REMEDIATION PLAYBOOK DEMO")
    print("=" * 70)
    
    # Create executor
    executor = PlaybookExecutor()
    
    # Get a playbook from library
    playbooks = PlaybookLibrary.get_all_playbooks()
    playbook = playbooks["AWS-PUBLIC-S3"]
    
    print(f"\n📋 Playbook: {playbook.name}")
    print(f"   ID: {playbook.playbook_id}")
    print(f"   Category: {playbook.finding_category}")
    print(f"   Severity: {playbook.severity}")
    print(f"   Requires Approval: {playbook.requires_approval}")
    print(f"   Actions: {len(playbook.actions)}")
    
    # Validate playbook
    is_valid = executor.validate_playbook(playbook)
    print(f"\n✅ Playbook validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Create sample finding
    finding_data = {
        "id": "FIND-001",
        "title": "S3 Bucket Public Access",
        "resource": "arn:aws:s3:::company-data-bucket"
    }
    
    # Execute playbook (with approval required)
    print(f"\n⏳ Executing playbook (with approval requirement)...")
    execution = executor.execute_playbook(
        playbook,
        finding_data,
        initiated_by="security-admin@company.com",
        dry_run=True
    )
    
    print(f"\n📊 Execution Report:")
    print(f"   Execution ID: {execution.execution_id}")
    print(f"   Status: {execution.status.value}")
    print(f"   Approval Status: {execution.approval_status}")
    print(f"   Initiated By: {execution.initiated_by}")
    
    # Simulate approval
    print(f"\n✅ Approving execution...")
    executor.approve_execution(
        execution.execution_id,
        approver="security-manager@company.com"
    )
    
    # Get execution history
    print(f"\n📜 Execution History:")
    history = executor.get_execution_history(playbook.playbook_id)
    print(f"   Total executions: {len(history)}")


def demo_playbook_library():
    """Demonstrate playbook library browsing."""
    print("\n" + "=" * 70)
    print("📚 PLAYBOOK LIBRARY DEMO")
    print("=" * 70)
    
    # Get all playbooks
    playbooks = PlaybookLibrary.get_all_playbooks()
    print(f"\n📊 Available Playbooks: {len(playbooks)}")
    
    for pb_id, playbook in playbooks.items():
        print(f"\n  • {playbook.name}")
        print(f"    ID: {pb_id}")
        print(f"    Category: {playbook.finding_category}")
        print(f"    Severity: {playbook.severity}")
        print(f"    Approval Required: {playbook.requires_approval}")
    
    # Filter by category
    print(f"\n\n🔍 Storage-Related Playbooks:")
    storage_playbooks = PlaybookLibrary.get_playbook_by_category("Storage")
    for pb_id, pb in storage_playbooks.items():
        print(f"  • {pb.name} ({pb_id})")
    
    # Filter by severity
    print(f"\n🔴 Critical Severity Playbooks:")
    critical_playbooks = PlaybookLibrary.get_playbooks_by_severity("CRITICAL")
    for pb_id, pb in critical_playbooks.items():
        print(f"  • {pb.name} ({pb_id})")


def main():
    """Run all demos."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "   MULTI-FORMAT EXPORT + REMEDIATION PLAYBOOKS DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Create reports directory
    Path("reports").mkdir(exist_ok=True)
    
    try:
        # Run demos
        demo_json_export()
        demo_csv_export()
        demo_html_export()
        demo_email_service()
        demo_playbook_library()
        demo_playbook_execution()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        print("\n📂 Generated Files:")
        for file in Path("reports").glob("export_demo_*"):
            print(f"  • {file}")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
