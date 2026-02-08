#!/usr/bin/env python3
"""
Microsoft Azure Security Agent

This agent provides security assessment and analysis for Azure resources.
Supports IAM (Entra ID), Storage security, Compute security, and networking.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.audit import AzureAuditReport
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
from src.remediation import PlaybookExecutor, PlaybookLibrary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()


class AzureSecurityAgent:
    """
    An agent for assessing and analyzing security in Microsoft Azure.
    Supports Entra ID (formerly Azure AD), Storage, Compute, SQL, and Networking security checks.
    """
    
    def __init__(self, subscription_id: Optional[str] = None, google_api_key: Optional[str] = None):
        """
        Initialize the Azure Security Agent.
        
        Args:
            subscription_id: Azure subscription ID (defaults to environment variable)
            google_api_key: Google API key for Gemini LLM
        """
        self.subscription_id = subscription_id or os.getenv("AZURE_SUBSCRIPTION_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        
        if not self.subscription_id:
            logger.warning(
                "Azure subscription ID not found. Set AZURE_SUBSCRIPTION_ID environment variable "
                "or pass subscription_id parameter."
            )
        
        if not self.tenant_id:
            logger.warning(
                "Azure tenant ID not found. Set AZURE_TENANT_ID environment variable."
            )
        
        # Initialize Azure clients would go here (when Azure SDK is available)
        # For now, we provide security recommendations based on best practices
        self.azure_clients = {}
        
        # Initialize Gemini LLM for security analysis
        self.api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=self.api_key
            )
        else:
            self.llm = None
            logger.warning("Google API key not found. LLM features will be disabled.")
    
    def process_command(self, user_input: str) -> str:
        """
        Process a user command and provide security analysis.
        
        Args:
            user_input: User's natural language query or command
            
        Returns:
            Analysis and recommendations as a formatted string
        """
        # Check for full audit request
        if "full audit" in user_input.lower() or "perform a full audit" in user_input.lower():
            try:
                with console.status("Running comprehensive Azure audit (this may take a few minutes)..."):
                    audit_result = self.perform_full_audit(export_pdf=True)
                
                response = f"✅ Azure Audit Complete!\n\n"
                response += f"Subscription ID: {audit_result['subscription_id']}\n"
                response += f"PDF Report: {audit_result['pdf_path']}\n"
                
                return response
            except Exception as e:
                error = f"❌ Error performing audit: {str(e)}"
                console.print(f"[red]{error}[/red]")
                return error
        
        # Map natural language to specific security checks
        commands = self._parse_command(user_input)
        
        results = []
        for command_type, params in commands:
            if command_type == "iam_analysis":
                result = self.analyze_entra_id_security(**params)
            elif command_type == "storage_analysis":
                result = self.analyze_storage_security(**params)
            elif command_type == "compute_analysis":
                result = self.analyze_compute_security(**params)
            elif command_type == "database_analysis":
                result = self.analyze_database_security(**params)
            elif command_type == "network_analysis":
                result = self.analyze_network_security(**params)
            else:
                result = self._get_llm_response(user_input)
            
            results.append(result)
        
        return "\n\n".join(results)
    
    def _parse_command(self, user_input: str) -> List[tuple]:
        """
        Parse user input and map to security analysis commands.
        
        Args:
            user_input: User's query
            
        Returns:
            List of (command_type, params) tuples
        """
        user_lower = user_input.lower()
        commands = []
        
        # Map keywords to analysis types
        if any(kw in user_lower for kw in ["entra", "azure ad", "identity", "iam", "rbac", "user", "role", "principal"]):
            commands.append(("iam_analysis", {}))
        
        if any(kw in user_lower for kw in ["storage", "blob", "file share", "data", "backup"]):
            commands.append(("storage_analysis", {}))
        
        if any(kw in user_lower for kw in ["vm", "virtual machine", "compute", "instance", "app service"]):
            commands.append(("compute_analysis", {}))
        
        if any(kw in user_lower for kw in ["database", "sql", "cosmos", "postgres", "mysql", "sql server"]):
            commands.append(("database_analysis", {}))
        
        if any(kw in user_lower for kw in ["network", "vnet", "nsg", "firewall", "security group", "routing"]):
            commands.append(("network_analysis", {}))
        
        # If no specific commands matched, return general LLM response
        if not commands:
            commands.append(("llm_response", {}))
        
        return commands
    
    def perform_full_audit(self, export_pdf: bool = True) -> Dict[str, Any]:
        """
        Perform a comprehensive full audit of Azure infrastructure.
        Covers VMs, Storage, Databases, Networking, and Entra ID.
        
        Args:
            export_pdf: Whether to export results as PDF
            
        Returns:
            Audit report dictionary with results and PDF path
        """
        console.print("[bold cyan]Starting Comprehensive Azure Audit...[/bold cyan]\n")
        
        # Create audit report
        audit_report = AzureAuditReport(self.subscription_id)
        
        # 1. Entra ID (Azure AD) Security Analysis
        console.print("[yellow]Analyzing Entra ID Security...[/yellow]")
        entra_analysis = self._audit_entra_id_security()
        audit_report.add_iam_analysis(entra_analysis)
        
        # 2. Storage Account Security Analysis
        console.print("[yellow]Analyzing Storage Account Security...[/yellow]")
        storage_analysis = self._audit_storage_security()
        audit_report.add_storage_analysis(storage_analysis)
        
        # 3. Virtual Machines & Compute Security Analysis
        console.print("[yellow]Analyzing Virtual Machines & Compute Security...[/yellow]")
        compute_analysis = self._audit_compute_security()
        audit_report.add_compute_analysis(compute_analysis)
        
        # 4. SQL Databases & Data Security Analysis
        console.print("[yellow]Analyzing Database Security...[/yellow]")
        database_analysis = self._audit_database_security()
        audit_report.add_database_analysis(database_analysis)
        
        # 5. Network Security (vNets, NSGs, Firewalls)
        console.print("[yellow]Analyzing Network Security...[/yellow]")
        network_analysis = self._audit_network_security()
        audit_report.add_network_analysis(network_analysis)
        
        console.print()
        
        # Display summary
        audit_report.display_summary()
        
        # Generate PDF if requested
        pdf_path = None
        if export_pdf:
            console.print("\n[cyan]Generating PDF report...[/cyan]")
            pdf_path = audit_report.generate_pdf()
        
        return {
            "subscription_id": self.subscription_id,
            "report": audit_report,
            "pdf_path": pdf_path,
            "summary": audit_report.summary_data
        }
    
    def _audit_entra_id_security(self) -> Dict[str, Any]:
        """Audit Entra ID (Azure AD) security"""
        findings = []
        
        findings.append({
            "severity": "High",
            "title": "Enable Multi-Factor Authentication (MFA)",
            "description": "MFA should be required for all users, especially administrators.",
            "recommendation": "Enforce MFA through Conditional Access policies for all users."
        })
        
        findings.append({
            "severity": "High",
            "title": "Review Privileged Access Management (PAM)",
            "description": "Privileged accounts need heightened security controls.",
            "recommendation": "Use Azure AD Privileged Identity Management (PIM) for just-in-time access."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Sign-in Risk Detection",
            "description": "Detect and respond to risky sign-in attempts.",
            "recommendation": "Enable Azure AD Identity Protection to monitor risky sign-ins and user risks."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Review Application Permissions",
            "description": "Third-party applications should have minimal permissions.",
            "recommendation": "Audit and restrict permissions granted to applications in Entra ID."
        })
        
        findings.append({
            "severity": "Low",
            "title": "Monitor Admin Role Assignments",
            "description": "Track who has administrative privileges.",
            "recommendation": "Regularly review Azure AD role assignments and remove unnecessary admins."
        })
        
        return {
            "description": "This section analyzes Entra ID (Azure AD) security, including user management, roles, MFA, and conditional access.",
            "findings": findings,
            "summary": [
                "Enable MFA for all users",
                "Use Privileged Identity Management (PIM)",
                "Enable Identity Protection",
                "Review and restrict application permissions",
                "Monitor administrative role assignments"
            ]
        }
    
    def _audit_storage_security(self) -> Dict[str, Any]:
        """Audit Azure Storage security"""
        findings = []
        
        findings.append({
            "severity": "High",
            "title": "Enforce HTTPS Only",
            "description": "All storage accounts should require HTTPS for data in transit.",
            "recommendation": "Set 'Secure transfer required' to enabled on all storage accounts."
        })
        
        findings.append({
            "severity": "High",
            "title": "Enable Storage Encryption",
            "description": "Data at rest should be encrypted.",
            "recommendation": "Enable Storage Service Encryption (SSE) and use customer-managed keys (CMK) for sensitive data."
        })
        
        findings.append({
            "severity": "High",
            "title": "Restrict Public Access",
            "description": "Storage accounts should not allow anonymous public access by default.",
            "recommendation": "Disable 'Allow Blob public access' and configure proper access controls."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Storage Firewalls",
            "description": "Restrict storage account access to specific networks.",
            "recommendation": "Configure storage account firewalls and virtual network service endpoints."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Storage Logging & Monitoring",
            "description": "Monitor access and changes to storage accounts.",
            "recommendation": "Enable Azure Storage logging and integrate with Azure Monitor/Log Analytics."
        })
        
        findings.append({
            "severity": "Low",
            "title": "Implement Blob Versioning",
            "description": "Protect against accidental deletion or modification.",
            "recommendation": "Enable blob versioning and soft delete policies on all containers."
        })
        
        return {
            "description": "This section analyzes Azure Storage security, including access controls, encryption, and monitoring.",
            "findings": findings,
            "summary": [
                "Enforce HTTPS-only connections",
                "Enable encryption at rest with CMK",
                "Disable public blob access",
                "Configure storage firewalls",
                "Enable comprehensive logging and monitoring",
                "Implement versioning and soft delete"
            ]
        }
    
    def _audit_compute_security(self) -> Dict[str, Any]:
        """Audit Azure Virtual Machines & Compute security"""
        findings = []
        
        findings.append({
            "severity": "High",
            "title": "Enable Disk Encryption",
            "description": "Virtual machine disks should be encrypted at rest.",
            "recommendation": "Enable Azure Disk Encryption or enable encryption at host for all VMs."
        })
        
        findings.append({
            "severity": "High",
            "title": "Enable Just-In-Time (JIT) VM Access",
            "description": "Limit RDP/SSH access to specific times and IP addresses.",
            "recommendation": "Enable Azure Security Center Just-in-Time VM access controls."
        })
        
        findings.append({
            "severity": "High",
            "title": "Use Managed Identities",
            "description": "VMs should use managed identities instead of storing credentials.",
            "recommendation": "Assign managed identities to all VMs and use them for Azure resource access."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Restrict Network Access",
            "description": "Virtual machines should be protected by Network Security Groups (NSGs).",
            "recommendation": "Apply NSGs to all VMs and restrict inbound rules to necessary ports only."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Operating System Updates",
            "description": "Keep OS and applications patched and up-to-date.",
            "recommendation": "Enable automatic OS patching through Azure Update Management."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Antimalware Protection",
            "description": "Protect VMs from malware and threats.",
            "recommendation": "Install and enable Microsoft Antimalware or third-party antivirus on all VMs."
        })
        
        findings.append({
            "severity": "Low",
            "title": "Enable Azure Monitor & Logging",
            "description": "Monitor VM health and security.",
            "recommendation": "Enable Azure Monitor, Azure Diagnostics, and log forwarding to Log Analytics."
        })
        
        return {
            "description": "This section analyzes Azure Virtual Machines security, including encryption, access controls, and patching.",
            "findings": findings,
            "summary": [
                "Enable disk encryption (ADE/encryption at host)",
                "Implement Just-in-Time VM access",
                "Use managed identities for authentication",
                "Apply Network Security Groups",
                "Enable OS patching and updates",
                "Enable antimalware protection",
                "Enable comprehensive monitoring"
            ]
        }
    
    def _audit_database_security(self) -> Dict[str, Any]:
        """Audit Azure Database security"""
        findings = []
        
        findings.append({
            "severity": "High",
            "title": "Enable Database Encryption",
            "description": "Databases should be encrypted at rest.",
            "recommendation": "Enable Transparent Data Encryption (TDE) for SQL databases."
        })
        
        findings.append({
            "severity": "High",
            "title": "Configure Firewall Rules",
            "description": "Database servers should restrict access to specific IPs/networks.",
            "recommendation": "Configure firewall rules and use private endpoints for databases."
        })
        
        findings.append({
            "severity": "High",
            "title": "Enable SQL Advanced Threat Protection",
            "description": "Detect and respond to database threats.",
            "recommendation": "Enable Azure Defender for SQL to detect suspicious activities."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Audit Database Access",
            "description": "Track who accesses databases and what changes are made.",
            "recommendation": "Enable SQL Server Auditing or Azure SQL Auditing."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Use Azure AD Authentication",
            "description": "Use Entra ID for database authentication instead of SQL logins.",
            "recommendation": "Configure Azure AD authentication for SQL databases."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Backup & Restore",
            "description": "Ensure databases can be recovered from failures.",
            "recommendation": "Configure automatic backups with appropriate retention policies."
        })
        
        return {
            "description": "This section analyzes Azure Database security, including encryption, access controls, and threat detection.",
            "findings": findings,
            "summary": [
                "Enable Transparent Data Encryption (TDE)",
                "Configure restrictive firewall rules",
                "Use private endpoints for databases",
                "Enable Azure Defender for SQL",
                "Implement SQL auditing",
                "Use Entra ID authentication",
                "Configure automatic backups"
            ]
        }
    
    def _audit_network_security(self) -> Dict[str, Any]:
        """Audit Azure Network security"""
        findings = []
        
        findings.append({
            "severity": "High",
            "title": "Implement Network Segmentation",
            "description": "Use subnets and NSGs to segment network traffic.",
            "recommendation": "Create separate subnets for different workloads and apply NSGs with least privilege rules."
        })
        
        findings.append({
            "severity": "High",
            "title": "Use Azure Firewall",
            "description": "Central firewall for network filtering and threat protection.",
            "recommendation": "Deploy Azure Firewall for centralized network protection and logging."
        })
        
        findings.append({
            "severity": "High",
            "title": "Enable DDoS Protection",
            "description": "Protect against Distributed Denial of Service attacks.",
            "recommendation": "Enable Azure DDoS Protection Standard on critical resources."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Use VPN Gateway for Remote Access",
            "description": "Secure remote access to Azure resources.",
            "recommendation": "Configure Azure VPN Gateway with Point-to-Site or Site-to-Site VPN."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable Network Watcher",
            "description": "Monitor network traffic and diagnose issues.",
            "recommendation": "Enable Network Watcher and configure NSG flow logs."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Use Private Link/Endpoints",
            "description": "Access Azure services privately without internet exposure.",
            "recommendation": "Use Azure Private Link and Private Endpoints for internal access."
        })
        
        return {
            "description": "This section analyzes Azure Network security, including VNets, NSGs, firewalls, and monitoring.",
            "findings": findings,
            "summary": [
                "Implement network segmentation with subnets and NSGs",
                "Deploy Azure Firewall for centralized control",
                "Enable DDoS Protection Standard",
                "Configure VPN for remote access",
                "Enable Network Watcher and NSG flow logs",
                "Use Private Link for internal connectivity",
                "Regular firewall rule audits"
            ]
        }
    
    def analyze_entra_id_security(self, check_type: str = "overview") -> str:
        """
        Analyze Entra ID (Azure AD) security configuration.
        
        Args:
            check_type: Type of analysis
            
        Returns:
            Analysis as formatted string
        """
        console.print(Panel("[bold blue]Analyzing Entra ID Security...[/bold blue]"))
        
        analysis = self._audit_entra_id_security()
        
        result = f"[bold cyan]Entra ID Security Analysis[/bold cyan]\n\n"
        result += f"{analysis['description']}\n\n"
        
        for finding in analysis['findings']:
            severity = finding.get('severity', 'Unknown')
            title = finding.get('title', 'Untitled')
            result += f"[{severity}] {title}\n"
        
        return result
    
    def analyze_storage_security(self, check_type: str = "overview") -> str:
        """Analyze Azure Storage security"""
        console.print(Panel("[bold blue]Analyzing Azure Storage Security...[/bold blue]"))
        
        analysis = self._audit_storage_security()
        
        result = f"[bold cyan]Azure Storage Security Analysis[/bold cyan]\n\n"
        result += f"{analysis['description']}\n\n"
        
        for finding in analysis['findings']:
            severity = finding.get('severity', 'Unknown')
            title = finding.get('title', 'Untitled')
            result += f"[{severity}] {title}\n"
        
        return result
    
    def analyze_compute_security(self, check_type: str = "overview") -> str:
        """Analyze Azure Compute security"""
        console.print(Panel("[bold blue]Analyzing Azure Compute Security...[/bold blue]"))
        
        analysis = self._audit_compute_security()
        
        result = f"[bold cyan]Azure Compute Security Analysis[/bold cyan]\n\n"
        result += f"{analysis['description']}\n\n"
        
        for finding in analysis['findings']:
            severity = finding.get('severity', 'Unknown')
            title = finding.get('title', 'Untitled')
            result += f"[{severity}] {title}\n"
        
        return result
    
    def analyze_database_security(self, check_type: str = "overview") -> str:
        """Analyze Azure Database security"""
        console.print(Panel("[bold blue]Analyzing Azure Database Security...[/bold blue]"))
        
        analysis = self._audit_database_security()
        
        result = f"[bold cyan]Azure Database Security Analysis[/bold cyan]\n\n"
        result += f"{analysis['description']}\n\n"
        
        for finding in analysis['findings']:
            severity = finding.get('severity', 'Unknown')
            title = finding.get('title', 'Untitled')
            result += f"[{severity}] {title}\n"
        
        return result
    
    def analyze_network_security(self, check_type: str = "overview") -> str:
        """Analyze Azure Network security"""
        console.print(Panel("[bold blue]Analyzing Azure Network Security...[/bold blue]"))
        
        analysis = self._audit_network_security()
        
        result = f"[bold cyan]Azure Network Security Analysis[/bold cyan]\n\n"
        result += f"{analysis['description']}\n\n"
        
        for finding in analysis['findings']:
            severity = finding.get('severity', 'Unknown')
            title = finding.get('title', 'Untitled')
            result += f"[{severity}] {title}\n"
        
        return result
    
    def export_report(self, findings: Dict[str, Any], format: str = "json", output_path: Optional[str] = None) -> str:
        """
        Export security findings in multiple formats.
        
        Args:
            findings: Security findings dictionary
            format: Export format ('json', 'csv', 'html')
            output_path: Output file path (optional)
        
        Returns:
            Export status message
        """
        try:
            if format == "json":
                exporter = JSONExporter()
                file_path = output_path or f"reports/azure_report_{self.subscription_id}.json"
                exporter.export_report(findings, file_path)
                return f"✅ JSON export successful: {file_path}"
                
            elif format == "csv":
                exporter = CSVExporter()
                file_path = output_path or f"reports/azure_findings_{self.subscription_id}.csv"
                exporter.export_findings_to_csv(findings.get("findings", []), file_path)
                return f"✅ CSV export successful: {file_path}"
                
            elif format == "html":
                exporter = HTMLExporter()
                file_path = output_path or f"reports/azure_report_{self.subscription_id}.html"
                exporter.export_email_template(findings, file_path)
                return f"✅ HTML export successful: {file_path}"
                
            else:
                return f"❌ Unknown format: {format}"
        except Exception as e:
            return f"❌ Export error: {str(e)}"
    
    def remediate_finding(self, finding_id: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute remediation playbook for a finding.
        
        Args:
            finding_id: Finding ID to remediate
            dry_run: Test without making changes
        
        Returns:
            Execution status dictionary
        """
        try:
            executor = PlaybookExecutor()
            playbooks = PlaybookLibrary.get_all_playbooks()
            
            # Find matching playbook
            matching_playbook = None
            for pb_name, pb in playbooks.items():
                if "AZURE" in pb_name:
                    matching_playbook = pb
                    break
            
            if not matching_playbook:
                matching_playbook = playbooks.get("AZURE-BLOB-PUBLIC")
            
            # Execute
            execution = executor.execute_playbook(
                playbook=matching_playbook,
                finding_data={"id": finding_id, "subscription": self.subscription_id},
                initiated_by=os.getenv("USER", "system"),
                dry_run=dry_run
            )
            
            return {
                "success": True,
                "execution_id": execution.execution_id,
                "status": execution.status.value,
                "playbook": execution.playbook_name,
                "actions": len(execution.actions)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_llm_response(self, user_input: str) -> str:
        """Get LLM response for general security questions."""
        if not self.llm:
            return "LLM service not available. Please check your Google API key."
        
        system_prompt = """
        You are an expert Microsoft Azure security advisor.
        Provide concise, actionable security recommendations for Azure resources.
        Focus on Entra ID, Storage, Compute, Databases, and Networking security.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error getting response: {str(e)}"


if __name__ == "__main__":
    # Example usage
    agent = AzureSecurityAgent(subscription_id="your-subscription-id")
    
    # Test different queries
    queries = [
        "Check my Entra ID security",
        "Analyze my Storage security",
        "Review Virtual Machine security"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        result = agent.process_command(query)
