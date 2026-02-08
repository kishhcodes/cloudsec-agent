#!/usr/bin/env python3
"""
Azure Security Patterns and Utilities

Provides security patterns, risk assessment, and recommendations for Azure.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class AzureSecurityPattern:
    """Represents an Azure security pattern or best practice"""
    name: str
    severity: str
    description: str
    remediation: str
    affected_services: List[str]


class AzureSecurityPatterns:
    """
    Defines common Azure security patterns and risky configurations.
    """
    
    # Risky roles and permissions
    RISKY_ROLES = {
        "Owner": "Full access to all resources - use sparingly",
        "Contributor": "Can create and modify all resources",
        "User Access Administrator": "Can manage user access - high risk",
        "Virtual Machine Administrator Login": "Admin access to VMs",
        "Storage Account Key Operator Service Role": "Can manage storage keys",
    }
    
    # Risky permissions
    RISKY_PERMISSIONS = [
        "Microsoft.Authorization/*/Write",
        "Microsoft.Network/*/Write",
        "Microsoft.Compute/*/Write",
        "Microsoft.Storage/*/Write",
        "Microsoft.Sql/*/Write",
    ]
    
    # Azure services with security focus
    SECURITY_SERVICES = {
        "azure_security_center": "Azure Defender (formerly Security Center)",
        "azure_defender": "Advanced threat protection",
        "azure_policy": "Enforce organizational standards",
        "azure_blueprints": "Repeatable security baselines",
        "azure_management_groups": "Governance at scale",
        "azure_resource_graph": "Query resource compliance",
        "key_vault": "Secrets and key management",
        "application_gateway": "Web application firewall",
        "azure_firewall": "Network-level protection",
        "ddos_protection": "DDoS attack mitigation",
    }
    
    # Best practices
    BEST_PRACTICES = [
        {
            "category": "Identity & Access",
            "items": [
                "Enforce MFA for all users",
                "Use Privileged Identity Management (PIM)",
                "Implement Conditional Access policies",
                "Regularly review role assignments",
                "Use managed identities instead of credentials",
                "Enable sign-in risk detection",
            ]
        },
        {
            "category": "Data Protection",
            "items": [
                "Enable encryption at rest (TDE, SSE)",
                "Use customer-managed encryption keys (CMK)",
                "Implement data loss prevention (DLP)",
                "Enable versioning and soft delete",
                "Use Azure Key Vault for secrets",
                "Classify and label sensitive data",
            ]
        },
        {
            "category": "Network Security",
            "items": [
                "Implement network segmentation",
                "Use Network Security Groups (NSGs)",
                "Deploy Azure Firewall",
                "Enable DDoS Protection",
                "Use private endpoints and Private Link",
                "Configure service endpoints",
            ]
        },
        {
            "category": "Compute Security",
            "items": [
                "Enable disk encryption",
                "Implement Just-in-Time VM access",
                "Use managed identities",
                "Apply OS patching",
                "Enable antimalware/antivirus",
                "Enable Azure Monitor agent",
            ]
        },
        {
            "category": "Database Security",
            "items": [
                "Enable Transparent Data Encryption (TDE)",
                "Configure firewall rules",
                "Use private endpoints",
                "Enable Azure Defender for SQL",
                "Implement SQL auditing",
                "Use Entra ID authentication",
            ]
        },
        {
            "category": "Monitoring & Compliance",
            "items": [
                "Enable Azure Monitor",
                "Configure diagnostic settings",
                "Enable activity logging",
                "Use Log Analytics workspace",
                "Implement alerts and automation",
                "Regular compliance assessments",
            ]
        }
    ]
    
    @classmethod
    def get_risky_role_description(cls, role: str) -> str:
        """Get description of a risky role"""
        return cls.RISKY_ROLES.get(role, "Unknown role")
    
    @classmethod
    def is_risky_permission(cls, permission: str) -> bool:
        """Check if a permission is risky"""
        for risky_perm in cls.RISKY_PERMISSIONS:
            if risky_perm.replace("*", "").lower() in permission.lower():
                return True
        return False


class AzureRiskAssessment:
    """Assess risk levels for Azure configurations"""
    
    RISK_SCORES = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25,
        "pass": 0,
    }
    
    @staticmethod
    def calculate_risk_score(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall risk score from findings.
        
        Args:
            findings: List of security findings
            
        Returns:
            Risk assessment with scores and recommendations
        """
        if not findings:
            return {
                "overall_score": 0,
                "risk_level": "Low",
                "status": "pass"
            }
        
        total_score = 0
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "pass": 0
        }
        
        for finding in findings:
            severity = finding.get("severity", "low").lower()
            score = AzureRiskAssessment.RISK_SCORES.get(severity, 0)
            total_score += score
            
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calculate average risk
        num_findings = len(findings)
        average_risk = total_score / num_findings if num_findings > 0 else 0
        
        # Determine risk level
        if average_risk >= 75:
            risk_level = "Critical"
        elif average_risk >= 50:
            risk_level = "High"
        elif average_risk >= 25:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "overall_score": int(average_risk),
            "risk_level": risk_level,
            "total_findings": num_findings,
            "severity_breakdown": severity_counts,
            "remediation_priority": AzureRiskAssessment._get_remediation_priority(severity_counts)
        }
    
    @staticmethod
    def _get_remediation_priority(severity_counts: Dict[str, int]) -> List[str]:
        """Get remediation priority based on severity"""
        priority = []
        
        if severity_counts.get("critical", 0) > 0:
            priority.append(f"Address {severity_counts['critical']} CRITICAL findings immediately")
        
        if severity_counts.get("high", 0) > 0:
            priority.append(f"Remediate {severity_counts['high']} HIGH-risk findings within 7 days")
        
        if severity_counts.get("medium", 0) > 0:
            priority.append(f"Plan remediation for {severity_counts['medium']} MEDIUM-risk findings")
        
        if severity_counts.get("low", 0) > 0:
            priority.append(f"Address {severity_counts['low']} LOW-risk findings in backlog")
        
        return priority if priority else ["No findings - maintain current security posture"]


