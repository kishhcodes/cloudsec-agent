#!/usr/bin/env python3
"""
JSON Export Module for Audit Reports

Exports audit reports in structured JSON format for API integration,
CI/CD pipelines, and tool automation.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class JSONExporter:
    """Export audit reports to JSON format."""
    
    def __init__(self):
        """Initialize the JSON exporter."""
        self.logger = logging.getLogger(__name__)
    
    def export_report(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export report to JSON format.
        
        Args:
            report_data: Dictionary containing report information
            output_path: Optional file path to save JSON
            pretty: Whether to pretty-print JSON (default: True)
            
        Returns:
            JSON string of the report
            
        Raises:
            ValueError: If report_data is invalid
        """
        if not report_data:
            raise ValueError("report_data cannot be empty")
        
        # Prepare JSON-serializable data
        json_data = self._prepare_json_data(report_data)
        
        # Serialize to JSON
        try:
            if pretty:
                json_str = json.dumps(json_data, indent=2, default=str)
            else:
                json_str = json.dumps(json_data, default=str)
        except (TypeError, ValueError) as e:
            self.logger.error(f"Failed to serialize report to JSON: {e}")
            raise ValueError(f"Failed to serialize report: {e}")
        
        # Save to file if path provided
        if output_path:
            try:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(json_str)
                self.logger.info(f"Report exported to JSON: {output_path}")
            except IOError as e:
                self.logger.error(f"Failed to write JSON file: {e}")
                raise
        
        return json_str
    
    def export_findings(
        self,
        findings: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export findings to JSON format.
        
        Args:
            findings: List of finding dictionaries
            output_path: Optional file path to save JSON
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string of findings
        """
        findings_data = {
            "exported_at": datetime.now().isoformat(),
            "finding_count": len(findings),
            "findings": findings
        }
        
        return self.export_report(findings_data, output_path, pretty)
    
    def export_compliance_summary(
        self,
        compliance_data: Dict[str, Any],
        output_path: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export compliance summary to JSON.
        
        Args:
            compliance_data: Compliance framework data
            output_path: Optional file path to save JSON
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string of compliance data
        """
        summary = {
            "exported_at": datetime.now().isoformat(),
            "compliance": compliance_data,
            "frameworks_count": len(compliance_data.get("frameworks", {}))
        }
        
        return self.export_report(summary, output_path, pretty)
    
    def export_for_api_integration(
        self,
        report_data: Dict[str, Any],
        include_fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None
    ) -> str:
        """
        Export report in API-integration friendly format.
        
        Args:
            report_data: Full report data
            include_fields: Fields to include (None = all)
            exclude_fields: Fields to exclude
            
        Returns:
            JSON string optimized for API consumption
        """
        # Filter fields if specified
        if include_fields or exclude_fields:
            filtered_data = self._filter_fields(
                report_data,
                include_fields,
                exclude_fields
            )
        else:
            filtered_data = report_data
        
        # Add API metadata
        api_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "data": filtered_data
        }
        
        return json.dumps(api_data, indent=2, default=str)
    
    def export_for_pipeline(
        self,
        report_data: Dict[str, Any],
        pipeline_type: str = "generic"
    ) -> str:
        """
        Export report optimized for CI/CD pipeline consumption.
        
        Args:
            report_data: Report data
            pipeline_type: Type of pipeline (generic, github, gitlab, jenkins)
            
        Returns:
            JSON string optimized for pipeline
        """
        # Extract critical fields for pipeline
        pipeline_data = {
            "status": self._determine_status(report_data),
            "score": report_data.get("security_score", 0),
            "critical_count": len([f for f in report_data.get("findings", []) 
                                   if f.get("severity") == "CRITICAL"]),
            "high_count": len([f for f in report_data.get("findings", [])
                              if f.get("severity") == "HIGH"]),
            "timestamp": datetime.now().isoformat(),
            "data": report_data
        }
        
        if pipeline_type == "github":
            # GitHub Actions format
            pipeline_data["github_action"] = {
                "conclusion": "failure" if pipeline_data["status"] == "CRITICAL" else "success",
                "summary": f"Security score: {pipeline_data['score']}/100"
            }
        elif pipeline_type == "gitlab":
            # GitLab CI format
            pipeline_data["gitlab"] = {
                "sast": {
                    "schema_version": 14,
                    "vulnerabilities": self._to_sast_vulnerabilities(report_data)
                }
            }
        
        return json.dumps(pipeline_data, indent=2, default=str)
    
    def _prepare_json_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare report data for JSON serialization.
        
        Args:
            report_data: Raw report data
            
        Returns:
            JSON-serializable report data
        """
        prepared = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "export_format": "json",
                "version": "1.0"
            },
            "summary": {
                "account_id": report_data.get("account_id"),
                "account_name": report_data.get("account_name"),
                "security_score": report_data.get("security_score", 0),
                "total_findings": len(report_data.get("findings", [])),
                "critical": len([f for f in report_data.get("findings", [])
                                if f.get("severity") == "CRITICAL"]),
                "high": len([f for f in report_data.get("findings", [])
                            if f.get("severity") == "HIGH"]),
                "medium": len([f for f in report_data.get("findings", [])
                              if f.get("severity") == "MEDIUM"]),
                "low": len([f for f in report_data.get("findings", [])
                           if f.get("severity") == "LOW"]),
            },
            "findings": report_data.get("findings", []),
            "sections": report_data.get("sections", {}),
            "compliance": report_data.get("compliance", {}),
            "recommendations": report_data.get("recommendations", [])
        }
        
        return prepared
    
    def _filter_fields(
        self,
        data: Dict[str, Any],
        include_fields: Optional[List[str]],
        exclude_fields: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Filter data fields based on inclusion/exclusion lists."""
        if include_fields:
            return {k: v for k, v in data.items() if k in include_fields}
        elif exclude_fields:
            return {k: v for k, v in data.items() if k not in exclude_fields}
        return data
    
    def _determine_status(self, report_data: Dict[str, Any]) -> str:
        """Determine overall status from report data."""
        score = report_data.get("security_score", 0)
        critical = len([f for f in report_data.get("findings", [])
                       if f.get("severity") == "CRITICAL"])
        
        if critical > 0:
            return "CRITICAL"
        elif score < 40:
            return "POOR"
        elif score < 60:
            return "FAIR"
        elif score < 80:
            return "GOOD"
        else:
            return "EXCELLENT"
    
    def _to_sast_vulnerabilities(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert findings to GitLab SAST format."""
        vulnerabilities = []
        for finding in report_data.get("findings", []):
            vuln = {
                "id": finding.get("id", "unknown"),
                "category": "sast",
                "name": finding.get("title", "Finding"),
                "message": finding.get("description", ""),
                "severity": self._map_severity_to_sast(finding.get("severity")),
                "confidence": "high",
                "solution": finding.get("remediation", ""),
                "identifiers": [{
                    "type": "finding_id",
                    "name": finding.get("id", "unknown"),
                    "value": finding.get("id", "unknown")
                }],
                "location": {
                    "file": finding.get("resource", "unknown"),
                    "start_line": 1
                }
            }
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _map_severity_to_sast(self, severity: str) -> str:
        """Map finding severity to SAST severity levels."""
        mapping = {
            "CRITICAL": "critical",
            "HIGH": "high",
            "MEDIUM": "medium",
            "LOW": "low"
        }
        return mapping.get(severity, "unknown")
