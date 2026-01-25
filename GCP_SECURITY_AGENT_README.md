# Google Cloud Platform Security Agent

## Overview

The GCP Security Agent provides comprehensive security analysis and recommendations for Google Cloud Platform resources. It supports:

- **IAM Security**: Analyze role-based access control and permissions
- **Cloud Storage**: Security assessment of Cloud Storage buckets
- **Compute Engine**: Review instance security configurations
- **Cloud SQL**: Database security recommendations
- **VPC & Networking**: Network security analysis

## Features

### 1. IAM Security Analysis
- Detect overly permissive roles
- Identify external user access
- Service account analysis
- Binding security review

**Example Queries**:
- "Check my IAM security"
- "Analyze IAM permissions"
- "List service accounts with excessive permissions"

### 2. Cloud Storage Security
- Versioning status checks
- Encryption validation
- Public access detection
- Bucket policy analysis
- Risk assessment per bucket

**Example Queries**:
- "Analyze my Cloud Storage buckets"
- "Check bucket encryption"
- "List public buckets"

### 3. Compute Engine Security
- Instance security review
- Public IP detection
- Service account assessment
- Metadata server configuration
- Disk encryption checks

**Example Queries**:
- "Review my Compute Engine instances"
- "Find instances with public IPs"
- "Check service account configurations"

### 4. Cloud SQL Security
- Connection security recommendations
- Backup configuration
- User access review
- Database flag recommendations

**Example Queries**:
- "Check Cloud SQL security"
- "Review database access"

### 5. VPC & Network Security
- Firewall rule analysis
- VPC configuration review
- NAT configuration
- Service controls setup

**Example Queries**:
- "Analyze my VPC configuration"
- "Check firewall rules"
- "Review network security"

## Setup & Configuration

### Prerequisites

1. **Google Cloud Project**: Active GCP project
2. **Service Account**: GCP service account with appropriate permissions
3. **Authentication**: Application Default Credentials set up

### Installation

1. Install GCP-specific dependencies:
```bash
pip install -r requirements.txt
```

Or specifically install GCP libraries:
```bash
pip install google-cloud-storage \
            google-cloud-compute \
            google-cloud-resource-manager \
            google-cloud-sql \
            google-cloud-iam-credentials
```

2. Set up authentication:
```bash
# Option 1: Using gcloud
gcloud auth application-default login

# Option 2: Using service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

3. Set your GCP project ID:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
```

4. Set your Google API key (for Gemini LLM):
```bash
export GOOGLE_API_KEY=your-api-key
```

### Required GCP Permissions

Your service account needs the following roles:

```yaml
roles:
  - roles/iam.securityReviewer       # For IAM analysis
  - roles/storage.admin              # For Storage analysis
  - roles/compute.viewer             # For Compute analysis
  - roles/cloudsql.viewer            # For SQL analysis
  - roles/viewer                     # For general resource viewing
```

Or create a custom role with these permissions:
- `iam.roles.list`
- `iam.serviceAccounts.list`
- `storage.buckets.list`
- `storage.buckets.getIamPolicy`
- `compute.instances.list`
- `cloudsql.instances.list`

## Usage

### Standalone CLI

Run the GCP Security Agent as a standalone CLI:

```bash
python gcp_security_agent.py
```

Then interact with natural language queries:
```
GCP Security> Check my IAM security
GCP Security> Analyze my Cloud Storage buckets
GCP Security> Review Compute Engine instances
```

### Integrated with Main CLI

Access the GCP agent from the unified CLI:

```bash
python main_cli.py
```

Then switch to the GCP agent:
```
general> switch to gcp
general> switch to gcp-security
general> switch to google cloud
```

### Programmatic Usage

```python
from src.agents.gcp_security.agent import GCPSecurityAgent

# Initialize the agent
agent = GCPSecurityAgent(project_id="my-project")

# Analyze IAM security
iam_analysis = agent.analyze_iam_security()
print(iam_analysis)

# Analyze storage security
storage_analysis = agent.analyze_storage_security()
print(storage_analysis)

# Process natural language query
result = agent.process_command("Check my Cloud Storage buckets")
print(result)
```

## Sample Output

### IAM Security Analysis
```
Analyzing IAM Security...

IAM Security Analysis for my-project

Security Findings:
1. Overly permissive role roles/editor assigned to allUsers
   Severity: Critical
   Recommendation: Remove public access immediately

IAM Statistics:
Total role bindings: 15
Service accounts: 3
External users: 2
```

### Storage Security Analysis
```
Analyzing Cloud Storage Security...

Bucket Security Status

┌──────────────────┬────────────┬────────────┬──────────────┬──────────────┐
│ Bucket Name      │ Versioning │ Encryption │ Public Access│ Risk Level   │
├──────────────────┼────────────┼────────────┼──────────────┼──────────────┤
│ prod-data        │ ✓ Enabled  │ ✓ Enabled  │ ✓ Private    │ Low          │
│ logs-archive     │ ✗ Disabled │ ✓ Enabled  │ ✓ Private    │ Medium       │
│ public-assets    │ ✓ Enabled  │ ✗ Disabled │ ✗ Public     │ High         │
└──────────────────┴────────────┴────────────┴──────────────┴──────────────┘
```

## Commands

| Command | Description |
|---------|-------------|
| `check iam` | Analyze IAM configuration |
| `check storage` | Analyze Cloud Storage |
| `check compute` | Analyze Compute Engine |
| `check sql` | Analyze Cloud SQL |
| `check network` | Analyze VPC/Network |
| `help` | Show help message |
| `clear` or `cls` | Clear screen |
| `exit` | Exit the agent |

## Security Best Practices

The agent provides recommendations aligned with:

- **Google Cloud Security Best Practices**
- **CIS Google Cloud Platform Foundation Benchmark**
- **NIST Cybersecurity Framework**
- **ISO 27001 standards**

## Troubleshooting

### Authentication Issues

**Error**: `DefaultCredentialsError: Could not automatically determine credentials`

**Solution**:
```bash
gcloud auth application-default login
```

### Permission Denied

**Error**: `PermissionDenied: 403 When calling the Resource Manager API: Permission denied`

**Solution**: Ensure your service account has the required roles (see Required GCP Permissions section)

### Project ID Not Found

**Error**: `GCP project ID not found`

**Solution**:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
```

### API Not Enabled

**Error**: `ServiceNotEnabledError`

**Solution**: Enable the required APIs:
```bash
gcloud services enable iam.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

## Limitations

1. Some advanced GCP features may require manual configuration
2. Real-time monitoring requires additional setup
3. Historical trend analysis requires data collection over time
4. Some analyses are template-based and may need customization

## Future Enhancements

- [ ] BigQuery security analysis
- [ ] Cloud Run security review
- [ ] GKE cluster security analysis
- [ ] Cloud Functions security scan
- [ ] Real-time monitoring and alerts
- [ ] Custom security policy templates
- [ ] Integration with Cloud Security Command Center

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review GCP documentation
3. Check service account permissions
4. Enable necessary GCP APIs

## Related Documentation

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [IAM Best Practices](https://cloud.google.com/iam/docs/best-practices)
- [Cloud Storage Security](https://cloud.google.com/storage/docs/security)
- [Compute Engine Security](https://cloud.google.com/compute/docs/security)

---

**Last Updated**: December 3, 2025
**Version**: 1.0
**Status**: Stable