class AzureSecurityRecommendations:
    """Pre-built security recommendations for Azure"""
    
    REMEDIATION_STEPS = {
        "enable_mfa": [
            "Navigate to Azure AD > Security > MFA",
            "Enable Multi-Factor Authentication for all users",
            "Configure Conditional Access policies",
            "Test MFA with a test account",
        ],
        "enable_encryption": [
            "Go to Storage Account > Security + networking > Encryption",
            "Enable 'Double encryption'",
            "For SQL: Enable Transparent Data Encryption (TDE)",
            "Configure customer-managed keys in Key Vault",
        ],
        "restrict_access": [
            "Review Network Security Groups (NSGs)",
            "Remove overly permissive rules",
            "Implement principle of least privilege",
            "Use private endpoints instead of public access",
        ],
        "enable_monitoring": [
            "Enable Azure Monitor for all resources",
            "Configure diagnostic settings",
            "Set up alerts for security events",
            "Integrate with SIEM if available",
        ],
    }
    
    @staticmethod
    def get_remediation_steps(issue_type: str) -> List[str]:
        """Get detailed remediation steps for an issue"""
        return AzureSecurityRecommendations.REMEDIATION_STEPS.get(
            issue_type,
            ["Please consult Azure security documentation for this issue"]
        )


class AzureComplianceFrameworks:
    """Azure compliance and security frameworks"""
    
    FRAMEWORKS = {
        "cis_benchmarks": {
            "name": "CIS Microsoft Azure Foundations Benchmark",
            "description": "Best practices for Azure security configuration",
            "version": "1.4.0"
        },
        "azure_security_benchmark": {
            "name": "Azure Security Benchmark",
            "description": "Microsoft's security recommendations for Azure",
            "controls": [
                "Network Security",
                "Logging and Threat Detection",
                "Identity and Access Control",
                "Data Protection",
                "Asset Management",
                "Incident Response",
                "Backup and Recovery",
            ]
        },
        "pci_dss": {
            "name": "PCI DSS (Payment Card Industry)",
            "description": "Requirements for handling payment card data",
            "azure_services": ["Azure SQL Database", "Azure Key Vault", "Azure Firewall"]
        },
        "hipaa": {
            "name": "HIPAA (Healthcare)",
            "description": "Healthcare data protection requirements",
            "azure_services": ["Azure SQL Database", "Azure Storage", "Azure Key Vault"]
        },
        "gdpr": {
            "name": "GDPR (General Data Protection Regulation)",
            "description": "EU data protection and privacy regulations",
            "azure_services": ["Azure Policy", "Azure DLP", "Data Residency options"]
        },
        "iso_27001": {
            "name": "ISO/IEC 27001",
            "description": "Information Security Management System",
            "azure_services": ["Azure Security Center", "Azure Policy", "Azure Advisor"]
        }
    }
    
    @staticmethod
    def get_framework_recommendations(framework: str) -> Dict[str, Any]:
        """Get specific recommendations for a compliance framework"""
        return AzureComplianceFrameworks.FRAMEWORKS.get(
            framework.lower(),
            {"error": "Framework not found"}
        )
