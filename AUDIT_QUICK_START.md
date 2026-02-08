# Quick Start: Full Audit Reports

## 30-Second Summary

Run comprehensive security audits for AWS or GCP and generate professional PDF reports.

```bash
# For AWS
python main_cli.py
general> switch to aws-security
aws-security> perform a full audit

# For GCP
python main_cli.py
general> switch to gcp-security
gcp-security> perform a full audit
```

Reports are saved to `reports/` directory.

## What Gets Audited

### AWS
- ✅ IAM (users, roles, MFA, passwords)
- ✅ S3 (buckets, encryption, versioning, public access)
- ✅ EC2 (instances, monitoring, EBS)
- ✅ VPC (security groups, flow logs)

### GCP
- ✅ IAM (service accounts, roles)
- ✅ Cloud Storage (buckets, access controls, versioning)
- ✅ Compute Engine (instances, security)
- ✅ VPC & Networking (firewall, flow logs)

## Output

**Console**: Real-time progress + summary statistics

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ AWS Audit Summary          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Critical Issues       │ 2   │
│ High Risk            │ 5   │
│ Medium Risk          │ 8   │
│ Low Risk             │ 3   │
│ Compliant Items      │ 12  │
└──────────────────────┴─────┘
```

**PDF Report**: Professional audit document with:
- Executive summary
- Detailed findings by severity
- Remediation roadmap
- Best practices

Example: `AWS-AUDIT-20250103-143022.pdf`

## Requirements

### AWS
```bash
export AWS_PROFILE=your-profile
# or just: aws configure
```

### GCP
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
gcloud auth application-default login
```

## Finding Severity

| Level | Time to Fix |
|-------|------------|
| 🔴 CRITICAL | 24-48 hours |
| 🟠 HIGH | 1-2 weeks |
| 🟡 MEDIUM | 1 month |
| 🔵 LOW | Quarter |
| ✅ PASS | Maintain |

## Common Examples

### AWS IAM Findings
- Root account MFA not enabled ⚠️ CRITICAL
- Users without MFA ⚠️ HIGH
- Old access keys ⚠️ MEDIUM

### AWS S3 Findings
- Publicly accessible buckets ⚠️ CRITICAL
- Unencrypted buckets ⚠️ HIGH
- No versioning enabled ⚠️ MEDIUM

### GCP IAM Findings
- Using default service account ⚠️ HIGH
- Workload Identity not configured ⚠️ MEDIUM

### GCP Storage Findings
- Uniform bucket access not enforced ⚠️ CRITICAL
- Versioning disabled ⚠️ MEDIUM

## File Locations

Reports: `reports/`

Each report includes:
- PDF file: `{PROVIDER}-AUDIT-{TIMESTAMP}.pdf`
- Report ID: Unique identifier in filename

## Timing

- Execution time: 2-5 minutes
- Depends on infrastructure size
- AWS: ~15-20 API calls
- GCP: ~10-15 API calls

## Next: Remediation

After reviewing your audit report:

1. **Prioritize**: Focus on CRITICAL and HIGH severity
2. **Create tickets**: For each finding
3. **Follow roadmap**: Use the remediation timeline
4. **Reaudit**: After fixes (quarterly minimum)

## Troubleshooting

### AWS Credentials Not Found
```bash
aws configure
# or
export AWS_PROFILE=your-profile
```

### GCP Project Not Set
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
gcloud auth application-default login
```

### Reports Directory Permission Error
```bash
mkdir -p reports
chmod 755 reports
```

## Integration Examples

### Schedule Regular Audits
```bash
# Run audit monthly
0 0 1 * * cd /path/to/cloudsec-agent && ./run_audit.sh
```

### Script Usage
```python
from aws_security_agent import AWSSecurityAgent

agent = AWSSecurityAgent()
agent.start()
result = agent.perform_full_audit(export_pdf=True)
print(result['pdf_path'])
```

---

For detailed information, see `AUDIT_REPORTS_README.md`
