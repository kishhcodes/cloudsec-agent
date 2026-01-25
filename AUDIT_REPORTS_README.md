# Comprehensive Audit Reports

## Overview

The Cloud Security Assistant now includes a comprehensive audit capability for both AWS and GCP environments. This feature allows you to perform full security audits that analyze multiple services and produce professional PDF reports.

## Features

### Audit Scope

The full audit covers the following areas:

**AWS Audit:**
- **IAM Security**: User accounts, roles, MFA status, password policies
- **S3 Security**: Public access, encryption, versioning
- **EC2 Security**: Instance monitoring, EBS encryption
- **VPC Security**: Security groups, VPC configuration, flow logs

**GCP Audit:**
- **IAM Security**: Service accounts, role assignments, security best practices
- **Cloud Storage Security**: Bucket access controls, versioning, encryption
- **Compute Engine Security**: Instance configurations, OS Login, service accounts
- **VPC/Network Security**: Firewall rules, VPC Flow Logs, Private Google Access

### Report Output

- **Console Summary**: Real-time summary of findings with statistics
- **PDF Report**: Professional, detailed audit report including:
  - Executive Summary
  - Finding Details (by severity level)
  - Remediation Roadmap
  - Best Practices
  - Recommendations

## Usage

### Triggering a Full Audit

#### From Main CLI

```bash
python main_cli.py

# When asked for input:
general> switch to aws-security
aws-security> perform a full audit

# OR

general> switch to gcp-security
gcp-security> perform a full audit
```

#### Programmatically

**AWS:**
```python
from aws_security_agent import AWSSecurityAgent

agent = AWSSecurityAgent(aws_profile="your-profile")
agent.start()

# Perform audit
audit_result = agent.perform_full_audit(export_pdf=True)
print(f"Report saved to: {audit_result['pdf_path']}")
```

**GCP:**
```python
from src.agents.gcp_security.agent import GCPSecurityAgent

agent = GCPSecurityAgent(project_id="your-project-id")

# Perform audit
audit_result = agent.perform_full_audit(export_pdf=True)
print(f"Report saved to: {audit_result['pdf_path']}")
```

## Finding Severity Levels

Findings are categorized by severity:

| Severity | Color | Description | Action Required |
|----------|-------|-------------|-----------------|
| **CRITICAL** | Red | Immediate security risk | Address within 24-48 hours |
| **HIGH** | Orange | Significant security issue | Address within 1-2 weeks |
| **MEDIUM** | Yellow | Moderate risk | Address within 1 month |
| **LOW** | Blue | Minor concern | Address within quarter |
| **PASS** | Green | Compliant/Best Practice | Continue monitoring |

## Report Structure

Each audit report includes:

### Executive Summary
- Report metadata (ID, date, project/account info)
- Finding statistics by severity
- Overall risk assessment

### Detailed Findings
For each finding:
- **Severity Level**: Visual indicator and text
- **Title**: Brief description
- **Description**: Detailed explanation
- **Recommendation**: Specific remediation steps

### Remediation Roadmap
Prioritized action plan:
- **Immediate (0-7 days)**: Critical findings
- **Short-term (1-4 weeks)**: High-risk findings
- **Medium-term (1-2 months)**: Medium-risk findings
- **Long-term (Ongoing)**: Continuous monitoring

## Examples

### AWS Audit Example

```bash
$ python main_cli.py
CloudAssistant CLI

general> switch to aws-security
✓ Switched to AWS Security Agent

aws-security> perform a full audit

[Starting Comprehensive AWS Audit...]

[Analyzing IAM Security...]
[Analyzing S3 Security...]
[Analyzing EC2 Security...]
[Analyzing VPC Security...]

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ AWS Audit Summary          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Critical Issues       │ 2   │
│ High Risk            │ 5   │
│ Medium Risk          │ 8   │
│ Low Risk             │ 3   │
│ Compliant Items      │ 12  │
└──────────────────────┴─────┘

✓ PDF report generated: reports/AWS-AUDIT-20250103-143022.pdf

aws-security> 
```

### GCP Audit Example

```bash
$ python main_cli.py
CloudAssistant CLI

general> switch to gcp-security
✓ Switched to GCP Security Agent

gcp-security> perform a full audit

[Starting Comprehensive GCP Audit...]

[Analyzing IAM Security...]
[Analyzing Cloud Storage Security...]
[Analyzing Compute Engine Security...]
[Analyzing VPC & Network Security...]

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ GCP Audit Summary          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Critical Issues       │ 1   │
│ High Risk            │ 3   │
│ Medium Risk          │ 6   │
│ Low Risk             │ 2   │
│ Compliant Items      │ 10  │
└──────────────────────┴─────┘

✓ PDF report generated: reports/GCP-AUDIT-20250103-143145.pdf

gcp-security> 
```

## PDF Report Features

