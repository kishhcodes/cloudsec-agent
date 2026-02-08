# Email Configuration - Quick Reference Card

## ⚡ 5-Minute Setup

### 1️⃣ Pick Your Email Provider

| Provider | SMTP Server | Port | Setup Difficulty |
|----------|------------|------|-------------------|
| **Gmail** | smtp.gmail.com | 587 | Easy (App Password) |
| **Office 365** | smtp.office365.com | 587 | Easy |
| **AWS SES** | email-smtp.us-east-1.amazonaws.com | 587 | Medium |
| **Custom** | mail.yourcompany.com | 587 | Hard |

### 2️⃣ Set Environment Variables

**Gmail (Recommended for testing):**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # App Password!
```

**Office 365:**
```bash
export SMTP_SERVER="smtp.office365.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@outlook.com"
export SENDER_PASSWORD="your-password"
```

**AWS SES:**
```bash
export SMTP_SERVER="email-smtp.us-east-1.amazonaws.com"
export SMTP_PORT="587"
export SENDER_EMAIL="verified-email@example.com"
export SENDER_PASSWORD="ses-smtp-password"
```

### 3️⃣ Test It

```bash
python3 << 'EOF'
from src.audit.exporters import EmailService

email = EmailService()
config = email.test_connection()
print(f"✅ Connected!" if config['configured'] else f"❌ Failed: {config['status']}")
EOF
```

### 4️⃣ Send Your First Email

```python
from src.audit.exporters import EmailService

email = EmailService()
email.send_report(
    recipient_emails=["your-team@company.com"],
    subject="Test Email from Cloud Security Agent",
    html_content="<h1>Hello!</h1><p>Email is working!</p>"
)
```

---

## 🔧 Common Configurations

### Gmail (Easiest)

**Step 1:** Enable 2FA on Gmail  
**Step 2:** Get App Password: https://myaccount.google.com/security  
**Step 3:** Set env vars:
```bash
export SMTP_SERVER="smtp.gmail.com"
export SENDER_EMAIL="your@gmail.com"
export SENDER_PASSWORD="your-16-char-app-password"
```

### Office 365

```bash
export SMTP_SERVER="smtp.office365.com"
export SENDER_EMAIL="your@outlook.com"
export SENDER_PASSWORD="your-password"
```

### AWS SES

```bash
export SMTP_SERVER="email-smtp.us-east-1.amazonaws.com"
export SENDER_EMAIL="verified@example.com"
export SENDER_PASSWORD="your-ses-smtp-password"
```

---

## 📧 Email Commands

### Send Report
```python
email.send_report(
    recipient_emails=["user@company.com"],
    subject="Audit Report",
    html_content="<h1>Report</h1>..."
)
```

### Send with Attachment
```python
email.send_report_with_attachment(
    recipient_emails=["user@company.com"],
    subject="Report with PDF",
    html_content="See attached",
    report_file_path="reports/audit.pdf"
)
```

### Send Critical Alert
```python
email.send_critical_alert(
    recipient_emails=["ciso@company.com"],
    finding={"title": "Critical Issue", "severity": "CRITICAL"},
    severity_level="CRITICAL"
)
```

### Test Connection
```python
config = email.test_connection()
print(config['status'])  # "Connected" or error message
```

---

## 📅 Email Scheduling

### Schedule Daily Report
```python
from src.audit.exporters import EmailScheduler

email = EmailService()
scheduler = EmailScheduler(email)

scheduler.schedule_daily_report(
    schedule_id="daily-audit",
    recipient_emails=["team@company.com"],
    report_generator_func=generate_report,
    hour=9  # 9 AM daily
)
```

### Schedule Weekly Report
```python
scheduler.schedule_weekly_report(
    schedule_id="weekly-summary",
    recipient_emails=["executives@company.com"],
    report_generator_func=generate_summary,
    day_of_week=0,  # Monday
    hour=9
)
```

---

## 🆘 Troubleshooting

### "SMTP connection failed"
✅ Check email/password  
✅ Check firewall allows port 587  
✅ For Gmail, use App Password not regular password

### "Authentication failed"
✅ Verify email is correct  
✅ Verify password is correct  
✅ Gmail users: use 16-character App Password

### "Permission denied"
✅ Check firewall blocks port 587  
✅ Try port 25 (less secure)  
✅ Check SMTP server is correct

### Email not sending
✅ Check sender email is verified  
✅ Check recipient email is valid  
✅ Check SMTP credentials in env vars

---

## 🚀 CLI Integration

```bash
# Export report
python3 main_cli.py export --format html --report-id daily

# Send via email (when integrated)
python3 main_cli.py send-email --recipients team@company.com
```

---

## 🔒 Security Tips

✅ Use App Password for Gmail (not account password)  
✅ Store credentials in environment variables  
✅ Never commit passwords to git  
✅ Enable 2FA on email account  
✅ Use TLS encryption (port 587)  
✅ Monitor email delivery logs  

---

## 📝 Full Code Example

```python
from src.audit.exporters import EmailService, EmailScheduler
from src.agents.aws_security.agent import AWSSecurityAgent

# Initialize
email = EmailService()
agent = AWSSecurityAgent()

# Generate audit
findings = agent.analyze_storage_security()

# Send report
email.send_report(
    recipient_emails=["security@company.com"],
    subject="AWS Security Audit - Daily Report",
    html_content=f"<h1>Audit Results</h1><p>Found {len(findings)} issues</p>"
)

# Schedule daily
scheduler = EmailScheduler(email)
scheduler.schedule_daily_report(
    schedule_id="daily-aws-audit",
    recipient_emails=["team@company.com"],
    report_generator_func=agent.analyze_storage_security,
    hour=9
)
```

---

## 📚 Documentation

- Full Guide: `EMAIL_CONFIGURATION_GUIDE.md`
- Email Service: `src/audit/exporters/email_service.py`
- Test Results: `TEST_RESULTS_COMPREHENSIVE.md`

---

**Status:** ✅ Ready to configure  
**Default:** Gmail SMTP (port 587)  
**Time to Setup:** 5 minutes  
**Support:** See troubleshooting above
