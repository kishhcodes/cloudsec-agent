# Integration Checklist - Quick Reference

## ✅ Completed Components

- [x] JSONExporter (src/audit/exporters/json_exporter.py)
- [x] CSVExporter (src/audit/exporters/csv_exporter.py)
- [x] HTMLExporter (src/audit/exporters/html_exporter.py)
- [x] EmailService (src/audit/exporters/email_service.py)
- [x] RemediationPlaybook (src/remediation/playbook_engine.py)
- [x] PlaybookExecutor (src/remediation/playbook_engine.py)
- [x] PlaybookLibrary (src/remediation/playbook_library.py)
- [x] Complete documentation and guides

## ⏳ Pending Integration Tasks

### Task 1: Update src/audit/__init__.py (5 minutes)

**File**: `/home/vboxuser/projects/cloudsec-agent/src/audit/__init__.py`

**Add these lines after existing imports:**

```python
from .exporters import (
    JSONExporter,
    CSVExporter,
    HTMLExporter,
    EmailService,
    EmailScheduler
)
```

**Update __all__:**

```python
__all__ = [
    'AuditReport',
    'AWSAuditReport',
    'GCPAuditReport',
    'AzureAuditReport',
    'AuditHeader',
    'AuditFooter',
    'ChartGenerator',
    'ComplianceMapper',
    'JSONExporter',
    'CSVExporter',
    'HTMLExporter',
    'EmailService',
    'EmailScheduler',
]
```

---

### Task 2: Add CLI Commands to main_cli.py (2-3 hours)

**File**: `/home/vboxuser/projects/cloudsec-agent/main_cli.py`

**Add these imports:**

```python
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter, EmailService
from src.remediation import PlaybookExecutor, PlaybookLibrary
```

**Add these commands:**

```python
@app.command("export")
def export_report(
    format: str = typer.Option("json", help="Format: json, csv, html"),
    output: str = typer.Option(None, help="Output file path"),
):
    """Export audit report in multiple formats."""
    console.print("[yellow]Not yet implemented - select a report first[/yellow]")

@app.command("remediate")
def remediate_finding(
    finding_id: str = typer.Option(..., help="Finding ID"),
    dry_run: bool = typer.Option(True, help="Test without executing"),
):
    """Execute remediation playbook for a finding."""
    executor = PlaybookExecutor()
    console.print(f"[yellow]Remediation for {finding_id} (dry-run: {dry_run})[/yellow]")

@app.command("playbook-list")
def list_playbooks(
    category: str = typer.Option(None, help="Filter by category"),
    severity: str = typer.Option(None, help="Filter by severity"),
):
    """List available remediation playbooks."""
    playbooks = PlaybookLibrary.get_all_playbooks()
    
    table = Table(title="Available Remediation Playbooks")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Severity", style="red")
    table.add_column("Description", style="green")
    
    for name, playbook in playbooks.items():
        table.add_row(
            name,
            playbook.category,
            playbook.severity.value if hasattr(playbook, 'severity') else "N/A",
            playbook.description[:50] + "..." if len(playbook.description) > 50 else playbook.description
        )
    
    console.print(table)

@app.command("schedule-report")
def schedule_report(
    frequency: str = typer.Option("daily", help="Frequency: daily, weekly"),
    email: str = typer.Option(..., help="Email recipient"),
    hour: int = typer.Option(6, help="Hour (0-23)"),
):
    """Schedule automated report delivery."""
    console.print(f"[yellow]Scheduling {frequency} report to {email} at {hour}:00[/yellow]")
```

---

### Task 3: Integrate AWS Agent (1-2 hours)

**File**: `/home/vboxuser/projects/cloudsec-agent/aws_security_agent.py`

**Add to imports:**

```python
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
```

**Add to AWSSecurityAgent.__init__():**

```python
self.json_exporter = JSONExporter()
self.csv_exporter = CSVExporter()
self.html_exporter = HTMLExporter()
```

**Add method:**

```python
def export_reports(self, report_data):
    """Export report in all formats."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    account_id = self.aws_account_id
    
    # JSON export
    self.json_exporter.export_report(
        report_data,
        f"reports/AWS_AUDIT_{account_id}_{timestamp}.json"
    )
    
    # CSV exports
    self.csv_exporter.export_findings_to_csv(
        report_data.get('findings', []),
        f"reports/AWS_FINDINGS_{account_id}_{timestamp}.csv"
    )
    
    # HTML export
    self.html_exporter.export_email_template(
        report_data,
        f"reports/AWS_REPORT_{account_id}_{timestamp}.html"
    )
```

