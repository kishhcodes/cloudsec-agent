#!/usr/bin/env python3
"""
CSV Export Module for Audit Reports

Exports audit reports and findings in CSV format for spreadsheet
analysis and data import into other tools.
"""

import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CSVExporter:
    """Export audit reports to CSV format."""
    
    def __init__(self):
        """Initialize the CSV exporter."""
        self.logger = logging.getLogger(__name__)
    
    def export_findings_to_csv(
        self,
        findings: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        include_fields: Optional[List[str]] = None
    ) -> str:
        """
        Export findings to CSV format.
        
        Args:
            findings: List of finding dictionaries
            output_path: File path to save CSV (None = return string)
            include_fields: Specific fields to include (None = all)
            
        Returns:
            CSV content string or path to created CSV file
            
        Raises:
            ValueError: If findings list is empty or invalid
        """
        if not findings:
            raise ValueError("findings list cannot be empty")
        
        try:
            # Determine fieldnames
            if include_fields:
                fieldnames = include_fields
            else:
                # Auto-detect all fields from findings
                fieldnames = self._get_all_fieldnames(findings)
            
            # Generate CSV content
            import io
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()
            
            for finding in findings:
                # Flatten nested objects for CSV
                row = self._flatten_finding(finding, fieldnames)
                writer.writerow(row)
            
            csv_content = csv_buffer.getvalue()
            
            # Save to file if output_path provided
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', newline='') as csvfile:
                    csvfile.write(csv_content)
                self.logger.info(f"Findings exported to CSV: {output_path}")
                return output_path
            
            return csv_content
            
        except IOError as e:
            self.logger.error(f"Failed to write CSV file: {e}")
            raise
    
    def export_report_summary_to_csv(
        self,
        report_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Export report summary to CSV (single row).
        
        Args:
            report_data: Report dictionary
            output_path: File path to save CSV
            
        Returns:
            Path to created CSV file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            summary_row = self._create_summary_row(report_data)
            fieldnames = list(summary_row.keys())
            
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(summary_row)
            
            self.logger.info(f"Report summary exported to CSV: {output_path}")
            return output_path
            
        except IOError as e:
            self.logger.error(f"Failed to write CSV file: {e}")
            raise
    
    def export_findings_by_severity_to_csv(
        self,
        findings: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Export findings grouped by severity to CSV.
        
        Args:
            findings: List of findings
            output_path: File path to save CSV
            
        Returns:
            Path to created CSV file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Add severity grouping info
            enhanced_findings = []
            for finding in findings:
                enhanced = finding.copy()
                enhanced['severity_group'] = finding.get('severity', 'UNKNOWN')
                enhanced_findings.append(enhanced)
            
            # Sort by severity
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            enhanced_findings.sort(
                key=lambda f: severity_order.get(f.get('severity', 'UNKNOWN'), 4)
            )
            
            return self.export_findings_to_csv(enhanced_findings, output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export findings by severity: {e}")
            raise
    
    def export_compliance_summary_to_csv(
        self,
        compliance_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Export compliance framework coverage to CSV.
        
        Args:
            compliance_data: Compliance dictionary with frameworks
            output_path: File path to save CSV
            
        Returns:
            Path to created CSV file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            rows = []
            for framework_name, framework_data in compliance_data.items():
                row = {
                    'Framework': framework_name,
                    'Coverage_Percentage': framework_data.get('coverage', 0),
                    'Controls_Covered': framework_data.get('covered_controls', 0),
                    'Total_Controls': framework_data.get('total_controls', 0),
                    'Status': framework_data.get('status', 'UNKNOWN'),
                    'Gap_Count': framework_data.get('gap_count', 0)
                }
                rows.append(row)
            
            fieldnames = ['Framework', 'Coverage_Percentage', 'Controls_Covered',
                         'Total_Controls', 'Status', 'Gap_Count']
            
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            self.logger.info(f"Compliance summary exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export compliance summary: {e}")
            raise
    
    def export_remediation_tracker_to_csv(
        self,
        findings: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Export findings with remediation tracking columns to CSV.
        
        Args:
            findings: List of findings
            output_path: File path to save CSV
            
        Returns:
            Path to created CSV file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            rows = []
            for idx, finding in enumerate(findings, 1):
                row = {
                    'ID': finding.get('id', f'FIND-{idx}'),
                    'Title': finding.get('title', 'N/A'),
                    'Severity': finding.get('severity', 'UNKNOWN'),
                    'Category': finding.get('category', 'N/A'),
                    'Resource': finding.get('resource', 'N/A'),
                    'Description': finding.get('description', 'N/A'),
                    'Remediation': finding.get('remediation', 'N/A'),
                    'Status': 'New',  # Tracker fields
                    'Assigned_To': '',
                    'Due_Date': '',
                    'Notes': ''
                }
                rows.append(row)
            
            fieldnames = ['ID', 'Title', 'Severity', 'Category', 'Resource',
                         'Description', 'Remediation', 'Status', 'Assigned_To',
                         'Due_Date', 'Notes']
            
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            self.logger.info(f"Remediation tracker exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export remediation tracker: {e}")
            raise
    
    def _get_all_fieldnames(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Extract all unique fieldnames from findings."""
        fieldnames = set()
        for finding in findings:
            fieldnames.update(finding.keys())
        
        # Prioritize important fields at the beginning
        priority_fields = ['id', 'title', 'severity', 'category', 'resource',
                          'description', 'remediation', 'status']
        ordered_fields = [f for f in priority_fields if f in fieldnames]
        remaining_fields = sorted([f for f in fieldnames if f not in priority_fields])
        
        return ordered_fields + remaining_fields
    
    def _flatten_finding(
        self,
        finding: Dict[str, Any],
        fieldnames: List[str]
    ) -> Dict[str, Any]:
        """
        Flatten nested finding object for CSV export.
        
        Args:
            finding: Finding dictionary (may have nested objects)
            fieldnames: Fields to include
            
        Returns:
            Flattened finding dictionary
        """
        row = {}
        for field in fieldnames:
            value = finding.get(field, '')
            
            # Convert complex types to strings
            if isinstance(value, (dict, list)):
                value = str(value)
            elif value is None:
                value = ''
            
            row[field] = value
        
        return row
    
    def _create_summary_row(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single-row summary of the report."""
        findings = report_data.get('findings', [])
        
        return {
            'Report_Date': datetime.now().isoformat(),
            'Account_ID': report_data.get('account_id', 'N/A'),
            'Account_Name': report_data.get('account_name', 'N/A'),
            'Security_Score': report_data.get('security_score', 0),
            'Total_Findings': len(findings),
            'Critical_Findings': len([f for f in findings if f.get('severity') == 'CRITICAL']),
            'High_Findings': len([f for f in findings if f.get('severity') == 'HIGH']),
            'Medium_Findings': len([f for f in findings if f.get('severity') == 'MEDIUM']),
            'Low_Findings': len([f for f in findings if f.get('severity') == 'LOW']),
            'Passed_Checks': len([f for f in findings if f.get('severity') == 'PASS']),
            'Status': self._determine_status(report_data)
        }
    
    def _determine_status(self, report_data: Dict[str, Any]) -> str:
        """Determine overall status from report data."""
        score = report_data.get('security_score', 0)
        findings = report_data.get('findings', [])
        critical = len([f for f in findings if f.get('severity') == 'CRITICAL'])
        
        if critical > 0:
            return 'CRITICAL'
        elif score < 40:
            return 'POOR'
        elif score < 60:
            return 'FAIR'
        elif score < 80:
            return 'GOOD'
        else:
            return 'EXCELLENT'
