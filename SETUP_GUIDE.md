# Complete Setup Guide for All Cloud Security Agents

This guide covers setup requirements for **AWS**, **GCP**, and **Azure** security agents.

---

## Prerequisites (All Agents)

### 1. Python Environment

```bash
# Create virtual environment
python -m venv cloudagent
source cloudagent/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Gemini API Key (Required for all agents)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Create an API key
3. Save it to `.env` file:

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
EOF
```

Or export as environment variable:
```bash
export GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## AWS Security Agent Setup

### What It Does
- Analyzes EC2, S3, VPC, and IAM security configurations
- Performs comprehensive security audits
- Generates PDF reports with findings and recommendations
- Supports natural language queries about AWS infrastructure

### Prerequisites

1. **AWS Account** with resources to audit
2. **AWS CLI** installed and configured:

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

3. **AWS IAM Permissions** - Create an IAM user or role with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:List*",
        "s3:GetBucketPolicy",
        "s3:GetBucketVersioning",
        "iam:ListUsers",
        "iam:ListRoles",
        "iam:GetRole",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

### How to Use

#### Option 1: Interactive CLI (Recommended)
```bash
python main_cli.py

# Then type:
general> switch to aws-security
aws-security> Check my EC2 security groups
aws-security> Perform a full audit
```

#### Option 2: Direct AWS Agent
```bash
python aws_security_agent.py
```

#### Option 3: Standalone Script
```bash
python -c "
from aws_security_agent import AWSSecurityAgent
agent = AWSSecurityAgent()
result = agent.perform_full_audit(export_pdf=True)
print(f'Report: {result[\"pdf_path\"]}')"
```

### Example Commands in AWS Agent

```
Check my EC2 instances
Review S3 bucket security
Analyze VPC configuration
List IAM users and roles
Find unrestricted security groups
Perform a full audit
```

### Verification

```bash
# Test AWS CLI connection
aws sts get-caller-identity

# Should output your AWS account info:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

### Troubleshooting

**Error: "aws: command not found"**
- AWS CLI not installed or not in PATH
- Reinstall and add to PATH

**Error: "Unable to locate credentials"**
- Run `aws configure` and enter your credentials
- Or set environment variables: `export AWS_ACCESS_KEY_ID=...` and `export AWS_SECRET_ACCESS_KEY=...`

**Error: "An error occurred (AccessDenied)"**
- IAM user doesn't have required permissions
- Add EC2, S3, and IAM read permissions

---

## GCP Security Agent Setup

### What It Does
- Analyzes GCE, GCS, VPC, Cloud SQL, and IAM security
- Performs comprehensive GCP infrastructure audits
- Generates professional PDF reports
- Supports natural language queries about GCP resources

### Prerequisites

1. **Google Cloud Project** with resources
2. **GCP CLI** installed:

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init
```

3. **Service Account** with proper permissions:

```bash
# Set your project
export GCP_PROJECT=your-project-id

# Create service account
gcloud iam service-accounts create gcp-security-agent \
  --display-name="GCP Security Agent" \
  --project=$GCP_PROJECT

# Create and download key
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=gcp-security-agent@$GCP_PROJECT.iam.gserviceaccount.com

# Grant required roles
gcloud projects add-iam-policy-binding $GCP_PROJECT \
  --member=serviceAccount:gcp-security-agent@$GCP_PROJECT.iam.gserviceaccount.com \
  --role=roles/viewer

gcloud projects add-iam-policy-binding $GCP_PROJECT \
  --member=serviceAccount:gcp-security-agent@$GCP_PROJECT.iam.gserviceaccount.com \
  --role=roles/compute.viewer

gcloud projects add-iam-policy-binding $GCP_PROJECT \
  --member=serviceAccount:gcp-security-agent@$GCP_PROJECT.iam.gserviceaccount.com \
  --role=roles/storage.admin

gcloud projects add-iam-policy-binding $GCP_PROJECT \
  --member=serviceAccount:gcp-security-agent@$GCP_PROJECT.iam.gserviceaccount.com \
  --role=roles/cloudsql.viewer
```

4. **Authenticate**:

```bash
# Using service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json

