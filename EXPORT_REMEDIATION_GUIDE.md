# Multi-Format Report Export & Remediation Playbooks

**Complete Feature Implementation Guide**  
*Phase 1 & 2 Integration*  
Date: February 7, 2026

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Multi-Format Export System](#multi-format-export-system)
3. [Remediation Playbook Engine](#remediation-playbook-engine)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This document covers two major feature implementations:

### 1. **Multi-Format Report Export** (2,500+ lines)
   - JSON export for API integration & CI/CD pipelines
   - CSV export for spreadsheet analysis
   - HTML export with responsive email templates
   - Email delivery with SMTP integration
   - Report scheduling

### 2. **Remediation Playbook Engine** (1,500+ lines)
   - Automated remediation of security findings
   - Pre-built playbooks for 10 common findings
   - Approval workflows with audit logging
   - Rollback support for safe automation
   - Cloud-agnostic action handlers

---

## Multi-Format Export System

### Architecture

```
AuditReport
    ├── JSONExporter
    │   ├── export_report()              → Structured JSON
    │   ├── export_for_api_integration() → API-friendly JSON
    │   └── export_for_pipeline()        → CI/CD optimized
    │
    ├── CSVExporter
    │   ├── export_findings_to_csv()           → Findings spreadsheet
    │   ├── export_remediation_tracker_to_csv() → Remediation tracking
    │   └── export_compliance_summary_to_csv()  → Compliance matrix
    │
    ├── HTMLExporter
    │   ├── export_report_to_html()           → Full HTML report
    │   ├── export_email_template()           → Email-ready HTML
    │   └── export_executive_summary_html()   → Executive summary
    │
    └── EmailService
        ├── send_report()            → Email with attachments
        ├── send_critical_alert()    → Escalated alerts
        └── EmailScheduler           → Scheduled delivery
```

### JSON Export Features

**Full Report Export:**
```python
from src.audit.exporters import JSONExporter

exporter = JSONExporter()
json_str = exporter.export_report(
    report_data,
    output_path="report.json",
    pretty=True
)
```

**Output Structure:**
```json
{
  "metadata": {
    "exported_at": "2026-02-07T10:30:00",
    "export_format": "json",
    "version": "1.0"
  },
  "summary": {
    "account_id": "123456789012",
    "security_score": 72.5,
    "total_findings": 8,
    "critical": 2,
    "high": 2,
    "medium": 2,
    "low": 1
  },
  "findings": [...],
  "compliance": {...},
  "recommendations": [...]
}
```

**Pipeline Integration:**
```python
# GitHub Actions compatible
pipeline_json = exporter.export_for_pipeline(
    report_data,
    pipeline_type="github"  # or "gitlab", "jenkins"
)
```

**GitLab SAST Format:**
- Converts findings to SAST vulnerability format
- Integrates with GitLab's security dashboard
- Enables MR blocking on critical findings

### CSV Export Features

**Findings Export:**
```python
from src.audit.exporters import CSVExporter

exporter = CSVExporter()
exporter.export_findings_to_csv(
    findings=report_data['findings'],
    output_path="findings.csv",
    include_fields=['id', 'title', 'severity', 'remediation']
)
```

**Columns Generated:**
- ID, Title, Severity, Category, Resource
- Description, Remediation, Status
- (Optionally: Assigned_To, Due_Date, Notes)

**Remediation Tracker:**
```python
exporter.export_remediation_tracker_to_csv(
    findings=report_data['findings'],
    output_path="remediation_tracker.csv"
)
```

Includes empty columns for:
- Status (New, In Progress, Completed)
- Assigned To
- Due Date
- Notes/Comments

**Compliance Matrix:**
```python
exporter.export_compliance_summary_to_csv(
    compliance_data=report_data['compliance'],
    output_path="compliance.csv"
)
```

Output:
| Framework | Coverage | Controls Covered | Total Controls | Status | Gaps |
|-----------|----------|------------------|-----------------|--------|------|
| CIS v8    | 75%      | 15               | 20              | REVIEW | 5    |
| PCI DSS   | 65%      | 13               | 20              | REVIEW | 7    |

### HTML Export Features

**Full Report:**
```python
from src.audit.exporters import HTMLExporter

exporter = HTMLExporter()
exporter.export_report_to_html(
    report_data,
    output_path="report.html",
    include_toc=True,
    include_charts=True
)
```

Features:
- Responsive design (mobile-friendly)
- Table of contents with anchor links
- Color-coded severity indicators
- Interactive charts (when charts available)
- Print-friendly styling

**Email Template:**
```python
exporter.export_email_template(
    report_data,
    output_path="email_report.html",
    recipient_name="Alice Johnson",
    include_cta=True
)
```

Includes:
- Professional header with company colors
- Executive summary with key metrics
- Critical findings alert box
- Call-to-action buttons (View Report, View Dashboard)
- Footer with security notice

**Executive Summary:**
```python
exporter.export_executive_summary_html(
    report_data,
    output_path="executive_summary.html"
)
```

One-page summary with:
- Security posture assessment
- Key findings overview
- Compliance framework status
- Recommended next steps

### Email Service

**SMTP Configuration:**
```python
from src.audit.exporters import EmailService

email_service = EmailService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email="security@company.com",
    sender_password="app_password_here"
)
```

**Or via Environment Variables:**
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=security@company.com
export SENDER_PASSWORD=your_app_password
```

**Send Report with Attachment:**
```python
email_service.send_report_with_attachment(
    recipient_emails=["ciso@company.com", "security@company.com"],
    subject="Security Audit Report - Production",
    html_content=html_email_content,
    report_file_path="reports/production_audit.pdf",
    report_format="pdf"
)
```

**Critical Alert Notification:**
```python
email_service.send_critical_alert(
    recipient_emails=["oncall@company.com", "security@company.com"],
    finding_data={
        "title": "S3 Bucket Public Access",
        "resource": "arn:aws:s3:::company-data",
        "description": "...",
        "remediation": "..."
    },
    escalation_level="CRITICAL"
)
```

**Email Scheduling:**
```python
from src.audit.exporters import EmailScheduler

scheduler = EmailScheduler(email_service)

# Daily at 9 AM
scheduler.schedule_daily_report(
    schedule_id="daily-executive",
    recipient_emails=["ciso@company.com"],
    report_generator_func=generate_daily_report,
    hour=9,
    minute=0
)

# Weekly on Monday at 8 AM
scheduler.schedule_weekly_report(
    schedule_id="weekly-audit",
    recipient_emails=["team@company.com"],
    report_generator_func=generate_weekly_report,
    day_of_week=0,  # Monday
    hour=8,
    minute=0
)
```

---

## Remediation Playbook Engine

### Architecture

```
RemediationPlaybook (Configuration)
    ├── Finding Category
    ├── Severity Level
    ├── Prerequisites
    └── Actions[]
        ├── Action 1 (AWS)
        ├── Action 2 (Notification)
        └── Action 3 (Script)

PlaybookExecutor (Execution Engine)
    ├── validate_playbook()
    ├── execute_playbook()
    ├── approve_execution()
    ├── rollback_execution()
    └── get_execution_history()
```

### Playbook Definition

**Create Custom Playbook:**
```python
from src.remediation import RemediationPlaybook

playbook = RemediationPlaybook(
    playbook_id="CUSTOM-S3-FIX",
    name="Fix Public S3 Bucket",
    description="Automatically restricts public access",
    finding_category="Storage",
    severity="CRITICAL"
)

# Add remediation actions
playbook.add_action(
    action_name="block_public_access",
    action_type="aws",
    params={
        "service": "s3",
        "action": "put-public-access-block",
        "params": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True
        }
    }
)

# Add notification action
playbook.add_action(
    action_name="notify_team",
    action_type="notification",
    params={
        "type": "slack",
        "channel": "#security-alerts",
        "message": "S3 public access was automatically blocked"
    }
)

# Configure playbook
playbook.requires_approval = True
playbook.rollback_enabled = True
playbook.timeout_seconds = 300
```

### Standard Playbooks

**Available in PlaybookLibrary:**

| ID | Name | Category | Severity |
|---|---|---|---|
| AWS-PUBLIC-S3 | Fix Public S3 Bucket | Storage | CRITICAL |
| AWS-EBS-ENCRYPTION | Enable EBS Encryption | Compute | HIGH |
| AWS-SG-RESTRICTION | Restrict Security Group | Network | HIGH |
| GCP-PUBLIC-BUCKET | Restrict GCS Bucket | Storage | CRITICAL |
| GCP-FW-RESTRICTION | Restrict Firewall Rule | Network | HIGH |
| AZURE-BLOB-PUBLIC | Restrict Blob Storage | Storage | CRITICAL |
| AZURE-NSG-RESTRICTION | Restrict NSG Rule | Network | HIGH |
| ENABLE-LOGGING | Enable Resource Logging | Compliance | MEDIUM |
| ENABLE-MFA | Enable MFA | IAM | CRITICAL |
| ROTATE-CREDENTIALS | Rotate Credentials | IAM | CRITICAL |

**Get Playbooks:**
```python
from src.remediation import PlaybookLibrary

# Get all playbooks
all = PlaybookLibrary.get_all_playbooks()

# Get by category
storage = PlaybookLibrary.get_playbook_by_category("Storage")

# Get by severity
critical = PlaybookLibrary.get_playbooks_by_severity("CRITICAL")
```

### Execution Flow

**Step 1: Validate Playbook**
```python
from src.remediation import PlaybookExecutor

executor = PlaybookExecutor()
is_valid = executor.validate_playbook(playbook)
```

**Step 2: Execute (if approval not required)**
```python
execution = executor.execute_playbook(
    playbook=playbook,
    finding_data=finding,
    initiated_by="admin@company.com",
    dry_run=False
)

# Execution immediately runs all actions
# Returns PlaybookExecution with status=COMPLETED/FAILED
```

**Step 3: Execute with Approval**
```python
# Initiate execution (status=PENDING)
execution = executor.execute_playbook(
    playbook=playbook,
    finding_data=finding,
    initiated_by="analyst@company.com",
    dry_run=True  # Can test with dry_run=True
)

# Approval required (status=AWAITING_APPROVAL)
if execution.status == PlaybookStatus.PENDING:
    # Get approval from security manager
    approved = executor.approve_execution(
        execution_id=execution.execution_id,
        approver="manager@company.com",
        dry_run=False
    )
    # Now playbook executes (status=RUNNING → COMPLETED/FAILED)
```

**Step 4: Rollback (if enabled)**
```python
# If execution completed but caused issues
executor.rollback_execution(
    execution_id=execution.execution_id
)
# Reverses all actions in reverse order
```

### Execution Status Flow

```
PENDING (awaiting approval)
  ├─ Approval → APPROVED → RUNNING → COMPLETED ✅
  ├─ Approval → APPROVED → RUNNING → FAILED ❌
  └─ Rejection → REJECTED (stops here)

COMPLETED (successfully remediated)
  └─ rollback_execution() → ROLLED_BACK
```

### Dry Run Mode

Test playbooks without making real changes:
```python
execution = executor.execute_playbook(
    playbook=playbook,
    finding_data=finding,
    initiated_by="admin@company.com",
    dry_run=True  # No actual changes
)

# Review execution.actions to see what would happen
for action in execution.actions:
    print(f"{action.action_name}: {action.message}")
    # Output: [DRY RUN] AWS action would be executed: put-public-access-block
```

### Execution History

```python
# Get all executions for a playbook
history = executor.get_execution_history(
    playbook_id="AWS-PUBLIC-S3",
    limit=10
)

# Filter by finding
history = executor.get_execution_history(
    finding_id="FIND-001",
    limit=5
)

# Detailed execution record
execution = executor.get_execution(execution_id)
print(f"Status: {execution.status.value}")
print(f"Actions executed: {len(execution.actions)}")
print(f"Started: {execution.started_at}")
print(f"Completed: {execution.ended_at}")
```

---

## API Reference

### JSONExporter

```python
class JSONExporter:
    def export_report(report_data, output_path=None, pretty=True) → str
    def export_findings(findings, output_path=None, pretty=True) → str
    def export_compliance_summary(compliance_data, output_path=None, pretty=True) → str
    def export_for_api_integration(report_data, include_fields=None, exclude_fields=None) → str
    def export_for_pipeline(report_data, pipeline_type="generic") → str
```

### CSVExporter

```python
class CSVExporter:
    def export_findings_to_csv(findings, output_path, include_fields=None) → str
    def export_report_summary_to_csv(report_data, output_path) → str
    def export_findings_by_severity_to_csv(findings, output_path) → str
    def export_compliance_summary_to_csv(compliance_data, output_path) → str
    def export_remediation_tracker_to_csv(findings, output_path) → str
```

### HTMLExporter

```python
class HTMLExporter:
    def export_report_to_html(report_data, output_path, include_toc=True, include_charts=True) → str
    def export_email_template(report_data, output_path, recipient_name=None, include_cta=True) → str
    def export_executive_summary_html(report_data, output_path) → str
```

### EmailService

```python
class EmailService:
    def __init__(smtp_server=None, smtp_port=None, sender_email=None, sender_password=None)
    def send_report(recipient_emails, subject, html_content, attachments=None, cc=None, bcc=None, reply_to=None) → bool
    def send_report_with_attachment(recipient_emails, subject, html_content, report_file_path, report_format="pdf") → bool
    def send_critical_alert(recipient_emails, finding_data, escalation_level="HIGH") → bool
    def test_connection() → bool

class EmailScheduler:
    def __init__(email_service: EmailService)
    def schedule_daily_report(schedule_id, recipient_emails, report_generator_func, hour=9, minute=0) → bool
    def schedule_weekly_report(schedule_id, recipient_emails, report_generator_func, day_of_week=0, hour=9, minute=0) → bool
    def disable_schedule(schedule_id) → bool
    def list_schedules() → List[Dict]
```

### RemediationPlaybook

```python
class RemediationPlaybook:
    def __init__(playbook_id, name, description, finding_category, severity)
    def add_action(action_name, action_type, params, condition=None) → None
    def add_prerequisite(check_name) → None
    def set_approval_required(required: bool) → None
    def set_rollback_enabled(enabled: bool) → None
    def to_dict() → Dict
```

### PlaybookExecutor

```python
class PlaybookExecutor:
    def __init__(cloud_clients=None)
    def validate_playbook(playbook) → bool
    def execute_playbook(playbook, finding_data, initiated_by, execution_id=None, dry_run=False) → PlaybookExecution
    def approve_execution(execution_id, approver, dry_run=False) → bool
    def reject_execution(execution_id, rejector, reason) → bool
    def rollback_execution(execution_id) → bool
    def get_execution(execution_id) → PlaybookExecution
    def get_execution_history(playbook_id=None, finding_id=None, limit=10) → List[PlaybookExecution]
    def register_handler(action_type, handler: Callable) → None
```

---

## Usage Examples

### Complete Workflow

```python
from src.audit import AWSAuditReport
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter, EmailService
from src.remediation import PlaybookExecutor, PlaybookLibrary

# 1. Generate audit report
report = AWSAuditReport("123456789012")
report.add_iam_analysis(iam_data)
report.add_storage_analysis(storage_data)
report.enable_compliance_mapping()
report_data = report.generate_pdf()

# 2. Export in multiple formats
json_exporter = JSONExporter()
json_exporter.export_report(report_data, "reports/audit.json")

csv_exporter = CSVExporter()
csv_exporter.export_findings_to_csv(report_data['findings'], "reports/findings.csv")
csv_exporter.export_remediation_tracker_to_csv(report_data['findings'], "reports/tracker.csv")

html_exporter = HTMLExporter()
html_exporter.export_email_template(report_data, "reports/email.html", "Alice Johnson")

# 3. Send report via email
email_service = EmailService()
email_service.send_report_with_attachment(
    recipient_emails=["ciso@company.com"],
    subject="Production Audit Report",
    html_content=open("reports/email.html").read(),
    report_file_path="reports/audit.pdf"
)

# 4. Auto-remediate critical findings
executor = PlaybookExecutor()
playbooks = PlaybookLibrary.get_all_playbooks()

for finding in report_data['findings']:
    if finding['severity'] == 'CRITICAL':
        # Find matching playbook
        playbook_id = find_playbook_for_finding(finding)
        playbook = playbooks[playbook_id]
        
        # Execute with approval
        execution = executor.execute_playbook(
            playbook,
            finding,
            initiated_by="automation@company.com",
            dry_run=False
        )
        
        print(f"Remediation {execution.execution_id}: {execution.status.value}")
```

### API Integration

```python
# Export findings for API consumption
json_exporter = JSONExporter()
api_json = json_exporter.export_for_api_integration(
    report_data,
    include_fields=['id', 'title', 'severity', 'remediation']
)

# Use in API response
import json
response = json.loads(api_json)
return {'status': 'success', 'data': response}
```

### CI/CD Pipeline Integration

```python
# Export for GitHub Actions
json_exporter = JSONExporter()
pipeline_json = json_exporter.export_for_pipeline(report_data, "github")

# Parse and create annotations
pipeline_data = json.loads(pipeline_json)
if pipeline_data['status'] == 'CRITICAL':
    # GitHub Actions will fail the workflow
    print("::error::Critical security issues found")
```

---

## Configuration

### Email Configuration

**Gmail:**
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-specific-password
```

[Get Gmail App Password](https://myaccount.google.com/apppasswords)

**Office 365:**
```bash
export SMTP_SERVER=smtp.office365.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@company.onmicrosoft.com
export SENDER_PASSWORD=your-password
```

**AWS SES:**
```bash
export SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
export SMTP_PORT=587
export SENDER_EMAIL=your-verified-email@company.com
export SENDER_PASSWORD=your-ses-password
```

### Custom Actions

Register custom action handlers:
```python
def handle_custom_action(action, dry_run):
    # Custom logic
    return ActionResult(...)

executor.register_handler("custom_type", handle_custom_action)
```

---

## Troubleshooting

### Email Not Sending

**Check credentials:**
```python
email_service = EmailService()
if email_service.test_connection():
    print("✅ SMTP configured correctly")
else:
    print("❌ SMTP connection failed")
```

**Verify environment variables:**
```bash
echo $SENDER_EMAIL
echo $SENDER_PASSWORD  # Should show password
```

### Playbook Execution Failed

**Check playbook validity:**
```python
executor = PlaybookExecutor()
if not executor.validate_playbook(playbook):
    print("❌ Playbook validation failed")
    # Check action types are registered
```

**Review execution details:**
```python
execution = executor.get_execution(execution_id)
for action in execution.actions:
    if action.status == ActionStatus.FAILED:
        print(f"Failed: {action.error}")
```

### CSV Headers Not Right

**Specify fields explicitly:**
```python
exporter.export_findings_to_csv(
    findings,
    "output.csv",
    include_fields=['id', 'title', 'severity', 'remediation']
)
```

---

## Performance Metrics

| Operation | Typical Time | Notes |
|-----------|------------|-------|
| JSON export | <100ms | Serialization only |
| CSV export | <200ms | Per 100 findings |
| HTML export | <500ms | Full report generation |
| Email send | <2s | Network dependent |
| Playbook validation | <50ms | Quick check |
| Playbook execution | 2-10s | Depends on actions |

---

## Next Steps

1. **Database Integration** (Phase 3)
   - Store reports in SQLite
   - Track remediation SLAs
   - Enable trend analysis

2. **Web Dashboard** (Phase 4)
   - Real-time report viewing
   - Interactive remediation approval
   - Team collaboration

3. **Advanced Integrations**
   - Jira ticket creation
   - Slack/Teams notifications
   - PagerDuty escalation

---

## Support & Questions

For issues or questions:
1. Check the troubleshooting section above
2. Review the test demo: `test_export_remediation.py`
3. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

---

Generated: February 7, 2026  
Version: 1.0
