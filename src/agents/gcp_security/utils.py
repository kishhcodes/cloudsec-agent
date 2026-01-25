#!/usr/bin/env python3
"""
Utilities for GCP Security Analysis

Helper functions and utilities for GCP security assessments.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GCPSecurityPatterns:
    """
    Common GCP security anti-patterns and vulnerabilities.
    """
    
    # IAM Patterns
    IAM_RISKY_ROLES = [
        "roles/owner",
        "roles/editor",
        "roles/iam.securityAdmin",
        "roles/iam.serviceAccountAdmin",
    ]
    
    IAM_RISKY_MEMBERS = [
        "allUsers",
        "allAuthenticatedUsers",
    ]
    
    # Storage Patterns
    STORAGE_SECURITY_BEST_PRACTICES = {
        "versioning": "Enable versioning to protect against accidental deletion",
        "encryption": "Enable encryption to protect data at rest",
        "private_access": "Block all public access",
        "logging": "Enable access logging for audit trails",
        "lifecycle": "Define lifecycle policies for cost optimization",
    }
    
    # Compute Patterns
    COMPUTE_SECURITY_BEST_PRACTICES = {
        "public_ip": "Avoid public IPs; use Cloud NAT instead",
        "service_account": "Use custom service accounts with minimal permissions",
        "metadata_server": "Disable metadata server if not needed",
        "serial_ports": "Disable serial port access",
        "preemptible": "Use preemptible instances for cost optimization",
        "disk_encryption": "Use customer-managed encryption keys (CMEK)",
    }
    
    # SQL Patterns
    SQL_SECURITY_BEST_PRACTICES = {
        "ssl": "Require SSL/TLS for all connections",
        "private_ip": "Use Private IP instead of public IP",
        "backup": "Enable automated backups",
        "binlog": "Enable binary logging",
        "auth_proxy": "Use Cloud SQL Auth Proxy",
        "database_flags": "Configure secure database flags",
    }
    
    # Network Patterns
    NETWORK_SECURITY_BEST_PRACTICES = {
        "vpc_sc": "Use VPC Service Controls for sensitive data",
        "flow_logs": "Enable VPC Flow Logs for monitoring",
        "cloud_armor": "Enable Cloud Armor for DDoS protection",
        "firewall_rules": "Implement least privilege firewall rules",
        "nat": "Use Cloud NAT for outbound traffic",
        "private_google_access": "Enable Private Google Access",
        "service_control": "Implement service controls",
    }


class GCPRiskAssessment:
    """
    Risk assessment utilities for GCP resources.
    """
    
    SEVERITY_LEVELS = {
        "critical": 5,
        "high": 4,
        "medium": 3,
        "low": 2,
        "info": 1,
    }
    
    @staticmethod
    def assess_iam_risk(bindings: List[Any]) -> Dict[str, Any]:
        """
        Assess IAM risk based on bindings.
        
        Returns:
            Risk assessment with score and recommendations
        """
        risk_score = 0
        findings = []
        
        for binding in bindings:
            role = binding.role
            members = binding.members
            
            # Check for dangerous role + member combinations
            for member in members:
                if member in GCPSecurityPatterns.IAM_RISKY_MEMBERS:
                    if any(risky_role in role for risky_role in GCPSecurityPatterns.IAM_RISKY_ROLES):
                        risk_score += 3
                        findings.append({
                            "issue": f"Dangerous role {role} assigned to {member}",
                            "severity": "Critical",
                            "recommendation": "Remove public access immediately"
                        })
        
        return {
            "risk_score": risk_score,
            "findings": findings,
            "risk_level": "critical" if risk_score >= 3 else "low"
        }
    
    @staticmethod
    def assess_storage_risk(bucket: Any) -> int:
        """
        Assess risk score for a storage bucket.
        
        Returns:
            Risk score (0-10)
        """
        risk_score = 0
        
        # Check versioning
        if not bucket.versioning_enabled:
            risk_score += 2
        
        # Check encryption
        if not bucket.encryption:
            risk_score += 2
        
        # Check public access (would need actual IAM check)
        # This is simplified - real implementation would check IAM
        
        return risk_score
    
    @staticmethod
    def assess_instance_risk(instance: Any) -> int:
        """
        Assess risk score for a compute instance.
        
        Returns:
            Risk score (0-10)
        """
        risk_score = 0
        
        # Check for public IP
        try:
            for interface in instance.network_interfaces:
                if interface.access_configs:
                    risk_score += 2
                    break
        except Exception:
            pass
        
        # Check service account
        if not instance.service_accounts:
            risk_score += 2
        
        return risk_score


class GCPSecurityRecommendations:
    """
    Security recommendations for GCP resources.
    """
    
    @staticmethod
    def get_iam_recommendations() -> List[str]:
        """Get IAM security recommendations."""
        return [
            "Use service accounts for application authentication",
            "Implement least privilege principle",
            "Regularly audit IAM bindings",
            "Use groups for managing access",
            "Enable audit logging for IAM changes",
            "Use custom roles instead of built-in roles when possible",
            "Regularly remove unused service accounts",
        ]
    
    @staticmethod
    def get_storage_recommendations() -> List[str]:
        """Get Cloud Storage security recommendations."""
        return [
            "Enable versioning on all buckets",
            "Enable encryption for all buckets",
            "Block public access at the bucket level",
            "Enable access logging",
            "Configure lifecycle policies",
            "Use object-level hold for critical data",
            "Enable uniform bucket-level access",
        ]
    
    @staticmethod
    def get_compute_recommendations() -> List[str]:
        """Get Compute Engine security recommendations."""
        return [
            "Use custom service accounts with minimal permissions",
            "Avoid assigning public IPs to instances",
            "Use Cloud NAT for outbound traffic",
            "Implement OS patching and updates",
            "Use Shielded VMs with Secure Boot",
            "Configure firewall rules with least privilege",
            "Monitor instances with Cloud Logging",
        ]
    
    @staticmethod
    def get_sql_recommendations() -> List[str]:
        """Get Cloud SQL security recommendations."""
        return [
            "Require SSL/TLS for all connections",
            "Use Private IP instead of public IP",
            "Enable automated backups",
            "Enable binary logging",
            "Use Cloud SQL Auth Proxy",
            "Configure secure database flags",
            "Regularly rotate database passwords",
        ]
    
    @staticmethod
    def get_network_recommendations() -> List[str]:
        """Get VPC and network security recommendations."""
        return [
            "Enable VPC Flow Logs",
            "Use VPC Service Controls",
            "Enable Cloud Armor for DDoS protection",
            "Implement least privilege firewall rules",
            "Use Cloud NAT for outbound traffic",
            "Enable Private Google Access",
            "Monitor network traffic",
        ]


def format_gcp_finding(finding: Dict[str, Any]) -> str:
    """Format a security finding for display."""
    output = []
    output.append(f"[bold red]Issue:[/bold red] {finding.get('issue', 'Unknown')}")
    
    if 'severity' in finding:
        output.append(f"[bold]Severity:[/bold] {finding['severity']}")
    
    if 'recommendation' in finding:
        output.append(f"[bold]Recommendation:[/bold] {finding['recommendation']}")
    
    return "\n".join(output)


def calculate_overall_risk_score(assessments: Dict[str, int]) -> str:
    """
    Calculate overall risk score from individual assessments.
    
    Args:
        assessments: Dictionary of risk scores for different components
        
    Returns:
        Formatted risk level
    """
    total_score = sum(assessments.values())
    average_score = total_score / len(assessments) if assessments else 0
    
    if average_score >= 7:
        return "[bold red]Critical[/bold red]"
    elif average_score >= 5:
        return "[bold red]High[/bold red]"
    elif average_score >= 3:
        return "[bold yellow]Medium[/bold yellow]"
    else:
        return "[bold green]Low[/bold green]"