# Or using gcloud
gcloud auth application-default login
```

5. **Optional**: Add to `.env` file:

```bash
cat >> .env << EOF
GCP_PROJECT=your-project-id
EOF
```

### How to Use

#### Option 1: Interactive CLI (Recommended)
```bash
python main_cli.py

# Then type:
general> switch to gcp-security
gcp-security> Check my GCE instances
gcp-security> Analyze Cloud Storage buckets
gcp-security> Perform a full audit
```

#### Option 2: Direct GCP Agent
```bash
python -c "
from src.agents.gcp_security.agent import GCPSecurityAgent
agent = GCPSecurityAgent(project_id='your-project-id')
agent.cli_main()
"
```

#### Option 3: Standalone Script
```bash
python -c "
from src.agents.gcp_security.agent import GCPSecurityAgent
agent = GCPSecurityAgent(project_id='your-project-id')
result = agent.perform_full_audit(export_pdf=True)
print(f'Report: {result[\"pdf_path\"]}')"
```

### Example Commands in GCP Agent

```
List my GCE instances
Check Cloud Storage buckets
Analyze network security
Review Cloud SQL databases
Check IAM bindings
Perform a full audit
```

### Verification

```bash
# Test GCP authentication
gcloud auth list

# Test project access
gcloud compute instances list --project=your-project-id
```

### Troubleshooting

**Error: "WARNING: Could not find default credentials"**
- Run `gcloud auth application-default login`
- Or set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

**Error: "ERROR: (gcloud.compute.instances.list) User does not have permission"**
- Service account missing required roles
- Run the `gcloud projects add-iam-policy-binding` commands above

**Error: "Project not found"**
- Set correct project ID in `.env` or command-line arguments
- Verify with `gcloud config get-value project`

---

## Azure Security Agent Setup

### What It Does
- Analyzes Entra ID, Storage, Compute, SQL, and Network security
- Performs comprehensive Azure infrastructure audits
- Generates professional PDF reports
- Supports natural language queries about Azure resources

### Prerequisites

1. **Azure Subscription** with resources
2. **Azure CLI** installed:

```bash
# On Linux/macOS
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Or on other systems, download from:
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
```

3. **Azure Authentication**:

```bash
# Interactive login
az login

# This opens a browser to authenticate
# After successful login, your subscription will be displayed

# Set default subscription
az account set --subscription "your-subscription-id"
```

4. **Service Principal** (Optional, for automation):

```bash
# Create service principal
az ad sp create-for-rbac --name "azure-security-agent" \
  --role "Reader" \
  --scopes /subscriptions/your-subscription-id

# This outputs:
# {
#   "appId": "...",
#   "password": "...",
#   "tenant": "..."
# }

# Set environment variables
export AZURE_CLIENT_ID="appId_value"
export AZURE_CLIENT_SECRET="password_value"
export AZURE_TENANT_ID="tenant_value"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

5. **Add to `.env`** (Optional):

```bash
cat >> .env << EOF
AZURE_SUBSCRIPTION_ID=your-subscription-id
EOF
```

### How to Use

#### Option 1: Interactive CLI (Recommended)
```bash
python main_cli.py

# Then type:
general> switch to azure-security
azure-security> Check my Entra ID security
azure-security> Review storage account settings
azure-security> Perform a full audit
```

#### Option 2: Direct Azure Agent
```bash
python azure_security_agent.py
```

#### Option 3: Standalone Script
```bash
python -c "
from src.agents.azure_security.agent import AzureSecurityAgent
agent = AzureSecurityAgent(subscription_id='your-subscription-id')
result = agent.perform_full_audit(export_pdf=True)
print(f'Report: {result[\"pdf_path\"]}')"
```

### Example Commands in Azure Agent

```
Check my Entra ID security
Review storage account settings
Analyze virtual machine configuration
What about SQL database security?
Check network security groups
Perform a full audit
```

### Verification

```bash
# Test Azure authentication
az account show

# Should show your subscription details:
# {
#   "id": "...",
#   "name": "...",
#   "user": {
#     "type": "user",
#     "name": "your-email@example.com"
#   }
# }
```

### Troubleshooting

**Error: "az: command not found"**
- Azure CLI not installed
- Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

