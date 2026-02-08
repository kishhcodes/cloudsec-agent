# Integration Roadmap

**How to integrate Multi-Format Export & Remediation into your workflow**

---

## 🔗 Integration Points

### With Existing Audit Reports

```python
# In your audit report generation code
from src.audit import AWSAuditReport
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter, EmailService

# Generate audit
report = AWSAuditReport("123456789012")
report_data = report.generate()  # Returns dict with findings

# Export in all formats
json_exporter = JSONExporter()
csv_exporter = CSVExporter()
html_exporter = HTMLExporter()

json_exporter.export_report(report_data, f"reports/{account_id}.json")
csv_exporter.export_findings_to_csv(
    report_data['findings'], 
    f"reports/{account_id}_findings.csv"
)
html_exporter.export_email_template(
    report_data, 
    f"reports/{account_id}_email.html"
)

# Send via email
email = EmailService()
email.send_report_with_attachment(
    ["security@company.com"],
    f"Audit Report - {account_id}",
    open(f"reports/{account_id}_email.html").read(),
    f"reports/{account_id}.pdf"
)
```

### With Main CLI

Update `main_cli.py`:

```python
# Add to imports
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter, EmailService

# Add export commands
@app.command("export")
def export_report(
    format: str = typer.Option("json", help="Export format: json, csv, html"),
    report_id: str = typer.Option(..., help="Report ID to export"),
    output: str = typer.Option(None, help="Output file path")
):
    """Export audit report in multiple formats."""
    # Load report from cache/database
    report_data = load_report(report_id)
    
    if format == "json":
        exporter = JSONExporter()
        json_str = exporter.export_report(report_data, output)
        console.print(f"✅ Exported to {output or 'stdout'}")
    
    elif format == "csv":
        exporter = CSVExporter()
        exporter.export_findings_to_csv(report_data['findings'], output)
        console.print(f"✅ Findings exported to {output}")
    
    elif format == "html":
        exporter = HTMLExporter()
        exporter.export_email_template(report_data, output)
        console.print(f"✅ Email template exported to {output}")

@app.command("remediate")
def remediate_finding(
    finding_id: str = typer.Option(..., help="Finding ID"),
    auto: bool = typer.Option(False, help="Auto-execute without approval"),
    dry_run: bool = typer.Option(True, help="Test without making changes")
):
    """Execute remediation playbook for a finding."""
    from src.remediation import PlaybookExecutor, PlaybookLibrary
    
    executor = PlaybookExecutor()
    playbooks = PlaybookLibrary.get_all_playbooks()
    
    # Find playbook for finding
    finding = load_finding(finding_id)
    playbook = find_playbook(finding, playbooks)
    
    # Execute
    execution = executor.execute_playbook(
        playbook,
        finding,
        initiated_by=os.getenv("USER"),
        dry_run=dry_run
    )
    
    console.print(f"✅ Execution {execution.execution_id}: {execution.status.value}")
```

### With AWS Security Agent

```python
# In aws_security_agent.py
from src.audit.exporters import JSONExporter, EmailService

class AWSSecurityAgent:
    def __init__(self):
        # ... existing code ...
        self.json_exporter = JSONExporter()
        self.email_service = EmailService()
    
    def generate_and_export_report(self):
        """Generate report and export in all formats."""
        # Generate audit
        report_data = self._generate_audit_report()
        
        # Export
        self.json_exporter.export_report(
            report_data,
            f"reports/aws_{self.account_id}.json"
        )
        
        # Email executives
        if report_data['security_score'] < 60:
            self.email_service.send_critical_alert(
                ["ciso@company.com"],
                report_data['findings'][0],
                "CRITICAL"
            )
```

### With GCP Security Agent

```python
# In gcp_security_agent.py
from src.remediation import PlaybookExecutor, PlaybookLibrary

class GCPSecurityAgent:
    def __init__(self):
        # ... existing code ...
        self.playbook_executor = PlaybookExecutor()
        self.playbooks = PlaybookLibrary.get_playbooks_by_category("Storage")
    
    def auto_remediate(self, findings):
        """Auto-remediate GCP findings where possible."""
        for finding in findings:
            if finding['severity'] == 'CRITICAL':
                playbook = self.playbooks.get(
                    f"GCP-{finding['category'].upper()}"
                )
                if playbook:
                    execution = self.playbook_executor.execute_playbook(
                        playbook,
                        finding,
                        initiated_by="automated"
                    )
```

### With Compliance Bot

```python
# In compliance_assistant.py
from src.audit.exporters import HTMLExporter

class ComplianceAssistant:
    def generate_compliance_report(self):
        """Generate compliance report with HTML export."""
        compliance_data = self._analyze_compliance()
        
        html_exporter = HTMLExporter()
        html_exporter.export_executive_summary_html(
            compliance_data,
            "reports/compliance_summary.html"
        )
```

---

## 🛠️ Step-by-Step Integration

### Step 1: Add to Your Audit Pipeline

