# Email Configuration Guide - SMTP Setup

**Last Updated:** February 7, 2026

---

## Quick Setup (5 minutes)

### Step 1: Set Environment Variables

Choose your email provider and set these environment variables:

#### Option A: Gmail
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
```

**Note:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password!

#### Option B: Microsoft Outlook/Office 365
```bash
export SMTP_SERVER="smtp.office365.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@outlook.com"
export SENDER_PASSWORD="your-password"
```

#### Option C: AWS SES (Simple Email Service)
```bash
export SMTP_SERVER="email-smtp.us-east-1.amazonaws.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-verified-email@example.com"
export SENDER_PASSWORD="your-ses-smtp-password"
```

#### Option D: Custom SMTP Server
```bash
export SMTP_SERVER="mail.yourcompany.com"
export SMTP_PORT="587"
export SENDER_EMAIL="security-alerts@yourcompany.com"
export SENDER_PASSWORD="your-password"
```

### Step 2: Verify Configuration

Test your setup:
```bash
python3 -c "
from src.audit.exporters import EmailService
email = EmailService()
config = email.test_connection()
print(f'Status: {config[\"status\"]}')
print(f'Server: {config[\"smtp_server\"]}')
print(f'Email: {config[\"sender_email\"]}')
"
```

### Step 3: Use in Your Code

```python
from src.audit.exporters import EmailService

email = EmailService()
email.send_report(
    recipient_emails=["team@company.com"],
    subject="Daily Security Audit Report",
    html_content="<h1>Audit Report</h1>..."
)
```

---

## Detailed Configuration

### Email Configuration Class

**File:** `src/audit/exporters/email_service.py`

```python
class EmailService:
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None
    ):
        """
        Initialize the email service.
        
        Args:
            smtp_server: SMTP server address (default: from env var)
            smtp_port: SMTP port (default: 587)
            sender_email: Sender email (default: from env var)
            sender_password: Password/API key (default: from env var)
        """
```

### Configuration Priority

The EmailService looks for configuration in this order:

1. **Constructor Parameters** (highest priority)
   ```python
   email = EmailService(
       smtp_server="smtp.gmail.com",
       sender_email="user@gmail.com",
       sender_password="app-password"
   )
   ```

2. **Environment Variables** (recommended)
   ```bash
   export SMTP_SERVER="smtp.gmail.com"
   export SENDER_EMAIL="user@gmail.com"
   export SENDER_PASSWORD="app-password"
   ```

3. **Defaults** (lowest priority)
   - SMTP_SERVER: "smtp.gmail.com"
   - SMTP_PORT: 587

---

## Email Service Methods

### Send Report

```python
email.send_report(
    recipient_emails=["user@company.com"],
    subject="Audit Report",
    html_content="<h1>Report</h1>...",
    attachments=["report.pdf"],
    cc=["manager@company.com"],
    bcc=["archive@company.com"],
    reply_to="noreply@company.com"
)
```

### Send Critical Alert

```python
email.send_critical_alert(
    recipient_emails=["ciso@company.com"],
    finding={
        "id": "FIND-001",
        "title": "Critical: Public S3 Bucket",
        "severity": "CRITICAL"
    },
    severity_level="CRITICAL"
)
```

### Send with Attachment

```python
email.send_report_with_attachment(
    recipient_emails=["team@company.com"],
    subject="Weekly Report",
    html_content="<h1>Report</h1>...",
    report_file_path="reports/audit.pdf",
    report_format="pdf"
)
```

### Test Connection

```python
config = email.test_connection()
print(f"Connected: {config['configured']}")
print(f"Server: {config['smtp_server']}")
print(f"Status: {config['status']}")
```

---

## Email Scheduling

### Setup Daily Report

```python
from src.audit.exporters import EmailScheduler

email = EmailService()
scheduler = EmailScheduler(email)

scheduler.schedule_daily_report(
    schedule_id="daily-audit",
    recipient_emails=["team@company.com"],
    report_generator_func=generate_daily_audit,
    hour=9  # Send at 9 AM
)
```

### Setup Weekly Report

```python
scheduler.schedule_weekly_report(
    schedule_id="weekly-summary",
    recipient_emails=["executives@company.com"],
    report_generator_func=generate_weekly_summary,
    day_of_week=0,  # Monday (0=Monday, 6=Sunday)
    hour=9
)
```

### List Active Schedules

```python
schedules = scheduler.list_schedules()
for schedule_id, schedule_info in schedules.items():
    print(f"{schedule_id}: {schedule_info}")
```

### Disable Schedule

```python
scheduler.disable_schedule("daily-audit")
```

---

## CLI Integration

### Export and Email Report

```bash
# Export to HTML and email
python3 main_cli.py export --format html --report-id daily-audit

# Then send via CLI (when integrated)
python3 main_cli.py send-email --report-id daily-audit \
  --recipients team@company.com,manager@company.com
