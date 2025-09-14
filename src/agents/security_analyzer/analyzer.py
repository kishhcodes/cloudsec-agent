# src/agents/security_analyzer/analyzer.py
import os
import re
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json

class SecurityAnalyzer:
    """
    Security Analyzer agent that detects potential security poisoning in compliance frameworks.
    It analyzes configurations, policies, and other security artifacts for signs of tampering or vulnerability.
    """
    
    def __init__(self):
        """Initialize the security analyzer with detection capabilities."""
        # Define known patterns for potential security vulnerabilities or poisoning
        self.poisoning_patterns = {
            "aws_backdoor": [
                r"aws_iam_policy.*effect.*:.*allow.*action.*:\*.*resource.*:\*",
                r"aws_security_group.*cidr_blocks.*:.*0\.0\.0\.0/0.*port.*:.*22",
            ],
            "excessive_permissions": [
                r"(admin|root|superuser).*privilege",
                r"full.*access",
                r"permission.*:.*\*",
            ],
            "encryption_weaknesses": [
                r"encryption.*:.*false",
                r"ssl.*verify.*:.*false",
                r"insecure.*tls",
                r"weak.*cipher",
            ],
            "credential_exposure": [
                r"password|secret|credential|token|key.*=.*[a-zA-Z0-9/+]{8,}",
                r"aws_access_key_id|aws_secret_access_key",
            ],
        }
        
        # Load known compliance fingerprints if available
        self.compliance_fingerprints = self._load_compliance_fingerprints()
        
    def _load_compliance_fingerprints(self) -> Dict[str, Dict[str, Any]]:
        """
        Load compliance fingerprints from a file.
        These fingerprints represent known-good states of compliance frameworks.
        """
        fingerprints_path = os.path.join(os.path.dirname(__file__), "fingerprints.json")
        if os.path.exists(fingerprints_path):
            try:
                with open(fingerprints_path, 'r') as f:
                    return json.load(f)
            except Exception:
                # Return empty dict if file couldn't be loaded
                return {}
        return {}
        
    def analyze_configuration(self, config_text: str, framework_type: str) -> Dict[str, Any]:
        """
        Analyze a configuration for potential security poisoning.
        
        Args:
            config_text: The configuration text to analyze
            framework_type: The type of compliance framework (e.g., 'cis_aws', 'pci_dss')
            
        Returns:
            Dict with analysis results
        """
        results = {
            "poisoning_detected": False,
            "risk_level": "low",
            "findings": [],
            "suggested_remediations": [],
            "framework_type": framework_type,
        }
        
        # Calculate hash of configuration for comparison with known good states
        config_hash = hashlib.sha256(config_text.encode()).hexdigest()
        
        # Check if this is a known good configuration
        if (framework_type in self.compliance_fingerprints and 
            config_hash in self.compliance_fingerprints[framework_type].get("known_good_hashes", [])):
            return results
            
        # Analyze for known poisoning patterns
        for category, patterns in self.poisoning_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, config_text, re.IGNORECASE)
                for match in matches:
                    # Extract the matched text and some surrounding context
                    start = max(0, match.start() - 50)
                    end = min(len(config_text), match.end() + 50)
                    context = config_text[start:end].strip()
                    
                    # Add finding
                    results["findings"].append({
                        "type": category,
                        "pattern": pattern,
                        "matched_text": match.group(0),
                        "context": context,
                        "position": (match.start(), match.end()),
                    })
                    
                    # Suggest remediation based on the type
                    remediation = self._get_remediation(category, match.group(0))
                    if remediation:
                        results["suggested_remediations"].append(remediation)
        
        # Update the overall results based on findings
        if results["findings"]:
            results["poisoning_detected"] = True
            results["risk_level"] = self._calculate_risk_level(results["findings"])
            
        return results
    
    def analyze_policy_drift(self, current_policy: str, reference_policy: str) -> Dict[str, Any]:
        """
        Analyze drift between a current policy and a reference policy.
        
        Args:
            current_policy: The current policy text
            reference_policy: The reference (known good) policy text
            
        Returns:
            Dict with drift analysis results
        """
        results = {
            "drift_detected": False,
            "risk_level": "low",
            "additions": [],
            "removals": [],
            "modifications": [],
        }
        
        # Simple line-by-line comparison
        current_lines = current_policy.splitlines()
        reference_lines = reference_policy.splitlines()
        
        # Find additions (lines in current but not in reference)
        for i, line in enumerate(current_lines):
            line = line.strip()
            if line and line not in reference_lines:
                results["additions"].append({
                    "line_number": i + 1,
                    "content": line,
                })
        
        # Find removals (lines in reference but not in current)
        for i, line in enumerate(reference_lines):
            line = line.strip()
            if line and line not in current_lines:
                results["removals"].append({
                    "line_number": i + 1,
                    "content": line,
                })
        
        # Update drift detection
        if results["additions"] or results["removals"]:
            results["drift_detected"] = True
            # Calculate risk level based on the drift
            results["risk_level"] = self._calculate_drift_risk(
                results["additions"], results["removals"]
            )
            
        return results
    
    def detect_poisoned_benchmarks(self, benchmark_text: str) -> Dict[str, Any]:
        """
        Analyze compliance benchmarks for signs of poisoning or tampering.
        
        Args:
            benchmark_text: The benchmark text to analyze
            
        Returns:
            Dict with benchmark analysis results
        """
        results = {
            "tampering_detected": False,
            "risk_level": "low", 
            "suspicious_sections": [],
            "recommendations": [],
        }
        
        # Look for patterns that indicate benchmark tampering
        tampering_patterns = [
            (r"disable.*logging", "Disabling logging mechanisms"),
            (r"disable.*monitoring", "Disabling monitoring mechanisms"),
            (r"ignore.*alert", "Ignoring security alerts"),
            (r"(backdoor|bypass).*security", "Security bypass mechanisms"),
            (r"(allow|permit).*all.*traffic", "Overly permissive network rules"),
        ]
        
        for pattern, description in tampering_patterns:
            matches = re.finditer(pattern, benchmark_text, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(benchmark_text), match.end() + 100)
                context = benchmark_text[start:end].strip()
                
                # Find the section header (assume it's a line ending with ":")
                section_lines = benchmark_text[:match.start()].splitlines()
                section_header = "Unknown Section"
                for line in reversed(section_lines):
                    if line.strip().endswith(":") or line.strip().endswith("]"):
                        section_header = line.strip()
                        break
                
                results["suspicious_sections"].append({
                    "description": description,
                    "matched_text": match.group(0),
                    "context": context,
                    "section": section_header,
                })
                
                # Add recommendation
                results["recommendations"].append(
                    f"Review the '{description}' in section '{section_header}' as it may indicate benchmark tampering."
                )
        
        # Update overall results
        if results["suspicious_sections"]:
            results["tampering_detected"] = True
            results["risk_level"] = self._calculate_benchmark_risk(results["suspicious_sections"])
            
        return results
    
    def _calculate_risk_level(self, findings: List[Dict[str, Any]]) -> str:
        """Calculate the risk level based on findings."""
        # Simple risk calculation based on finding types and count
        risk_scores = {
            "aws_backdoor": 10,
            "excessive_permissions": 8,
            "encryption_weaknesses": 7,
            "credential_exposure": 9,
        }
        
        total_score = 0
        for finding in findings:
            total_score += risk_scores.get(finding["type"], 5)
            
        # Determine risk level from score
        if total_score >= 15:
            return "critical"
        elif total_score >= 10:
            return "high"
        elif total_score >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_drift_risk(self, additions: List[Dict[str, Any]], removals: List[Dict[str, Any]]) -> str:
        """Calculate risk level based on policy drift."""
        # Risk is higher when security-related configs are removed
        high_risk_terms = [
            "encryption", "security", "monitor", "log", "alert", "auth", "restrict"
        ]
        
        # Count high risk changes
        high_risk_changes = 0
        for removal in removals:
            if any(term in removal["content"].lower() for term in high_risk_terms):
                high_risk_changes += 1
                
        # Check for potentially malicious additions
        suspicious_additions = 0
        for addition in additions:
            if any(re.search(pattern, addition["content"], re.IGNORECASE) 
                   for category in self.poisoning_patterns.values() 
                   for pattern in category):
                suspicious_additions += 1
        
        # Calculate risk
        if suspicious_additions > 0 or high_risk_changes >= 3:
            return "critical"
        elif high_risk_changes > 0 or len(removals) > 5:
            return "high"
        elif len(additions) + len(removals) > 10:
            return "medium"
        else:
            return "low"
    
    def _calculate_benchmark_risk(self, suspicious_sections: List[Dict[str, Any]]) -> str:
        """Calculate risk level based on suspicious benchmark sections."""
        critical_terms = ["backdoor", "bypass", "disable"]
        
        # Count suspicious sections with critical terms
        critical_count = 0
        for section in suspicious_sections:
            if any(term in section["matched_text"].lower() for term in critical_terms):
                critical_count += 1
        
        if critical_count >= 2:
            return "critical"
        elif critical_count == 1 or len(suspicious_sections) >= 3:
            return "high"
        elif len(suspicious_sections) > 0:
            return "medium"
        else:
            return "low"
            
    def _get_remediation(self, category: str, matched_text: str) -> Optional[str]:
        """Generate remediation suggestion based on the finding category."""
        remediations = {
            "aws_backdoor": "Remove overly permissive IAM policies. Follow the principle of least privilege.",
            "excessive_permissions": "Restrict permissions to only those necessary for the required functionality.",
            "encryption_weaknesses": "Enable encryption and use secure TLS/SSL configurations.",
            "credential_exposure": "Remove hardcoded credentials and use a secure secret management solution.",
        }
        
        return remediations.get(category)
        
    def summarize_findings(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the analysis results."""
        if "poisoning_detected" in results and results["poisoning_detected"]:
            summary = [
                f"Security poisoning detected with {results['risk_level']} risk level.",
                f"Found {len(results['findings'])} potential issues:",
            ]
            
            # Group findings by type
            findings_by_type = {}
            for finding in results["findings"]:
                if finding["type"] not in findings_by_type:
                    findings_by_type[finding["type"]] = []
                findings_by_type[finding["type"]].append(finding)
            
            # Summarize each type
            for type_name, findings in findings_by_type.items():
                summary.append(f"- {len(findings)} {type_name.replace('_', ' ')} issues")
                
            # Add remediation suggestions
            if results["suggested_remediations"]:
                summary.append("\nRecommended remediations:")
                for i, remediation in enumerate(results["suggested_remediations"], 1):
                    summary.append(f"{i}. {remediation}")
        
        elif "drift_detected" in results and results["drift_detected"]:
            summary = [
                f"Configuration drift detected with {results['risk_level']} risk level.",
                f"Found {len(results['additions'])} additions and {len(results['removals'])} removals.",
            ]
            
            # Highlight high-risk changes
            if results["risk_level"] in ["high", "critical"]:
                summary.append("\nHigh-risk changes detected:")
                # Show most concerning removals
                security_terms = ["security", "encryption", "auth", "monitor"]
                for removal in results["removals"]:
                    if any(term in removal["content"].lower() for term in security_terms):
                        summary.append(f"- Removed: {removal['content']}")
        
        elif "tampering_detected" in results and results["tampering_detected"]:
            summary = [
                f"Benchmark tampering detected with {results['risk_level']} risk level.",
                f"Found {len(results['suspicious_sections'])} suspicious sections.",
            ]
            
            # List suspicious sections
            if results["recommendations"]:
                summary.append("\nRecommendations:")
                for i, recommendation in enumerate(results["recommendations"][:3], 1):
                    summary.append(f"{i}. {recommendation}")
                
                if len(results["recommendations"]) > 3:
                    summary.append(f"...and {len(results['recommendations']) - 3} more recommendations.")
        
        else:
            summary = ["No security issues detected in the analysis."]
            
        return "\n".join(summary)
