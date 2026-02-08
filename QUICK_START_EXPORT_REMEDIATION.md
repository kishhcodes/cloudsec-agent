# Quick Start: Export & Remediation

**Get started in 5 minutes**

## 1️⃣ Export Audit Reports

### JSON (API Integration)
```python
from src.audit.exporters import JSONExporter

exporter = JSONExporter()
exporter.export_report(report_data, "report.json")
```

### CSV (Spreadsheet Analysis)
```python
from src.audit.exporters import CSVExporter

exporter = CSVExporter()
exporter.export_findings_to_csv(findings, "findings.csv")
exporter.export_remediation_tracker_to_csv(findings, "tracker.csv")
```

### HTML (Email Ready)
```python
from src.audit.exporters import HTMLExporter

exporter = HTMLExporter()
exporter.export_email_template(report_data, "email.html", "Alice Johnson")
```

## 2️⃣ Send Reports via Email

```python
from src.audit.exporters import EmailService

email_service = EmailService()
email_service.send_report_with_attachment(
    recipient_emails=["ciso@company.com"],
    subject="Security Audit Report",
    html_content=html_content,
    report_file_path="report.pdf"
)
```

**Setup:**
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password
```

## 3️⃣ Automate Remediation

### Use Pre-Built Playbook
```python
from src.remediation import PlaybookExecutor, PlaybookLibrary

executor = PlaybookExecutor()
playbooks = PlaybookLibrary.get_all_playbooks()

playbook = playbooks["AWS-PUBLIC-S3"]  # Fix public S3 bucket
execution = executor.execute_playbook(
    playbook,
    finding_data,
    initiated_by="admin@company.com"
)
```

### Create Custom Playbook
```python
from src.remediation import RemediationPlaybook

playbook = RemediationPlaybook(
    playbook_id="CUSTOM-001",
    name="My Remediation",
    description="Fix my finding",
    finding_category="Storage",
    severity="CRITICAL"
)

playbook.add_action(
    "block_public_access",
    "aws",
    {"service": "s3", "action": "put-public-access-block"}
)

playbook.requires_approval = True
```

## 4️⃣ Schedule Reports

```python
from src.audit.exporters import EmailScheduler

scheduler = EmailScheduler(email_service)

# Daily at 9 AM
scheduler.schedule_daily_report(
    "daily-executive",
    ["ciso@company.com"],
    generate_report_func,
    hour=9
)

# Weekly on Monday
scheduler.schedule_weekly_report(
    "weekly-audit",
    ["team@company.com"],
    generate_report_func,
    day_of_week=0
)
```

## 5️⃣ Check Execution History

```python
# Get history for a playbook
history = executor.get_execution_history(playbook_id="AWS-PUBLIC-S3")

# Get specific execution
execution = executor.get_execution(execution_id)
print(f"Status: {execution.status.value}")
print(f"Actions: {len(execution.actions)}")
```

---

## Standard Playbooks

| ID | Name | Severity |
|---|---|---|
| AWS-PUBLIC-S3 | Fix Public S3 | CRITICAL |
| AWS-EBS-ENCRYPTION | Enable EBS Encryption | HIGH |
| AWS-SG-RESTRICTION | Restrict Security Group | HIGH |
| GCP-PUBLIC-BUCKET | Restrict GCS Bucket | CRITICAL |
| AZURE-BLOB-PUBLIC | Restrict Blob Storage | CRITICAL |
| ENABLE-MFA | Enable MFA | CRITICAL |
| ENABLE-LOGGING | Enable Logging | MEDIUM |

**Get by category:** `PlaybookLibrary.get_playbook_by_category("Storage")`  
**Get by severity:** `PlaybookLibrary.get_playbooks_by_severity("CRITICAL")`

---

## Features Included

✅ **Multi-Format Export**
- JSON for API/CI-CD integration
- CSV for spreadsheet analysis  
- HTML with responsive email templates

✅ **Email Integration**
- SMTP configuration
- Attachment support
- Critical alert notifications

✅ **Report Scheduling**
- Daily, weekly schedules
- Automatic delivery
- Multiple recipients

✅ **Automated Remediation**
- 10 pre-built playbooks
- Approval workflows
- Dry-run testing
- Rollback support

✅ **Audit Logging**
- Execution history
- Action tracking
- Change documentation

---

## Full Documentation

See `EXPORT_REMEDIATION_GUIDE.md` for comprehensive API reference, advanced examples, and troubleshooting.

## Test Demo

Run all features:
```bash
python3 test_export_remediation.py
```

Generated files in `reports/`:
- `export_demo_report.json` - Full JSON export
- `export_demo_findings.csv` - Findings spreadsheet
- `export_demo_email.html` - Email template
- `export_demo_report.html` - Full HTML report
- More...

---

**Ready to use!** Import the modules and start exporting reports and automating remediation.
