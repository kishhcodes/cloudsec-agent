# src/agents/security_analyzer/agent.py
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from .analyzer import SecurityAnalyzer
from .extractor import ComplianceExtractor

class SecurityPoisoningAgent:
    """
    Agent that detects and analyzes security poisoning in compliance frameworks
    and configurations.
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize the security poisoning agent.
        
        Args:
            google_api_key: Google API key for LLM integration
        """
        self.analyzer = SecurityAnalyzer()
        self.extractor = ComplianceExtractor()
        
        # Initialize LLM if API key is available
        self.api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.2
            )
        else:
            self.llm = None
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a configuration file for potential security poisoning.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dict with analysis results
        """
        # Extract configuration from file
        content, format_type, error = self.extractor.extract_from_file(file_path)
        if error:
            return {
                "success": False,
                "error": error
            }
            
        # Determine framework type based on file path and content
        framework_type = self._determine_framework_type(file_path, content)
            
        # Analyze the configuration
        analysis_results = self.analyzer.analyze_configuration(content, framework_type)
        
        # Add file info to results
        analysis_results["file_path"] = file_path
        analysis_results["format_type"] = format_type
        analysis_results["success"] = True
        
        # Add LLM explanation if available
        if self.llm and analysis_results["poisoning_detected"]:
            explanation = self._generate_explanation(content, analysis_results)
            analysis_results["explanation"] = explanation
            
        return analysis_results
    
    def analyze_benchmark(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a compliance benchmark document for potential tampering.
        
        Args:
            file_path: Path to the benchmark file
            
        Returns:
            Dict with analysis results
        """
        # Extract content from file
        content, _, error = self.extractor.extract_from_file(file_path)
        if error:
            return {
                "success": False,
                "error": error
            }
            
        # Analyze the benchmark
        analysis_results = self.analyzer.detect_poisoned_benchmarks(content)
        
        # Add file info to results
        analysis_results["file_path"] = file_path
        analysis_results["success"] = True
        
        # Add LLM explanation if available
        if self.llm and analysis_results["tampering_detected"]:
            explanation = self._generate_benchmark_explanation(content, analysis_results)
            analysis_results["explanation"] = explanation
            
        return analysis_results
    
    def compare_configurations(self, current_file: str, reference_file: str) -> Dict[str, Any]:
        """
        Compare a current configuration against a reference to detect drift or tampering.
        
        Args:
            current_file: Path to the current configuration file
            reference_file: Path to the reference (known good) configuration file
            
        Returns:
            Dict with comparison results
        """
        # Extract content from both files
        current_content, current_format, error1 = self.extractor.extract_from_file(current_file)
        if error1:
            return {
                "success": False,
                "error": f"Error with current file: {error1}"
            }
            
        reference_content, reference_format, error2 = self.extractor.extract_from_file(reference_file)
        if error2:
            return {
                "success": False,
                "error": f"Error with reference file: {error2}"
            }
            
        # Verify that formats match
        if current_format != reference_format:
            return {
                "success": False,
                "error": f"Format mismatch: current is {current_format}, reference is {reference_format}"
            }
            
        # Analyze drift between configurations
        drift_results = self.analyzer.analyze_policy_drift(current_content, reference_content)
        
        # Add file info to results
        drift_results["current_file"] = current_file
        drift_results["reference_file"] = reference_file
        drift_results["format"] = current_format
        drift_results["success"] = True
        
        # Add LLM explanation if available and drift detected
        if self.llm and drift_results["drift_detected"]:
            explanation = self._generate_drift_explanation(
                current_content, 
                reference_content, 
                drift_results
            )
            drift_results["explanation"] = explanation
            
        return drift_results
    
    def analyze_directory(self, dir_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        Analyze all configuration files in a directory for security poisoning.
        
        Args:
            dir_path: Path to the directory
            recursive: Whether to search subdirectories
            
        Returns:
            Dict with aggregated analysis results
        """
        # Extract configurations from directory
        extraction_results = self.extractor.extract_from_directory(dir_path, recursive)
        
        if not extraction_results:
            return {
                "success": False,
                "error": "No configuration files found"
            }
        
        # Analyze each extracted configuration
        analysis_results = []
        poisoning_detected = False
        highest_risk = "low"
        
        risk_levels = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        for extraction in extraction_results:
            if "error" in extraction:
                analysis_results.append({
                    "file_path": extraction.get("file_path", "unknown"),
                    "success": False,
                    "error": extraction["error"]
                })
                continue
                
            # Determine framework type
            framework_type = self._determine_framework_type(
                extraction["file_path"], 
                extraction["content"]
            )
                
            # Analyze the configuration
            result = self.analyzer.analyze_configuration(
                extraction["content"], 
                framework_type
            )
            
            # Add file info
            result["file_path"] = extraction["file_path"]
            result["format_type"] = extraction["format"]
            result["success"] = True
            
            # Track overall poisoning detection
            if result.get("poisoning_detected", False):
                poisoning_detected = True
                
                # Track highest risk level
                current_risk = risk_levels.get(result.get("risk_level", "low"), 1)
                highest_risk_level = risk_levels.get(highest_risk, 1)
                
                if current_risk > highest_risk_level:
                    highest_risk = result.get("risk_level", "low")
            
            analysis_results.append(result)
        
        # Create summary
        summary = {
            "directory": dir_path,
            "recursive": recursive,
            "files_analyzed": len(analysis_results),
            "poisoning_detected": poisoning_detected,
            "highest_risk_level": highest_risk,
            "analysis_results": analysis_results,
            "success": True
        }
        
        # Count files with issues
        files_with_issues = sum(1 for r in analysis_results 
                              if r.get("success", False) and r.get("poisoning_detected", False))
                              
        summary["files_with_issues"] = files_with_issues
        
        return summary
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about security poisoning.
        
        Args:
            query: The user's query
            
        Returns:
            Dict with response and information
        """
        if not self.llm:
            return {
                "success": False,
                "error": "LLM not available. Set GOOGLE_API_KEY to enable this feature."
            }
            
        # Prepare system prompt
        system_prompt = """You are a Cloud Security Poisoning Detection expert. Your task is to help 
identify and explain potential security poisoning in cloud compliance configurations and benchmarks. 
Security poisoning refers to malicious modifications of security configurations, compliance benchmarks, 
or infrastructure that introduce vulnerabilities or backdoors while appearing legitimate.

Focus on answering questions related to:
1. What security poisoning is and how to identify it
2. Common patterns of security poisoning in cloud environments
3. How to detect tampering in compliance benchmarks
4. Remediation steps for identified poisoning

Use technical details when appropriate but explain concepts clearly.
"""
        
        # Create messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        # Generate response
        response = self.llm.invoke(messages)
        
        return {
            "query": query,
            "response": response.content,
            "success": True
        }
    
    def generate_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate a summary of analysis results.
        
        Args:
            results: Analysis results to summarize
            
        Returns:
            Summary text
        """
        if "analysis_results" in results:
            # This is a directory analysis summary
            total_files = results["files_analyzed"]
            files_with_issues = results["files_with_issues"]
            highest_risk = results["highest_risk_level"]
            
            summary = [
                f"Analyzed {total_files} configuration files.",
                f"Found security issues in {files_with_issues} files.",
                f"Highest risk level detected: {highest_risk}."
            ]
            
            if files_with_issues > 0:
                # List the top issues by risk
                issues = sorted(
                    [r for r in results["analysis_results"] if r.get("poisoning_detected", False)],
                    key=lambda x: {
                        "critical": 4,
                        "high": 3,
                        "medium": 2,
                        "low": 1
                    }.get(x.get("risk_level", "low"), 0),
                    reverse=True
                )
                
                summary.append("\nTop issues:")
                for i, issue in enumerate(issues[:3], 1):
                    file_name = os.path.basename(issue["file_path"])
                    summary.append(f"{i}. {file_name} - {issue['risk_level']} risk")
                    if issue.get("findings"):
                        finding_types = set(f["type"] for f in issue["findings"])
                        summary.append(f"   Issues: {', '.join(t.replace('_', ' ') for t in finding_types)}")
                
        elif "poisoning_detected" in results and results["success"]:
            # This is a single file analysis
            summary = [self.analyzer.summarize_findings(results)]
            
        elif "drift_detected" in results and results["success"]:
            # This is a drift analysis
            summary = [
                f"Configuration drift analysis between:",
                f"- Current: {os.path.basename(results['current_file'])}",
                f"- Reference: {os.path.basename(results['reference_file'])}",
                f"Risk level: {results['risk_level']}",
                f"Found {len(results['additions'])} additions and {len(results['removals'])} removals."
            ]
            
            if results.get("explanation"):
                summary.append("\n" + results["explanation"])
                
        else:
            summary = ["No analysis results available."]
            
        return "\n".join(summary)
    
    def _determine_framework_type(self, file_path: str, content: str) -> str:
        """Determine the compliance framework type from file path and content."""
        file_name = os.path.basename(file_path).lower()
        
        if "cis" in file_name and "aws" in file_name:
            return "cis_aws"
        elif "pci" in file_name or "dss" in file_name:
            return "pci_dss"
        elif "hipaa" in file_name:
            return "hipaa"
        elif "nist" in file_name:
            return "nist"
        elif "soc" in file_name:
            return "soc2"
        
        # Try to determine from content
        if "CIS" in content and "AWS" in content:
            return "cis_aws"
        elif "PCI" in content and "DSS" in content:
            return "pci_dss"
        elif "HIPAA" in content:
            return "hipaa"
        elif "NIST" in content:
            return "nist"
        elif "SOC" in content and "Trust" in content:
            return "soc2"
            
        # Default to generic
        return "generic"
    
    def _generate_explanation(self, content: str, results: Dict[str, Any]) -> str:
        """Generate an LLM explanation for the security poisoning findings."""
        if not self.llm:
            return ""
            
        # Extract relevant parts of findings
        findings_summary = "\n".join([
            f"- {finding['type']}: {finding['matched_text']}" 
            for finding in results.get("findings", [])[:5]
        ])
            
        # Create prompt for LLM
        prompt = f"""Analyze the following potential security poisoning findings in a {results['framework_type']} compliance configuration:

Risk Level: {results['risk_level']}

Key Findings:
{findings_summary}

Explain in detail:
1. What security risks these findings represent
2. How they could be exploited
3. Recommended remediation steps

Keep your explanation technical but accessible.
"""

        # Generate explanation
        messages = [
            SystemMessage(content="You are a Cloud Security Poisoning Detection expert."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _generate_benchmark_explanation(self, content: str, results: Dict[str, Any]) -> str:
        """Generate an LLM explanation for benchmark tampering findings."""
        if not self.llm:
            return ""
            
        # Extract relevant parts of suspicious sections
        sections_summary = "\n".join([
            f"- {section['description']}: {section['matched_text']} in section '{section['section']}'" 
            for section in results.get("suspicious_sections", [])[:5]
        ])
            
        # Create prompt for LLM
        prompt = f"""Analyze the following potential tampering in a compliance benchmark document:

Risk Level: {results['risk_level']}

Suspicious Sections:
{sections_summary}

Explain in detail:
1. Why these sections are suspicious
2. What legitimate benchmark text would typically look like
3. How this tampering could compromise security
4. Recommendations for validation and remediation

Keep your explanation technical but accessible.
"""

        # Generate explanation
        messages = [
            SystemMessage(content="You are a Cloud Security Benchmark expert."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _generate_drift_explanation(self, current: str, reference: str, results: Dict[str, Any]) -> str:
        """Generate an LLM explanation for configuration drift findings."""
        if not self.llm:
            return ""
            
        # Extract relevant parts of additions and removals
        additions_summary = "\n".join([
            f"+ {addition['content']}" for addition in results.get("additions", [])[:5]
        ])
        
        removals_summary = "\n".join([
            f"- {removal['content']}" for removal in results.get("removals", [])[:5]
        ])
            
        # Create prompt for LLM
        prompt = f"""Analyze the following configuration drift between a current configuration and a reference (known good) configuration:

Risk Level: {results['risk_level']}

Key Additions:
{additions_summary}

Key Removals:
{removals_summary}

Explain in detail:
1. The security implications of these changes
2. Whether this drift appears suspicious or malicious
3. Which changes pose the highest security risk and why
4. Recommended actions to address any security concerns

Keep your explanation technical but accessible.
"""

        # Generate explanation
        messages = [
            SystemMessage(content="You are a Cloud Security Configuration expert."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
