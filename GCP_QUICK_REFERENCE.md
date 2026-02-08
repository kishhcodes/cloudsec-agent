# GCP Security Agent - Quick Reference

## 🚀 Quick Start

```bash
# 1. Activate environment
source cloudagent/bin/activate

# 2. Set GCP project
export GOOGLE_CLOUD_PROJECT=my-project-id

# 3. Run CLI
python main_cli.py

# 4. Switch to GCP agent
general> switch to gcp-security

# 5. Ask security question
gcp-security> Check my IAM security
```

---

## 📋 Common Commands

### Switching to GCP Agent
```
> switch to gcp-security
> switch to gcp
> use gcp
```

### IAM Security
```
gcp-security> Check my IAM security
gcp-security> Analyze IAM permissions
gcp-security> Review service accounts
```

### Cloud Storage
```
gcp-security> Analyze my Cloud Storage buckets
gcp-security> Check bucket encryption
gcp-security> Are my buckets public?
```

### Compute Engine
```
gcp-security> Review Compute Engine security
gcp-security> List instances with public IPs
gcp-security> Check VM security
```

### Networking
```
gcp-security> Check my VPC configuration
gcp-security> Review firewall rules
gcp-security> Analyze network security
```

### General Commands
```
gcp-security> help          # Show help
gcp-security> clear         # Clear screen
gcp-security> exit          # Quit application
```

---

## 🔧 Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] GCP project ID set
- [ ] GCP credentials configured
- [ ] Google API key set (optional, for LLM)

---

## 📊 Supported Analysis

| Category | Checks |
|----------|--------|
| **IAM** | Service accounts, Roles, Permissions |
| **Storage** | Encryption, Versioning, Public access |
| **Compute** | Public IPs, Service accounts, Security config |
| **Networking** | VPC, Firewalls, Private access |
| **SQL** | SSL/TLS, Private IP, Backups |

---

## ⚙️ Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=my-project-id

# Optional
GOOGLE_API_KEY=your-api-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

---

## 🎯 Example Workflows

### Workflow 1: Quick Security Check
```
> switch to gcp-security
gcp-security> Check my IAM security
gcp-security> Analyze my Cloud Storage buckets
gcp-security> Review Compute Engine security
gcp-security> exit
```

### Workflow 2: Comprehensive Audit
```
> switch to gcp-security
gcp-security> Check IAM
gcp-security> Check storage
gcp-security> Check compute
gcp-security> Check network
gcp-security> switch to compliance-chat
compliance-chat> What are GCP security standards?
```

### Workflow 3: Compliance Verification
```
> switch to gcp-security
gcp-security> Check security configuration
> switch to compliance-chat
compliance-chat> Is my GCP setup CIS compliant?
compliance-chat> What about ISO 27001?
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | Run `pip install -r requirements.txt` |
| Project ID missing | Set `GOOGLE_CLOUD_PROJECT` env var |
| Auth error | Run `gcloud auth application-default login` |
| LLM disabled | Set `GOOGLE_API_KEY` env var |

---

## 📚 Files Structure

```
src/agents/gcp_security/
├── __init__.py          # Module initialization
├── agent.py             # Main GCP agent (600+ lines)
├── cli.py               # CLI interface
└── utils.py             # Utilities and patterns
```

---

## 🔑 Key Capabilities

✅ Natural language queries
✅ Multi-resource analysis  
✅ Real-time security checks
✅ Best practice recommendations
✅ Seamless agent switching
✅ Rich terminal output

---

## 💡 Tips

- Use `help` command to see available commands
- Type `clear` to clean up the screen
- Ask follow-up questions for more details
- Switch between agents for multi-cloud analysis

---

## 📖 More Information

- Full docs: `GCP_IMPLEMENTATION_COMPLETE.md`
- Project walkthrough: `PROJECT_WALKTHROUGH.md`
- Feature roadmap: `FEATURE_RECOMMENDATIONS.md`

---

**Quick Reference v1.0** | December 3, 2025
