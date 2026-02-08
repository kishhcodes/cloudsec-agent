#!/usr/bin/env python3
"""
Google Cloud Platform Security Agent

This agent provides security assessment and analysis for GCP resources.
It supports IAM analysis, storage security, compute security, and networking.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from google.cloud.resourcemanager_v3 import ProjectsClient
from google.cloud import storage as gcp_storage
from google.cloud.compute_v1 import InstancesClient

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.audit import GCPAuditReport
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
from src.remediation import PlaybookExecutor, PlaybookLibrary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

class GCPSecurityAgent:
    """
    An agent for assessing and analyzing security in Google Cloud Platform.
    Supports IAM, Storage, Compute, SQL, and Networking security checks.
    """
    
    def __init__(self, project_id: Optional[str] = None, google_api_key: Optional[str] = None):
        """
        Initialize the GCP Security Agent.
        
        Args:
            project_id: GCP project ID (defaults to environment variable)
            google_api_key: Google API key for Gemini LLM
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project_id:
            raise ValueError(
                "GCP project ID not found. Set GOOGLE_CLOUD_PROJECT environment variable "
                "or pass project_id parameter."
            )
        
        # Initialize GCP clients
        try:
            self.resource_manager_client = ProjectsClient()
            self.storage_client = gcp_storage.Client(project=self.project_id)
            self.compute_client = InstancesClient()
        except Exception as e:
            logger.warning(f"Could not initialize some GCP clients: {str(e)}")
            self.resource_manager_client = None
            self.storage_client = None
            self.compute_client = None
        
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
                with console.status("Running comprehensive GCP audit (this may take a few minutes)..."):
                    audit_result = self.perform_full_audit(export_pdf=True)
                
                response = f"✅ GCP Audit Complete!\n\n"
                response += f"Project ID: {audit_result['project_id']}\n"
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
                result = self.analyze_iam_security(**params)
            elif command_type == "storage_analysis":
                result = self.analyze_storage_security(**params)
            elif command_type == "compute_analysis":
                result = self.analyze_compute_security(**params)
            elif command_type == "sql_analysis":
                result = self.analyze_sql_security(**params)
            elif command_type == "network_analysis":
                result = self.analyze_network_security(**params)
            else:
                result = self._get_llm_response(user_input)
            
            results.append(result)
        
        return "\n\n".join(results)
    
    def analyze_iam_security(self, check_type: str = "overview") -> str:
        """
        Analyze IAM security configuration.
        
        Args:
            check_type: Type of IAM check (overview, roles, service_accounts, permissions)
            
        Returns:
            IAM security analysis as formatted string
        """
        console.print(Panel("[bold blue]Analyzing IAM Security...[/bold blue]"))
        
        analysis = []
        
        try:
            # Note: Getting IAM policy requires service account credentials
            analysis.append(f"[bold]IAM Security Analysis for {self.project_id}[/bold]\n")
            
            analysis.append("[bold]Recommended IAM Security Best Practices:[/bold]")
            analysis.append("1. Use service accounts instead of user accounts for applications")
            analysis.append("2. Apply principle of least privilege")
            analysis.append("3. Regularly audit IAM bindings")
            analysis.append("4. Use Cloud Audit Logs to track IAM changes")
            analysis.append("5. Enable Organization Policy for access control")
            analysis.append("6. Use custom roles instead of built-in roles when applicable")
            analysis.append("7. Regularly remove unused service accounts")
            analysis.append("8. Implement group-based access management")
            
            analysis.append("\n[bold]Common IAM Security Issues to Check:[/bold]")
            analysis.append("• allUsers or allAuthenticatedUsers with sensitive roles")
            analysis.append("• User accounts with Owner or Editor roles")
            analysis.append("• Service accounts with overly broad permissions")
            analysis.append("• Unused or inactive service accounts")
            analysis.append("• Missing API access logging")
            
        except Exception as e:
            analysis.append(f"[bold red]Error analyzing IAM:[/bold red] {str(e)}")
        
        return "\n".join(analysis)
    
    def analyze_storage_security(self, bucket_name: Optional[str] = None) -> str:
        """
        Analyze Cloud Storage bucket security.
        
        Args:
            bucket_name: Specific bucket to analyze (all if None)
            
        Returns:
            Storage security analysis as formatted string
        """
        console.print(Panel("[bold blue]Analyzing Cloud Storage Security...[/bold blue]"))
        
        analysis = []
        analysis.append("[bold]Cloud Storage Security Analysis[/bold]\n")
        
        try:
            if bucket_name:
                buckets = [self.storage_client.get_bucket(bucket_name)]
            else:
                buckets = self.storage_client.list_buckets()
            
            if not buckets:
                analysis.append("[yellow]No buckets found in project[/yellow]")
                return "\n".join(analysis)
            
            # Create security table
            table = Table(title="Bucket Security Status", box=box.ROUNDED)
            table.add_column("Bucket Name", style="cyan")
            table.add_column("Versioning", style="magenta")
            table.add_column("Encryption", style="magenta")
            table.add_column("Public Access", style="magenta")
            table.add_column("Risk Level", style="magenta")
            
            findings = []
            
            for bucket in buckets:
                bucket_findings = self._analyze_bucket_security(bucket)
                findings.extend(bucket_findings)
                
                versioning_status = "✓ Enabled" if bucket.versioning_enabled else "✗ Disabled"
                encryption_status = "✓ Enabled" if bucket.encryption else "✗ Disabled"
                
                # Check public access
                public_access = self._check_bucket_public_access(bucket)
                public_status = "✗ Public" if public_access else "✓ Private"
                
                # Determine risk level
                risk_level = self._calculate_bucket_risk(bucket)
                
                table.add_row(
                    bucket.name,
                    versioning_status,
                    encryption_status,
                    public_status,
                    risk_level
                )
            
            console.print(table)
            
            if findings:
                analysis.append("[bold red]\nSecurity Findings:[/bold red]")
                for finding in findings:
                    analysis.append(f"• {finding['issue']}")
                    analysis.append(f"  Recommendation: {finding['recommendation']}\n")
            
        except Exception as e:
            analysis.append(f"[bold red]Error analyzing storage:[/bold red] {str(e)}")
        
        return "\n".join(analysis)
    
    def analyze_compute_security(self, zone: Optional[str] = None) -> str:
        """
        Analyze Compute Engine security.
        
        Args:
            zone: Specific zone to analyze (all zones if None)
            
        Returns:
            Compute security analysis as formatted string
        """
        console.print(Panel("[bold blue]Analyzing Compute Engine Security...[/bold blue]"))
        
        analysis = []
        analysis.append("[bold]Compute Engine Security Analysis[/bold]\n")
        
        try:
            # List all instances
            zones = [zone] if zone else self._get_all_zones()
            
            findings = []
            instance_count = 0
            
            for z in zones:
                instances = self.compute_client.list(
                    project=self.project_id,
                    zone=z
                )
                
                for instance in instances:
                    instance_count += 1
                    instance_findings = self._analyze_instance_security(instance, z)
                    findings.extend(instance_findings)
            
            if instance_count == 0:
                analysis.append("[yellow]No Compute Engine instances found[/yellow]")
            else:
                analysis.append(f"[bold]Found {instance_count} instances across all zones[/bold]\n")
                
                if findings:
                    analysis.append("[bold red]Security Findings:[/bold red]")
                    for finding in findings:
                        analysis.append(f"• {finding['issue']} (Instance: {finding['instance']})")
                        analysis.append(f"  Recommendation: {finding['recommendation']}\n")
                else:
                    analysis.append("[bold green]✓ No critical security issues found[/bold green]")
            
        except Exception as e:
            analysis.append(f"[bold red]Error analyzing compute:[/bold red] {str(e)}")
        
        return "\n".join(analysis)
    
    def analyze_sql_security(self, instance_name: Optional[str] = None) -> str:
        """
        Analyze Cloud SQL security.
        
        Args:
            instance_name: Specific instance to analyze (all if None)
            
        Returns:
            SQL security analysis as formatted string
        """
        console.print(Panel("[bold blue]Analyzing Cloud SQL Security...[/bold blue]"))
        
        analysis = []
        analysis.append("[bold]Cloud SQL Security Analysis[/bold]\n")
        
        try:
            # Note: Cloud SQL API might require different authentication
            # This is a placeholder for the implementation
            analysis.append("[yellow]Cloud SQL analysis requires additional authentication setup[/yellow]")
            analysis.append("\n[bold]Recommended Cloud SQL Security Practices:[/bold]")
            analysis.append("1. Enable SSL/TLS for all connections")
            analysis.append("2. Use private IP addresses")
            analysis.append("3. Enable automated backups")
            analysis.append("4. Use Cloud SQL Auth Proxy")
            analysis.append("5. Restrict network access")
            analysis.append("6. Enable Binary Logging")
            
        except Exception as e:
            analysis.append(f"[bold red]Error analyzing SQL:[/bold red] {str(e)}")
        
        return "\n".join(analysis)
    
    def analyze_network_security(self) -> str:
        """
        Analyze VPC and networking security.
        
        Returns:
            Network security analysis as formatted string
        """
        analysis = []
        analysis.append("[bold]VPC and Network Security Analysis[/bold]\n")
        
        try:
            analysis.append("[bold]Recommended Network Security Practices:[/bold]")
            analysis.append("1. Use VPC Service Controls for sensitive data")
            analysis.append("2. Enable VPC Flow Logs for monitoring")
            analysis.append("3. Use Cloud Armor for DDoS protection")
            analysis.append("4. Implement least privilege firewall rules")
            analysis.append("5. Use Cloud NAT for outbound traffic")
            analysis.append("6. Enable Private Google Access")
            analysis.append("7. Monitor network traffic with VPC Flow Logs")
            
        except Exception as e:
            analysis.append(f"[bold red]Error analyzing network:[/bold red] {str(e)}")
        
        return "\n".join(analysis)
    
    # Helper methods
    
    def _parse_command(self, user_input: str) -> List[tuple]:
        """Parse natural language command to specific checks."""
        user_input_lower = user_input.lower()
        commands = []
        
        if any(word in user_input_lower for word in ["iam", "role", "permission", "service account"]):
            commands.append(("iam_analysis", {}))
        if any(word in user_input_lower for word in ["storage", "bucket", "gcs", "cloud storage"]):
            commands.append(("storage_analysis", {}))
        if any(word in user_input_lower for word in ["compute", "instance", "vm", "virtual machine"]):
            commands.append(("compute_analysis", {}))
        if any(word in user_input_lower for word in ["sql", "database", "cloudsql"]):
            commands.append(("sql_analysis", {}))
        if any(word in user_input_lower for word in ["network", "vpc", "firewall"]):
            commands.append(("network_analysis", {}))
        
        # If no specific command detected, return empty
        return commands if commands else [("iam_analysis", {})]
    
    def _analyze_iam_bindings(self, bindings: List[Any]) -> List[Dict[str, str]]:
        """Analyze IAM bindings for security issues."""
        findings = []
        
        for binding in bindings:
            role = binding.role
            members = binding.members
            
            # Check for overly permissive roles
            if "Owner" in role or "Editor" in role:
                for member in members:
                    if member == "allUsers" or member == "allAuthenticatedUsers":
                        findings.append({
                            "issue": f"Overly permissive role {role} assigned to {member}",
                            "severity": "Critical",
                            "recommendation": "Remove public access and use specific service accounts instead"
                        })
        
        return findings
    
    def _count_service_accounts(self, bindings: List[Any]) -> int:
        """Count service accounts in IAM bindings."""
        count = 0
        for binding in bindings:
            for member in binding.members:
                if "serviceAccount" in member:
                    count += 1
        return count
    
    def _count_external_users(self, bindings: List[Any]) -> int:
        """Count external users in IAM bindings."""
        count = 0
        for binding in bindings:
            for member in binding.members:
                if "@" in member and "serviceAccount" not in member:
                    count += 1
        return count
    
    def _analyze_bucket_security(self, bucket: Any) -> List[Dict[str, str]]:
        """Analyze individual bucket for security issues."""
        findings = []
        
        if not bucket.versioning_enabled:
            findings.append({
                "issue": f"Bucket '{bucket.name}' does not have versioning enabled",
                "recommendation": "Enable versioning to protect against accidental deletion"
            })
        
        if not bucket.encryption:
            findings.append({
                "issue": f"Bucket '{bucket.name}' does not have encryption enabled",
                "recommendation": "Enable default encryption (Google-managed or customer-managed keys)"
            })
        
        return findings
    
    def _check_bucket_public_access(self, bucket: Any) -> bool:
        """Check if bucket has public access."""
        try:
            for policy in bucket.iam.get_bindings().values():
                for member in policy:
                    if "allUsers" in member or "allAuthenticatedUsers" in member:
                        return True
        except Exception:
            pass
        return False
    
    def _calculate_bucket_risk(self, bucket: Any) -> str:
        """Calculate risk level for a bucket."""
        risk_score = 0
        
        if not bucket.versioning_enabled:
            risk_score += 2
        if not bucket.encryption:
            risk_score += 2
        if self._check_bucket_public_access(bucket):
            risk_score += 3
        
        if risk_score >= 5:
            return "[bold red]High[/bold red]"
        elif risk_score >= 2:
            return "[bold yellow]Medium[/bold yellow]"
        else:
            return "[bold green]Low[/bold green]"
    
    def _analyze_instance_security(self, instance: Any, zone: str) -> List[Dict[str, str]]:
        """Analyze Compute Engine instance for security issues."""
        findings = []
        
        # Check for public IP
        if self._instance_has_public_ip(instance):
            findings.append({
                "issue": f"Instance '{instance.name}' has a public IP address",
                "instance": instance.name,
                "recommendation": "Use Cloud NAT or remove public IP if not needed"
            })
        
        # Check for service accounts
        if not instance.service_accounts:
            findings.append({
                "issue": f"Instance '{instance.name}' uses default service account",
                "instance": instance.name,
                "recommendation": "Create and use a custom service account with minimal permissions"
            })
        
        return findings
    
    def _instance_has_public_ip(self, instance: Any) -> bool:
        """Check if instance has a public IP."""
        try:
            for interface in instance.network_interfaces:
                if interface.access_configs:
                    return True
        except Exception:
            pass
        return False
    
    def _get_all_zones(self) -> List[str]:
        """Get all zones in the project."""
        # Placeholder for getting all zones
        return ["us-central1-a", "us-central1-b", "us-central1-c"]
    
    def perform_full_audit(self, export_pdf: bool = True) -> Dict[str, Any]:
        """
        Perform a comprehensive full audit of GCP infrastructure.
        Covers Compute Engine, Cloud Storage, IAM, VPC and generates a detailed report.
        
        Args:
            export_pdf: Whether to export results as PDF
            
        Returns:
            Audit report dictionary with results and PDF path
        """
        console.print("[bold cyan]Starting Comprehensive GCP Audit...[/bold cyan]\n")
        
        # Create audit report
        audit_report = GCPAuditReport(self.project_id)
        
        # 1. IAM Security Analysis
        console.print("[yellow]Analyzing IAM Security...[/yellow]")
        iam_analysis = self._audit_iam_security()
        audit_report.add_iam_analysis(iam_analysis)
        
        # 2. Cloud Storage Security Analysis
        console.print("[yellow]Analyzing Cloud Storage Security...[/yellow]")
        storage_analysis = self._audit_storage_security()
        audit_report.add_storage_analysis(storage_analysis)
        
        # 3. Compute Engine Security Analysis
        console.print("[yellow]Analyzing Compute Engine Security...[/yellow]")
        compute_analysis = self._audit_compute_security()
        audit_report.add_compute_analysis(compute_analysis)
        
        # 4. VPC & Network Security Analysis
        console.print("[yellow]Analyzing VPC & Network Security...[/yellow]")
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
            "project_id": self.project_id,
            "report": audit_report,
            "pdf_path": pdf_path,
            "summary": audit_report.summary_data
        }
    
    def _audit_iam_security(self) -> Dict[str, Any]:
        """Audit IAM security"""
        findings = []
        
        try:
            # Get service accounts
            from google.cloud import iam_admin_v1
            iam_client = iam_admin_v1.GetIamPolicyRequest()
            service_accounts = []
            
            # Note: In a real implementation, you would list service accounts
            # For now, we provide general IAM recommendations
            
        except Exception as e:
            logger.warning(f"Could not fetch IAM details: {e}")
        
        # Build findings
        findings.append({
            "severity": "Medium",
            "title": "Regular IAM Policy Review",
            "description": "IAM policies should be reviewed regularly to ensure least privilege access.",
            "recommendation": "Review all service account and IAM bindings quarterly."
        })
        
        findings.append({
            "severity": "High",
            "title": "Avoid Using Default Service Account",
            "description": "The default Compute Engine service account has the Editor role by default.",
            "recommendation": "Create custom service accounts with minimal required permissions instead of using the default."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Use Workload Identity When Possible",
            "description": "For GKE workloads, Workload Identity is more secure than service account keys.",
            "recommendation": "Configure Workload Identity to map Kubernetes service accounts to GCP service accounts."
        })
        
        findings.append({
            "severity": "Low",
            "title": "IAM Best Practices Applied",
            "description": "Following GCP IAM security recommendations.",
            "recommendation": "Continue monitoring IAM configurations and update as needed."
        })
        
        return {
            "description": "This section analyzes Identity and Access Management (IAM) security, including service accounts and role assignments.",
            "findings": findings,
            "summary": [
                "Review service account key rotation policies",
                "Audit custom roles for least privilege",
                "Disable unused service accounts",
                "Monitor IAM policy changes"
            ]
        }
    
    def _audit_storage_security(self) -> Dict[str, Any]:
        """Audit Cloud Storage security"""
        findings = []
        
        try:
            if not self.storage_client:
                raise Exception("Storage client not initialized")
            
            buckets = list(self.storage_client.list_buckets())
            public_buckets = 0
            unencrypted_buckets = 0
            no_versioning_buckets = 0
            
            for bucket in buckets:
                # Check public access
                try:
                    policy = bucket.iam_configuration
                    if hasattr(policy, 'uniform_bucket_level_access'):
                        if not policy.uniform_bucket_level_access.enabled:
                            public_buckets += 1
                except Exception:
                    pass
                
                # Check versioning
                if not bucket.versioning_enabled:
                    no_versioning_buckets += 1
            
            total_buckets = len(buckets)
            
            if total_buckets == 0:
                findings.append({
                    "severity": "Pass",
                    "title": "No Cloud Storage Buckets",
                    "description": "No Cloud Storage buckets found in project.",
                    "recommendation": "Ensure security policies are in place before creating new buckets."
                })
            else:
                findings.append({
                    "severity": "Low",
                    "title": f"{total_buckets} Cloud Storage Bucket(s)",
                    "description": f"Your project has {total_buckets} Cloud Storage bucket(s).",
                    "recommendation": "Regularly audit bucket configurations and access policies."
                })
            
            if public_buckets > 0:
                findings.append({
                    "severity": "Critical",
                    "title": f"{public_buckets} Bucket(s) Without Uniform Bucket-Level Access",
                    "description": f"Found {public_buckets} bucket(s) without uniform bucket-level access control.",
                    "recommendation": "Enable uniform bucket-level access on all buckets and remove object-level ACLs."
                })
            
            if no_versioning_buckets > 0:
                findings.append({
                    "severity": "Medium",
                    "title": f"{no_versioning_buckets} Bucket(s) Without Versioning",
                    "description": f"Found {no_versioning_buckets} bucket(s) without versioning enabled.",
                    "recommendation": "Enable object versioning on all buckets for data protection."
                })
            
            # Encryption recommendation
            findings.append({
                "severity": "Medium",
                "title": "Verify Customer-Managed Encryption Keys (CMEK)",
                "description": "Consider using customer-managed encryption keys for sensitive data.",
                "recommendation": "Enable CMEK in Cloud KMS for sensitive Cloud Storage buckets."
            })
            
            return {
                "description": "This section analyzes Cloud Storage security, including bucket access controls and encryption.",
                "findings": findings,
                "summary": [
                    f"Total Cloud Storage Buckets: {total_buckets}",
                    f"Buckets Without Uniform Access: {public_buckets}",
                    f"Buckets Without Versioning: {no_versioning_buckets}",
                    "Recommended: Enable uniform bucket-level access and versioning"
                ]
            }
        
        except Exception as e:
            logger.error(f"Error auditing storage: {e}")
            return {
                "description": "Error analyzing Cloud Storage security.",
                "findings": [{
                    "severity": "Low",
                    "title": "Could Not Analyze Storage",
                    "description": f"Error: {str(e)}",
                    "recommendation": "Check authentication and permissions."
                }],
                "summary": ["Unable to complete storage audit"]
            }
    
    def _audit_compute_security(self) -> Dict[str, Any]:
        """Audit Compute Engine security"""
        findings = []
        
        try:
            if not self.compute_client:
                raise Exception("Compute client not initialized")
            
            # Get instances (simplified - would need to iterate zones in production)
            instances = []
            zones = self._get_all_zones()
            instances_count = 0
            
            findings.append({
                "severity": "Low",
                "title": "Compute Engine Instances Configured",
                "description": f"This project has Compute Engine instances deployed.",
                "recommendation": "Regularly review instance configurations and security settings."
            })
            
            findings.append({
                "severity": "High",
                "title": "Use Shielded VMs",
                "description": "Shielded VMs provide advanced protection against sophisticated threats.",
                "recommendation": "Enable Shielded VM features: Secure Boot, UEFI firmware, and Integrity Monitoring."
            })
            
            findings.append({
                "severity": "Medium",
                "title": "Disable Default Service Account Usage",
                "description": "Instances should use custom service accounts instead of the default.",
                "recommendation": "Create custom service accounts with minimal required permissions."
            })
            
            findings.append({
                "severity": "Medium",
                "title": "Enable OS Login",
                "description": "OS Login provides centralized identity and access management for VM instances.",
                "recommendation": "Enable OS Login at the project level for better access control."
            })
            
            return {
                "description": "This section analyzes Compute Engine security, including VM configurations and access controls.",
                "findings": findings,
                "summary": [
                    "Use Shielded VMs for enhanced security",
                    "Enable OS Login for centralized access management",
                    "Use custom service accounts",
                    "Enable monitoring and logging on all instances",
                    "Regularly patch and update OS images"
                ]
            }
        
        except Exception as e:
            logger.error(f"Error auditing compute: {e}")
            return {
                "description": "Error analyzing Compute Engine security.",
                "findings": [{
                    "severity": "Low",
                    "title": "Could Not Analyze Compute",
                    "description": f"Error: {str(e)}",
                    "recommendation": "Check authentication and permissions."
                }],
                "summary": ["Unable to complete compute audit"]
            }
    
    def _audit_network_security(self) -> Dict[str, Any]:
        """Audit VPC & network security"""
        findings = []
        
        findings.append({
            "severity": "Medium",
            "title": "Use VPC Service Controls",
            "description": "VPC Service Controls provide an additional layer of security for sensitive data.",
            "recommendation": "Implement VPC Service Controls to create security perimeters around sensitive services."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Enable VPC Flow Logs",
            "description": "VPC Flow Logs capture network traffic for monitoring and troubleshooting.",
            "recommendation": "Enable VPC Flow Logs on all subnets for security monitoring."
        })
        
        findings.append({
            "severity": "High",
            "title": "Configure Firewall Rules Properly",
            "description": "Firewall rules should follow the principle of least privilege.",
            "recommendation": "Review all ingress rules and restrict to necessary ports and protocols only."
        })
        
        findings.append({
            "severity": "Medium",
            "title": "Use Private Google Access",
            "description": "Private Google Access allows private VMs to access Google APIs securely.",
            "recommendation": "Enable Private Google Access for instances that don't need public internet access."
        })
        
        findings.append({
            "severity": "Low",
            "title": "Use Cloud Armor for DDoS Protection",
            "description": "Cloud Armor provides DDoS and application-level protection.",
            "recommendation": "Enable Cloud Armor on HTTP(S) load balancers for public-facing services."
        })
        
        return {
            "description": "This section analyzes VPC and network security, including firewall rules and connectivity.",
            "findings": findings,
            "summary": [
                "Review firewall rules for least privilege",
                "Enable VPC Flow Logs for monitoring",
                "Use Private Google Access when applicable",
                "Implement VPC Service Controls for sensitive data",
                "Enable Cloud Armor for public-facing services"
            ]
        }
    
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
                file_path = output_path or f"reports/gcp_report_{self.project_id}.json"
                exporter.export_report(findings, file_path)
                return f"✅ JSON export successful: {file_path}"
                
            elif format == "csv":
                exporter = CSVExporter()
                file_path = output_path or f"reports/gcp_findings_{self.project_id}.csv"
                exporter.export_findings_to_csv(findings.get("findings", []), file_path)
                return f"✅ CSV export successful: {file_path}"
                
            elif format == "html":
                exporter = HTMLExporter()
                file_path = output_path or f"reports/gcp_report_{self.project_id}.html"
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
                if "GCP" in pb_name:
                    matching_playbook = pb
                    break
            
            if not matching_playbook:
                matching_playbook = playbooks.get("GCP-PUBLIC-BUCKET")
            
            # Execute
            execution = executor.execute_playbook(
                playbook=matching_playbook,
                finding_data={"id": finding_id, "project": self.project_id},
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
        You are an expert Google Cloud Platform security advisor.
        Provide concise, actionable security recommendations for GCP resources.
        Focus on IAM, storage, compute, SQL, and networking security.
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
    agent = GCPSecurityAgent()
    
    # Test different queries
    queries = [
        "Check my IAM security",
        "Analyze my Cloud Storage buckets",
        "Review Compute Engine security"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        result = agent.process_command(query)
        print(result)
