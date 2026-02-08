#!/usr/bin/env python3
"""Test Azure Agent Setup"""

import os
import sys
from pathlib import Path

# Load environment variables from .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

print("=" * 70)
print("AZURE SECURITY AGENT - SETUP VERIFICATION")
print("=" * 70)

# 1. Check credentials
print("\n1️⃣  CREDENTIALS LOADED FROM .env")
print("-" * 70)
creds = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "AZURE_SUBSCRIPTION_ID": os.getenv("AZURE_SUBSCRIPTION_ID"),
    "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
}

for key, value in creds.items():
    if value and not value.startswith("your-"):
        masked = value[:15] + "..." if len(str(value)) > 15 else value
        print(f"✅ {key:<30} = {masked}")
    elif value:
        print(f"⚠️  {key:<30} = {value} (PLACEHOLDER)")
    else:
        print(f"❌ {key:<30} = NOT SET")

# 2. Agent initialization
print("\n2️⃣  AGENT INITIALIZATION TEST")
print("-" * 70)
try:
    from src.agents.azure_security.agent import AzureSecurityAgent
    agent = AzureSecurityAgent()
    print(f"✅ Agent initialized")
    print(f"   • Subscription: {agent.subscription_id or '(none)'}")
    print(f"   • Tenant: {agent.tenant_id or '(none)'}")
    print(f"   • LLM Status: {'✅ Enabled' if agent.llm else '⚠️  Disabled (Gemini key missing)'}")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    sys.exit(1)

# 3. Available capabilities
print("\n3️⃣  SECURITY ANALYSIS CAPABILITIES")
print("-" * 70)

audit_methods = [m for m in dir(agent) if m.startswith('_audit_')]
analysis_methods = [m for m in dir(agent) if m.startswith('analyze_')]

print(f"✅ Audit Methods ({len(audit_methods)}):")
for method in sorted(audit_methods):
    nice_name = method.replace('_audit_', '').replace('_', ' ').title()
    print(f"   • {nice_name}")

print(f"\n✅ Analysis Methods ({len(analysis_methods)}):")
for method in sorted(analysis_methods):
    nice_name = method.replace('analyze_', '').replace('_', ' ').title()
    print(f"   • {nice_name}")

print(f"\n✅ Main Methods:")
print(f"   • process_command() - Handle natural language queries")
print(f"   • perform_full_audit() - Generate complete security audit")

# 4. Demo test
print("\n4️⃣  DEMONSTRATION TEST")
print("-" * 70)
try:
    print("Testing: agent.process_command('Check Entra ID security')")
    result = agent.process_command("Check Entra ID security")
    print("✅ Command processed successfully")
    if result:
        lines = result.split('\n')[:3]
        print(f"   Sample output: {lines[0][:60]}...")
except Exception as e:
    print(f"⚠️  Command processing: {e}")

print("\n" + "=" * 70)
print("SETUP STATUS SUMMARY")
print("=" * 70)

issues = []
if not os.getenv("GOOGLE_API_KEY"):
    issues.append("❌ Gemini API key not set")
elif os.getenv("GOOGLE_API_KEY", "").startswith("your-"):
    issues.append("⚠️  Gemini API key is a placeholder")
else:
    print("✅ Gemini API key configured")

if not os.getenv("AZURE_SUBSCRIPTION_ID"):
    issues.append("❌ Azure subscription ID not set")
elif os.getenv("AZURE_SUBSCRIPTION_ID", "").startswith("your-"):
    issues.append("⚠️  Azure subscription ID is a placeholder")
else:
    print("✅ Azure subscription ID configured")

if not os.getenv("AZURE_TENANT_ID"):
    issues.append("❌ Azure tenant ID not set")
elif os.getenv("AZURE_TENANT_ID", "").startswith("your-"):
    issues.append("⚠️  Azure tenant ID is a placeholder")
else:
    print("✅ Azure tenant ID configured")

if not issues:
    print("\n✅ ALL SYSTEMS READY - Ready to connect to Azure!")
else:
    print("\n⚠️  Issues found:")
    for issue in issues:
        print(f"   {issue}")
    print("\n📝 NEXT STEPS:")
    print("   1. Update .env file with your actual credentials:")
    print("      • GOOGLE_API_KEY: Get from https://aistudio.google.com/app/apikeys")
    print("      • AZURE_SUBSCRIPTION_ID: Get from 'az account show' or Azure portal")
    print("      • AZURE_TENANT_ID: Get from 'az account show' or Azure portal")
    print("   2. Run 'az login' to authenticate with Azure")
    print("   3. Run this test again to verify")