**Error: "No subscriptions found"**
- Not logged in - run `az login`
- Or account has no active subscriptions

**Error: "Invalid subscription ID"**
- Subscription ID format incorrect
- Get correct ID: `az account list --query "[].id" -o tsv`

**Error: "AADSTS700016: Application ... not found in directory"**
- Service principal credentials incorrect
- Recreate service principal with correct steps above

---

## Quick Start: Testing All Agents

### 1. Activate Virtual Environment
```bash
source cloudagent/bin/activate
```

### 2. Test Each Agent

```bash
# AWS Agent
echo "Testing AWS Agent..."
python -c "
from aws_security_agent import AWSSecurityAgent
agent = AWSSecurityAgent()
print('✅ AWS Agent loaded successfully')
print(f'Region: {agent.region}')
"

# GCP Agent
echo "Testing GCP Agent..."
python -c "
from src.agents.gcp_security.agent import GCPSecurityAgent
agent = GCPSecurityAgent()
print('✅ GCP Agent loaded successfully')
print(f'Project: {agent.project_id}')
"

# Azure Agent
echo "Testing Azure Agent..."
python -c "
from src.agents.azure_security.agent import AzureSecurityAgent
agent = AzureSecurityAgent()
print('✅ Azure Agent loaded successfully')
print(f'Subscription: {agent.subscription_id}')
"
```

### 3. Try the Main CLI

```bash
python main_cli.py

# Inside the CLI:
# general> switch to aws-security
# aws-security> Check EC2 security groups

# Then try others:
# general> switch to gcp-security
# gcp-security> List Cloud Storage buckets

# general> switch to azure-security
# azure-security> Check Entra ID security
```

---

## Credentials Summary

| Agent | Required | Setup Method |
|-------|----------|--------------|
| **All** | Gemini API Key | Google AI Studio |
| **AWS** | AWS Credentials | `aws configure` |
| **GCP** | Service Account | `gcloud auth` |
| **Azure** | Azure Login | `az login` |

---

## Environment Variables Reference

```bash
# All agents
export GOOGLE_API_KEY=sk-...

# AWS (optional, aws configure is preferred)
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

# GCP
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
export GCP_PROJECT=your-project-id

# Azure
export AZURE_SUBSCRIPTION_ID=...
export AZURE_CLIENT_ID=...
export AZURE_CLIENT_SECRET=...
export AZURE_TENANT_ID=...
```

---

## Next Steps

1. **Set up all three agents** following the steps above
2. **Run the main CLI**: `python main_cli.py`
3. **Generate audit reports**: Use the `Perform a full audit` command in each agent
4. **Check the reports folder**: PDF reports are saved in `reports/` directory
5. **Review findings**: Each report includes:
   - Executive summary
   - Security findings by severity
   - Risk assessment
   - Remediation roadmap

---

## Support & Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'google'"**
```bash
pip install -r requirements.txt
```

**"Connection refused" errors**
- Verify cloud CLI is installed: `aws --version`, `gcloud --version`, `az --version`
- Verify you're logged in to each service

**"Permission denied" errors**
- Check IAM/RBAC roles have necessary read permissions
- Errors are usually clear about what permission is missing

### Getting Help

1. Check specific agent README files:
   - AWS: `aws_security_audit_README.md`
   - GCP: `GCP_SECURITY_AGENT_README.md`
   - Azure: `AZURE_SECURITY_AGENT_README.md`

2. Review implementation summaries:
   - `AZURE_IMPLEMENTATION_SUMMARY.md`
   - `GCP_IMPLEMENTATION_COMPLETE.md`

3. Check project walkthrough:
   - `PROJECT_WALKTHROUGH.md`

---

## Success Indicators

✅ You're ready when:
- [ ] Gemini API key configured and tested
- [ ] AWS CLI installed and `aws sts get-caller-identity` works
- [ ] GCP CLI installed and `gcloud auth list` works
- [ ] Azure CLI installed and `az account show` works
- [ ] `python main_cli.py` starts successfully
- [ ] Can switch between all three agents
- [ ] Each agent responds to queries
- [ ] PDF reports generate successfully

Happy auditing! 🔒
