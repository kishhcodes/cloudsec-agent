# Azure Security Agent

A comprehensive security assessment and analysis agent for Microsoft Azure infrastructure.

## Features

### Security Analysis Capabilities

- **Entra ID (Azure AD) Security**
  - Multi-Factor Authentication (MFA) verification
  - Privileged Access Management (PAM) analysis
  - Identity Protection assessment
  - Application permission review
  - Role assignment auditing

- **Storage Account Security**
  - HTTPS enforcement verification
  - Encryption configuration review
  - Public access control assessment
  - Storage firewall configuration
  - Logging and monitoring enablement
  - Blob versioning and soft delete

- **Virtual Machines & Compute Security**
  - Disk encryption verification
  - Just-in-Time (JIT) VM access
  - Managed identity assessment
  - Network security group (NSG) evaluation
  - OS patching and updates
  - Antimalware protection status
  - Monitoring and logging verification

- **SQL Databases Security**
  - Transparent Data Encryption (TDE) verification
  - Firewall rule assessment
  - Private endpoint configuration
  - Azure Defender for SQL status
  - Auditing configuration
  - Entra ID authentication review
  - Backup and recovery policies

- **Network Security**
  - Network segmentation analysis
  - Azure Firewall deployment
  - DDoS Protection configuration
  - VPN Gateway setup
  - Network Watcher enablement
  - Private Link and Private Endpoints
  - NSG flow logs monitoring

### Full Audit Reports

Generate comprehensive PDF audit reports covering:
- Executive summary with finding counts by severity
- Detailed security analysis for each service area
- Risk assessment and scoring
- Remediation roadmap (Immediate, Short-term, Medium-term, Long-term)
- Color-coded severity levels (Critical, High, Medium, Low, Pass)

### Natural Language Processing

The agent understands natural language queries related to Azure security:

```
"Check my Entra ID security"
"Review storage account settings"
"Analyze virtual machine configuration"
"What about SQL database security?"
"Perform a full audit"
"Check Azure firewall rules"
```

## Installation

### Prerequisites

```bash
# Set environment variables
export GOOGLE_API_KEY=your_gemini_api_key
export AZURE_SUBSCRIPTION_ID=your_subscription_id
```

### Running the Agent

#### Interactive CLI

```bash
python azure_security_agent.py
```

Or with subscription ID:

```bash
python azure_security_agent.py --subscription YOUR_SUBSCRIPTION_ID
```

#### From Main CLI

```bash
python main_cli.py

# Then switch to Azure agent:
general> switch to azure-security
azure-security> Check my Entra ID security
```

## Usage Examples

### Interactive Commands

```bash
azure-security> entra
# Analyzes Entra ID security

azure-security> storage
# Analyzes storage account security

azure-security> compute
# Analyzes virtual machine security

azure-security> database
# Analyzes SQL database security

azure-security> network
# Analyzes network security

azure-security> audit
# Performs full Azure audit and generates PDF report
```

### Natural Language Queries

```bash
azure-security> Check my MFA configuration
azure-security> What are the security issues with my storage accounts?
azure-security> Review VM security settings
azure-security> Is my database encrypted?
azure-security> Perform a full audit
```

## Security Recommendations

### Immediate Actions (0-7 days)

- ✅ Enable MFA for all users
- ✅ Disable public blob access
- ✅ Enable disk encryption
- ✅ Configure firewalls

### Short-term (1-4 weeks)

- 🔄 Implement Privileged Identity Management (PIM)
- 🔄 Enable Identity Protection
- 🔄 Configure private endpoints
- 🔄 Enable comprehensive logging

### Medium-term (1-2 months)

- 📅 Implement Azure Policy
- 📅 Deploy DDoS Protection
- 📅 Enable Azure Defender
- 📅 Review all role assignments

### Long-term (Ongoing)

- 🔁 Continuous monitoring
- 🔁 Regular compliance audits
- 🔁 Security training
- 🔁 Incident response planning

## Architecture

### Azure Services Analyzed

| Service | Analysis Points | Risk Categories |
|---------|---|---|
| Entra ID | MFA, PIM, Conditional Access | Identity & Access |
| Storage | Encryption, HTTPS, Public Access | Data Protection |
| Virtual Machines | Encryption, JIT Access, Patching | Compute Security |
| SQL Database | Encryption, Firewall, Auditing | Data Security |
| Networking | NSG, Firewall, DDoS, Monitoring | Network Security |

### Compliance Frameworks Supported

- **CIS Microsoft Azure Foundations Benchmark**
- **Azure Security Benchmark**
- **PCI DSS** (Payment Card Industry)
- **HIPAA** (Healthcare)
- **GDPR** (General Data Protection)
- **ISO/IEC 27001** (Information Security)

## Output Formats

### Console Output

Real-time analysis with color-coded findings and recommendations.

### PDF Reports

Comprehensive audit reports with:
- Professional formatting
- Color-coded severity indicators
- Executive summary
- Detailed findings
- Remediation roadmap
- Custom headers and footers

Reports are saved to: `reports/{PROVIDER}-AUDIT-{TIMESTAMP}.pdf`

## API Reference

### AzureSecurityAgent Class

```python
from src.agents.azure_security.agent import AzureSecurityAgent

# Initialize
agent = AzureSecurityAgent(subscription_id="your-subscription-id")

# Perform analysis
agent.analyze_entra_id_security()
agent.analyze_storage_security()
agent.analyze_compute_security()
agent.analyze_database_security()
agent.analyze_network_security()

# Full audit
result = agent.perform_full_audit(export_pdf=True)
```

### Utility Classes

```python
from src.agents.azure_security.utils import (
    AzureSecurityPatterns,
    AzureRiskAssessment,
    AzureSecurityRecommendations,
    AzureComplianceFrameworks
)
```

## Troubleshooting

### "Google API key not found"

Set the environment variable:
```bash
export GOOGLE_API_KEY=your_api_key
```

### "Subscription ID not found"

Set the environment variable:
```bash
export AZURE_SUBSCRIPTION_ID=your_subscription_id
```

Or pass it when running:
```bash
python azure_security_agent.py --subscription YOUR_SUBSCRIPTION_ID
```

### LLM features disabled

Ensure GOOGLE_API_KEY is set for full functionality including natural language understanding.

## Advanced Features

### Bulk Auditing

```python
subscriptions = ["sub1", "sub2", "sub3"]

for sub_id in subscriptions:
    agent = AzureSecurityAgent(subscription_id=sub_id)
    result = agent.perform_full_audit(export_pdf=True)
```

### Custom Analysis

```python
# Get findings in dict format
findings = agent._audit_entra_id_security()

# Process findings programmatically
from src.agents.azure_security.utils import AzureRiskAssessment

risk_score = AzureRiskAssessment.calculate_risk_score(
    findings['findings']
)
```

## Contributing

To extend the Azure agent with additional checks:

1. Add analysis method to `agent.py`
2. Implement helper method `_audit_*_security()`
3. Return dict with `findings` and `summary`
4. Update audit report generation

## License

Part of Cloud Security Assistant - See main project LICENSE

## Support

For issues or feature requests, refer to main project repository.
