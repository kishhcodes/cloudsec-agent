# .gitignore Configuration Guide

## Overview

This project's `.gitignore` file is configured to prevent accidentally committing sensitive information like credentials, API keys, and email configurations.

---

## What's Ignored

### Python Environment
```
__pycache__/
*.py[cod]
.Python
build/
dist/
*.egg-info/
.venv/
env/
cloudagent/
```

**Why:** Prevents virtual environment and build artifacts from being tracked.

---

### IDE and Editor Files
```
.idea/
.vscode/
*.sublime-*
.spyderproject
```

**Why:** Each developer may use different IDEs; these are personal configuration files.

---

### Sensitive Configuration Files
```
.env
.env.*
.env.local
.env.*.local

credentials
.aws/
aws-credentials

.smtp_config
smtp_credentials.json
config/*credentials*.json
config/*secret*.json
config/*smtp*
config/*email*
*api_key*
*apikey*
*credentials*
*secrets*
*smtp*password*
*email*password*
```

**Why:** NEVER commit secrets! These files contain:
- AWS credentials
- Azure subscription keys
- GCP service account keys
- SMTP email passwords
- API keys
- Database credentials

---

### Test and Build Artifacts
```
reports/*
!reports/.gitkeep

test-results/
*.coverage
.pytest_cache/
htmlcov/

.tox/
*.cover
```

**Why:** Generated test reports and coverage reports shouldn't be tracked.

---

### System Files
```
# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/

# Temporary
*.tmp
*.bak
*.swp
*~
```

**Why:** Operating system-specific files that vary by environment.

---

## What's NOT Ignored (Important!)

```
!*.md              # Documentation files (tracked)
!config/           # Config directory allowed (but contents may be ignored)
!reports/.gitkeep  # Marker file to keep reports/ directory in git
!data/*/.gitkeep   # Marker files for data directories
```

**Why:** We WANT to track documentation and directory structure, but not sensitive files within them.

---

## Common Files You Might Need to Add

### If adding new sensitive files:

1. **Database passwords:**
   ```
   *.db.password
   database_credentials.json
   ```

2. **API tokens:**
   ```
   *_token.json
   *_token.txt
   .tokens/
   ```

3. **Private keys:**
   ```
   *.pem
   *.key
   *.pkcs12
   ```

---

## How to Use This Safely

### ✅ DO

```bash
# Set environment variables locally (NOT in .env tracked by git)
export SMTP_SERVER="smtp.gmail.com"
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"

# Create a local .env file (ignored by git)
echo "SMTP_SERVER=smtp.gmail.com" > .env.local
# This file stays on YOUR machine only
```

### ❌ DON'T

```bash
# DON'T do this - it will be visible in git history!
export SENDER_PASSWORD="mysecretpassword"

# DON'T hardcode secrets in Python files
SMTP_PASSWORD = "mypassword"  # NEVER!

# DON'T commit .env files with real credentials
git add .env  # NEVER!
```

---

## Setting Up Your Environment

### Step 1: Create Local .env File

```bash
# Create a .env.local file (only on your machine)
cat > .env.local << 'EOF'
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# AWS Configuration (if using AWS)
AWS_PROFILE=default
AWS_REGION=us-east-1

# Other configuration...
EOF
```

### Step 2: Load Environment Variables

```bash
# Before running the application
source .env.local

# Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
if [ -f ".env.local" ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi
```

### Step 3: Verify Git Won't Track It

```bash
# Check that .env.local is ignored
git check-ignore .env.local
# Should output: .env.local

# Double-check nothing sensitive was committed
git log --oneline -- .env
# Should show no recent commits to .env files
```

---

## Emergency: If You Accidentally Committed Secrets

If you realize you committed a password or API key:

```bash
# Remove the file from git history (but keep it locally)
git rm --cached .env

# Update the commit (only if not pushed yet)
git commit --amend --remove-file .env

# If already pushed, you MUST rotate the credentials immediately!
# Change passwords/keys and notify your team.
```

---

## For Team Collaboration

### Document Required Configuration

Create a `.env.example` file (this IS tracked in git):

```bash
# .env.example - COPY THIS AND FILL IN YOUR VALUES
# git add .env.example (yes, this one is tracked!)

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password-here

# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-east-1

# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-api-key

# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
```

### Share Instructions

```markdown
## Setup Instructions

1. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```

2. Fill in your credentials:
   ```bash
   nano .env.local  # or your editor
   ```

3. Load the environment:
   ```bash
   source .env.local
   ```

4. Verify it's not tracked:
   ```bash
   git status
   # Should NOT show .env.local
   ```
```

---

## Verification Checklist

Before committing, verify:

- [ ] No `.env` files in staging area
- [ ] No credentials in any tracked files
- [ ] No API keys visible in source code
- [ ] No passwords in configuration files
- [ ] `.env.example` is tracked (public template)
- [ ] `.env.local` is NOT tracked (private config)

---

## Tools to Help

### Pre-commit Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent committing files with secrets

if git diff --cached | grep -E "(password|secret|token|api.?key)" -i; then
    echo "ERROR: Attempt to commit file with secrets!"
    exit 1
fi
```

### Git Commands to Check

```bash
# See what would be committed
git diff --cached

# Check for common secret patterns
git diff --cached | grep -i "password\|secret\|token"

# Review files before staging
git diff --stat
```

---

## Summary

✅ **DO:**
- Keep `.gitignore` comprehensive
- Use `.env.local` for secrets (local only)
- Use `.env.example` for templates (tracked in git)
- Rotate credentials if accidentally exposed
- Use environment variables for sensitive data

❌ **DON'T:**
- Commit `.env` files with real credentials
- Hardcode passwords in code
- Share API keys in pull requests
- Use `git add -f` to force-add ignored files with secrets
- Disable `.gitignore` checks

---

## Related Files

- `.env.example` - Template configuration (tracked)
- `.env.local` - Local secrets (NOT tracked, create yourself)
- `EMAIL_CONFIGURATION_GUIDE.md` - SMTP setup guide
- `src/audit/exporters/email_service.py` - Email service implementation

---

**Last Updated:** February 8, 2026  
**Status:** ✅ Complete