---

### Task 4: Integrate GCP Agent (1-2 hours)

**File**: `/home/vboxuser/projects/cloudsec-agent/src/agents/gcp_security/agent.py`

**Same pattern as AWS Agent** - Add exporters and export method

---

### Task 5: Integrate Azure Agent (1-2 hours)

**File**: `/home/vboxuser/projects/cloudsec-agent/src/agents/azure_security/agent.py`

**Same pattern as AWS Agent** - Add exporters and export method

---

### Task 6: Email Configuration (30 minutes)

**File**: `.env` (in project root)

**Add SMTP configuration:**

```bash
# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# OR Office 365
# SMTP_SERVER=smtp.office365.com
# SMTP_PORT=587
# SENDER_EMAIL=your-email@company.com
# SENDER_PASSWORD=your-password

# OR AWS SES
# SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
# SMTP_PORT=587
# SENDER_EMAIL=your-email@company.com
# SENDER_PASSWORD=your-password
```

**Test connection:**

```python
from src.audit.exporters import EmailService

service = EmailService()
result = service.test_connection()
print(result)
```

---

## Verification Checklist

### After Task 1 (Module Exports)
- [ ] `python -c "from src.audit.exporters import JSONExporter; print('✓ Import works')"`
- [ ] All 4 exporters importable

### After Task 2 (CLI Integration)
- [ ] `python main_cli.py --help` shows new commands
- [ ] `python main_cli.py export --help` works
- [ ] `python main_cli.py remediate --help` works
- [ ] `python main_cli.py playbook-list` displays playbooks

### After Task 3-5 (Agent Integration)
- [ ] Agents have export methods
- [ ] Reports generated in all 4 formats
- [ ] File sizes are reasonable

### After Task 6 (Email Setup)
- [ ] `python test_export_remediation.py` sends test email
- [ ] SMTP credentials work correctly
- [ ] Email received successfully

---

## Quick Test Commands

```bash
# Test exporters
python -c "from src.audit.exporters import JSONExporter; print(JSONExporter.__doc__)"

# Test playbooks
python -c "from src.remediation import PlaybookLibrary; print(list(PlaybookLibrary.get_all_playbooks().keys()))"

# Run integration test
python test_export_remediation.py

# List playbooks via CLI
python main_cli.py playbook-list

# Export a report
python main_cli.py export --format json --output report.json
```

---

## Files to Review

1. **EXPORT_REMEDIATION_GUIDE.md** - Complete API reference
2. **QUICK_START_EXPORT_REMEDIATION.md** - 5-minute setup
3. **INTEGRATION_GUIDE.md** - Copy-paste code examples
4. **INTEGRATION_STATUS.md** - Detailed status report (this repo)

---

## Estimated Effort

| Task | Duration | Difficulty |
|------|----------|-----------|
| Module Exports | 5 min | Easy |
| CLI Integration | 2-3 hrs | Medium |
| AWS Agent | 1-2 hrs | Medium |
| GCP Agent | 1-2 hrs | Medium |
| Azure Agent | 1-2 hrs | Medium |
| Email Setup | 30 min | Easy |
| **TOTAL** | **6-8 hrs** | - |

---

## Success Criteria

All of the following must work:

- [ ] JSONExporter exports reports to JSON
- [ ] CSVExporter exports findings to CSV
- [ ] HTMLExporter exports to HTML
- [ ] EmailService sends emails (if configured)
- [ ] CLI export command works
- [ ] CLI remediate command works
- [ ] CLI playbook-list works
- [ ] All agents support export
- [ ] Tests pass: `python test_export_remediation.py`

---

## Support Files

If you get stuck on any task:

1. See **INTEGRATION_GUIDE.md** for code examples
2. Check **EXPORT_REMEDIATION_GUIDE.md** for API docs
3. Run **test_export_remediation.py** to verify components work
4. Review specific exporter code (json_exporter.py, etc.)

---

## Next Phase: Phase 3 (Database Storage)

After integration is complete, Phase 3 will add:

- [ ] SQLite storage for audit reports
- [ ] History tracking and queries
- [ ] Report comparison and trends
- [ ] Remediation execution logs
- [ ] SLA monitoring

---

**Last Updated**: February 7, 2026
**Status**: Ready for integration
**Time to Complete**: 6-8 hours