```python
def audit_cloud_account(account_id):
    # Generate audit
    report = AWSAuditReport(account_id)
    findings = report.analyze()
    
    # Export results
    from src.audit.exporters import JSONExporter, CSVExporter
    
    json_exp = JSONExporter()
    csv_exp = CSVExporter()
    
    json_exp.export_report(findings, f"reports/{account_id}.json")
    csv_exp.export_findings_to_csv(findings['findings'], f"reports/{account_id}.csv")
```

### Step 2: Add Email Delivery

```python
# Configure SMTP
os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
os.environ['SENDER_EMAIL'] = 'audit@company.com'
os.environ['SENDER_PASSWORD'] = 'app_password'

# Send report
from src.audit.exporters import EmailService

email = EmailService()
email.send_report_with_attachment(
    ["team@company.com"],
    "Daily Audit Report",
    html_content,
    "report.pdf"
)
```

### Step 3: Add Scheduled Delivery

```python
from src.audit.exporters import EmailScheduler

scheduler = EmailScheduler(email)
scheduler.schedule_daily_report(
    "daily-audit",
    ["ciso@company.com"],
    lambda: generate_daily_audit(),
    hour=6
)

scheduler.schedule_weekly_report(
    "weekly-summary",
    ["security@company.com"],
    lambda: generate_weekly_summary(),
    day_of_week=0,  # Monday
    hour=9
)
```

### Step 4: Add Remediation Automation

```python
from src.remediation import PlaybookExecutor, PlaybookLibrary

executor = PlaybookExecutor()
playbooks = PlaybookLibrary.get_all_playbooks()

for finding in critical_findings:
    playbook = find_matching_playbook(finding, playbooks)
    if playbook:
        execution = executor.execute_playbook(
            playbook,
            finding,
            initiated_by="automation"
        )
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Audit Generation                             │
│        (AWS/GCP/Azure Agents + Compliance Analyzer)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Report Data  │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐      ┌──────────┐
   │ JSON    │        │ CSV     │      │ HTML     │
   │Exporter │        │Exporter │      │Exporter  │
   └────┬────┘        └────┬────┘      └────┬─────┘
        │                  │                │
        ▼                  ▼                ▼
   ┌─────────┐        ┌─────────┐      ┌──────────┐
   │JSON File│        │CSV File │      │HTML File │
   └────┬────┘        └────┬────┘      └────┬─────┘
        │                  │                │
        └──────────────────┼────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Email Service │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌──────────┐      ┌──────────┐      ┌─────────┐
   │Scheduled │      │Immediate │      │Critical │
   │Delivery  │      │Send      │      │Alert    │
   └──────────┘      └──────────┘      └─────────┘
        │                  │                │
        └──────────────────┼────────────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │     Executive Summary         │
        │ Remediation Tracker CSV       │
        │ API Integration JSON          │
        │ Email to Team                 │
        └──────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │  Playbook Executor Detects   │
        │  Critical Findings           │
        └──────────┬───────────────────┘
                   │
        ┌──────────┴──────────────────┐
        ▼                             ▼
   ┌──────────────┐          ┌──────────────┐
   │Get Playbook  │          │Needs Approval│
   │for Finding   │          │from Manager  │
   └──────┬───────┘          └──────┬───────┘
          │                         │
          ▼                         ▼
    ┌──────────────┐        ┌──────────────┐
    │Dry-Run Test  │        │Send Alert    │
    │(optional)    │        │to Approver   │
    └──────┬───────┘        └──────┬───────┘
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Manager Approves/Rejects    │
        │  Via Email or Dashboard      │
        └──────────┬───────────────────┘
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
   ┌──────────────┐        ┌──────────────┐
   │Execute       │        │Log Rejection │
   │Remediation   │        │Archive Audit │
   └──────┬───────┘        └──────────────┘
          │
          ▼
   ┌──────────────┐
   │Update Status │
   │Send Summary  │
   │Audit Trail   │
   └──────────────┘
```

---

## 🧪 Testing Integration

```python
# test_integration.py
def test_full_workflow():
    """Test complete export + remediation workflow."""
    
    # 1. Generate report
    report = create_test_report()
    
    # 2. Export formats
    from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
    
    json_exp = JSONExporter()
    json_str = json_exp.export_report(report)
    assert "metadata" in json.loads(json_str)
    
    # 3. Remediate
    from src.remediation import PlaybookExecutor, PlaybookLibrary
    
    executor = PlaybookExecutor()
    playbooks = PlaybookLibrary.get_all_playbooks()
    playbook = playbooks["AWS-PUBLIC-S3"]
    
    execution = executor.execute_playbook(
        playbook,
        report['findings'][0],
        "test_user",
        dry_run=True
    )
    
    assert execution.status == PlaybookStatus.PENDING
    assert len(execution.actions) > 0
```

---

## 📝 Next Actions

1. **Update main_cli.py** - Add export and remediation commands
2. **Configure Email** - Set SMTP environment variables
3. **Test with Real Data** - Run against production accounts (dry-run first)
4. **Deploy Scheduler** - Set up automated email delivery
5. **Team Training** - Show team how to use new features

---

See `EXPORT_REMEDIATION_GUIDE.md` for complete API reference and advanced integration patterns.