```

---

## Provider-Specific Setup

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Google Account
2. **Create App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Select "App Passwords"
   - Choose Mail and Windows Computer
   - Copy the generated password

3. **Configure:**
   ```bash
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   export SENDER_EMAIL="your-email@gmail.com"
   export SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # App password (16 chars)
   ```

### Office 365 Setup

1. **Enable SMTP Authentication** in Exchange Admin
2. **Verify Email Address** in Office 365
3. **Configure:**
   ```bash
   export SMTP_SERVER="smtp.office365.com"
   export SMTP_PORT="587"
   export SENDER_EMAIL="your-email@outlook.com"
   export SENDER_PASSWORD="your-password"
   ```

### AWS SES Setup

1. **Verify Email Address:**
   ```bash
   aws ses verify-email-identity --email-address your@example.com
   ```

2. **Create SMTP Credentials:**
   - Go to AWS SES Console
   - Get SMTP username and password (NOT AWS Access Key)

3. **Configure:**
   ```bash
   export SMTP_SERVER="email-smtp.us-east-1.amazonaws.com"
   export SMTP_PORT="587"
   export SENDER_EMAIL="your@example.com"
   export SENDER_PASSWORD="ses-smtp-password"
   ```

---

## Troubleshooting

### Issue: "SMTP connection failed"

**Solution:** Verify credentials and check firewall

```bash
# Test SMTP connection
python3 -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'app-password')
    print('✅ Connection successful!')
    server.quit()
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Issue: "Authentication failed"

**Checklist:**
- [ ] Email address is correct
- [ ] Password is correct (use App Password for Gmail)
- [ ] SMTP server is correct
- [ ] Firewall allows port 587

### Issue: "Permission denied / TLS error"

**Solution:** Check firewall and port

```bash
# Test if port is accessible
telnet smtp.gmail.com 587

# Or use nc
nc -zv smtp.gmail.com 587
```

### Issue: "Email not sending"

**Debug:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

email = EmailService()
result = email.send_report(
    recipient_emails=["test@example.com"],
    subject="Test",
    html_content="Test email"
)
print(f"Result: {result}")
```

---

## Security Best Practices

### ✅ DO:
- ✅ Use App Passwords (Gmail)
- ✅ Enable 2FA on email account
- ✅ Use environment variables (not hardcoded)
- ✅ Restrict email service permissions
- ✅ Monitor email delivery logs
- ✅ Use TLS encryption (port 587)

### ❌ DON'T:
- ❌ Hardcode passwords in code
- ❌ Commit credentials to git
- ❌ Use plain text passwords
- ❌ Share credentials in Slack/email
- ❌ Use old/unsupported SMTP ports
- ❌ Disable TLS for security

---

## Integration with Cloud Agents

### AWS Agent Email Integration

```python
from src.agents.aws_security.agent import AWSSecurityAgent
from src.audit.exporters import EmailService

agent = AWSSecurityAgent(aws_profile="production")
findings = agent.analyze_storage_security()

# Export and email report
email = EmailService()
email.send_report(
    recipient_emails=["security@company.com"],
    subject="AWS Storage Security Report",
    html_content=agent.export_report(findings, format="html")
)
```

### GCP Agent Email Integration

```python
from src.agents.gcp_security.agent import GCPSecurityAgent
from src.audit.exporters import EmailService

agent = GCPSecurityAgent(project_id="my-project")
findings = agent.analyze_iam_security()

email = EmailService()
email.send_report_with_attachment(
    recipient_emails=["team@company.com"],
    subject="GCP Security Audit",
    html_content="Security audit completed",
    report_file_path="reports/gcp_audit.pdf"
)
```

### Azure Agent Email Integration

```python
from src.agents.azure_security.agent import AzureSecurityAgent
from src.audit.exporters import EmailService

agent = AzureSecurityAgent(subscription_id="sub-123")
findings = agent.analyze_entra_id_security()

email = EmailService()
email.send_critical_alert(
    recipient_emails=["admin@company.com"],
    finding=findings[0],
    severity_level="CRITICAL"
)
```

---

## Example: Complete Setup Script

```bash
#!/bin/bash
# setup_email.sh

# Set email configuration
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="security-alerts@company.com"
export SENDER_PASSWORD="your-app-password"

# Test configuration
echo "Testing email configuration..."
python3 << 'EOF'
from src.audit.exporters import EmailService

email = EmailService()
config = email.test_connection()

if config['configured']:
    print("✅ Email configured successfully!")
    print(f"   Server: {config['smtp_server']}")
    print(f"   Email: {config['sender_email']}")
else:
    print("❌ Email configuration failed!")
    print(f"   Error: {config['status']}")
EOF
```

Run it:
```bash
bash setup_email.sh
```

---

## Next Steps

1. ✅ Choose your email provider
2. ✅ Get/create SMTP credentials
3. ✅ Set environment variables
4. ✅ Test connection
5. ✅ Send test email
6. ✅ Set up scheduling (optional)
7. ✅ Integrate with agents

---

## Support

For issues:
1. Check the Troubleshooting section above
2. Review `src/audit/exporters/email_service.py`
3. Check logs: `python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)"`
4. Verify credentials are correct

---

**Email Service Status:** ✅ Ready to configure  
**Default SMTP:** smtp.gmail.com (port 587)  
**Supported Providers:** Gmail, Office 365, AWS SES, Custom SMTP  
**TLS Encryption:** Enabled by default