### Professional Formatting
- **Branded header** with organization name
- **Page footer** with report ID and page numbers
- **Color-coded severity** indicators
- **Structured sections** for easy reading
- **Compliance-ready** format

### Report Contents

1. **Title Page**
   - Report title
   - Project/Account information
   - Report ID and generation timestamp
   - Confidentiality notice

2. **Executive Summary**
   - Audit scope overview
   - Finding statistics dashboard
   - Critical metrics at a glance

3. **Detailed Sections**
   - IAM Security Analysis
   - Storage Security Analysis
   - Compute Security Analysis
   - Network Security Analysis

4. **Remediation Roadmap**
   - Prioritized action items
   - Timeline-based milestones
   - Best practices guidance

## Finding Categories

### AWS IAM Findings Example

- ✅ Root account MFA status
- ✅ IAM user MFA compliance
- ✅ Password policy enforcement
- ✅ Access key age and rotation
- ✅ Unused accounts identification

### AWS S3 Findings Example

- ✅ Public bucket detection
- ✅ Encryption verification
- ✅ Versioning status
- ✅ Block Public Access settings
- ✅ Access logging configuration

### GCP IAM Findings Example

- ✅ Service account usage patterns
- ✅ Custom role creation
- ✅ Default service account protection
- ✅ Workload Identity configuration
- ✅ Key rotation policies

### GCP Storage Findings Example

- ✅ Uniform bucket-level access
- ✅ Object versioning status
- ✅ CMEK (Customer-Managed Encryption Key) usage
- ✅ Access log configuration
- ✅ Retention policies

## Query Patterns

The audit feature recognizes these query patterns:

```
"perform a full audit"
"perform full audit"
"full audit"
"run full audit"
"complete audit"
"comprehensive audit"
```

Any of these queries will trigger the comprehensive audit process.

## Output Files

Audit reports are saved to the `reports/` directory with the following naming convention:

- **AWS**: `AWS-AUDIT-YYYYMMDD-HHMMSS.pdf`
- **GCP**: `GCP-AUDIT-YYYYMMDD-HHMMSS.pdf`

Example: `AWS-AUDIT-20250103-143022.pdf`

## Performance Notes

- **Estimated Duration**: 2-5 minutes (depending on infrastructure size)
- **API Calls**: AWS audit makes ~15-20 AWS API calls
- **API Calls**: GCP audit makes ~10-15 GCP API calls
- **Requirements**: Valid AWS/GCP credentials with appropriate permissions

### Required AWS Permissions

For a complete audit, ensure your AWS credentials have these permissions:
- `iam:List*`
- `iam:Get*`
- `s3:List*`
- `s3:GetBucket*`
- `ec2:Describe*`

### Required GCP Permissions

For a complete audit, ensure your service account has:
- `resourcemanager.projects.get`
- `storage.buckets.list`
- `storage.buckets.get`
- `compute.instances.list`
- `compute.networks.list`

## Troubleshooting

### "Could not find project" Error

**AWS:**
```bash
export AWS_PROFILE=your-profile
# or
aws configure
```

**GCP:**
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
gcloud auth application-default login
```

### PDF Generation Fails

Ensure the `reports/` directory is writable:
```bash
chmod 755 reports/
```

### Missing Findings

Some findings require specific permissions. Check:
- AWS credentials have `iam:List*`, `s3:List*`, `ec2:Describe*` permissions
- GCP service account has required roles
- Rate limiting is not active

## Integration with CI/CD

You can integrate audits into your CI/CD pipeline:

```python
#!/usr/bin/env python3
"""Generate security audit as part of pipeline"""

from aws_security_agent import AWSSecurityAgent

def generate_audit_report():
    agent = AWSSecurityAgent()
    agent.start()
    
    audit_result = agent.perform_full_audit(export_pdf=True)
    
    # Store report
    pdf_path = audit_result['pdf_path']
    print(f"Audit report saved: {pdf_path}")
    
    # Check for critical issues
    summary = audit_result['summary']
    if summary['critical_issues'] > 0:
        print(f"ALERT: {summary['critical_issues']} critical issues found!")
        return False
    
    return True

if __name__ == "__main__":
    success = generate_audit_report()
    exit(0 if success else 1)
```

## Next Steps

1. **First Audit**: Run a full audit to baseline your infrastructure
2. **Review Report**: Examine the PDF report for findings
3. **Prioritize**: Start with CRITICAL and HIGH severity findings
4. **Remediate**: Follow the remediation roadmap in the report
5. **Reaudit**: Schedule regular audits (quarterly recommended)

## Support

For issues or questions about audit reports:

1. Check the troubleshooting section above
2. Verify AWS/GCP credentials and permissions
3. Review the PDF report for specific finding details
4. Consult GCP/AWS security best practices documentation

---

**Last Updated**: January 2025  
**Version**: 1.0
