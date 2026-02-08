#!/usr/bin/env python3
"""
AWS Security Agent with Gemini LLM and Export/Remediation Integration

This agent uses a custom MCP server to execute AWS CLI commands and Gemini LLM for analysis.
Includes integrated export and remediation functionality.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add root to path to import root-level modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from aws_security_agent import AWSSecurityAgent as RootAWSSecurityAgent
from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
from src.remediation import PlaybookExecutor, PlaybookLibrary
from src.audit import AWSAuditReport

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()


class AWSSecurityAgent(RootAWSSecurityAgent):
    """
    AWS Security Agent with integrated export and remediation functionality.
    
    Extends the root AWSSecurityAgent with:
    - Multi-format report export (JSON, CSV, HTML)
    - Automated remediation playbooks
    - Approval workflows
    """
    
    def __init__(self, aws_profile: Optional[str] = None, aws_region: Optional[str] = None):
        """
        Initialize the AWS Security Agent.
        
        Args:
            aws_profile: AWS profile to use
            aws_region: AWS region to use
        """
        super().__init__(aws_profile=aws_profile, aws_region=aws_region)
        
        # Initialize exporters
        self.json_exporter = JSONExporter()
        self.csv_exporter = CSVExporter()
        self.html_exporter = HTMLExporter()
        
        # Initialize remediation
        self.playbook_executor = PlaybookExecutor()
        self.playbooks = PlaybookLibrary.get_all_playbooks()
    
    def export_report(self, findings: Dict[str, Any], format: str = "json", 
                      output_path: Optional[str] = None) -> str:
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
            account_id = self.aws_profile or os.getenv("AWS_ACCOUNT_ID", "unknown")
            
            if format == "json":
                exporter = JSONExporter()
                file_path = output_path or f"reports/aws_report_{account_id}.json"
                exporter.export_report(findings, file_path)
                return f"✅ JSON export successful: {file_path}"
                
            elif format == "csv":
                exporter = CSVExporter()
                file_path = output_path or f"reports/aws_findings_{account_id}.csv"
                exporter.export_findings_to_csv(findings.get("findings", []), file_path)
                return f"✅ CSV export successful: {file_path}"
                
            elif format == "html":
                exporter = HTMLExporter()
                file_path = output_path or f"reports/aws_report_{account_id}.html"
                exporter.export_email_template(findings, file_path)
                return f"✅ HTML export successful: {file_path}"
                
            else:
                return f"❌ Unknown format: {format}"
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
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
            
            # Find matching AWS playbook
            matching_playbook = None
            for pb_name, pb in playbooks.items():
                if "AWS" in pb_name:
                    matching_playbook = pb
                    break
            
            if not matching_playbook:
                matching_playbook = playbooks.get("AWS-PUBLIC-S3")
            
            # Execute playbook
            execution = executor.execute_playbook(
                playbook=matching_playbook,
                finding_data={"id": finding_id, "account": self.aws_profile},
                initiated_by=os.getenv("USER", "system"),
                dry_run=dry_run
            )
            
            logger.info(f"Playbook executed: {execution.execution_id}")
            
            return {
                "success": True,
                "execution_id": execution.execution_id,
                "status": execution.status.value,
                "playbook": execution.playbook_name,
                "actions": len(execution.actions),
                "dry_run": dry_run
            }
        except Exception as e:
            logger.error(f"Remediation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_playbooks_for_account(self) -> Dict[str, Any]:
        """
        Get all AWS-specific remediation playbooks available for this account.
        
        Returns:
            Dictionary of available playbooks
        """
        aws_playbooks = {}
        for pb_name, pb in self.playbooks.items():
            if "AWS" in pb_name:
                aws_playbooks[pb_name] = {
                    "name": pb.name,
                    "category": pb.category,
                    "severity": pb.severity,
                    "description": pb.description,
                    "actions": len(pb.actions)
                }
        return aws_playbooks
    
    def generate_and_export_audit(self, export_format: str = "json") -> Dict[str, Any]:
        """
        Generate a complete AWS security audit and export it.
        
        Args:
            export_format: Export format (json, csv, html)
        
        Returns:
            Audit and export results
        """
        try:
            # Generate audit
            audit_report = AWSAuditReport(account_id=self.aws_profile)
            audit_data = audit_report.generate()
            
            # Export
            export_result = self.export_report(audit_data, format=export_format)
            
            return {
                "success": True,
                "audit_id": audit_data.get("id"),
                "findings_count": len(audit_data.get("findings", [])),
                "export_result": export_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Audit generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def display_remediation_summary(self):
        """Display available remediation playbooks and their status."""
        aws_playbooks = self.get_playbooks_for_account()
        
        if not aws_playbooks:
            console.print("[yellow]No AWS remediation playbooks available[/yellow]")
            return
        
        table = Table(title="AWS Remediation Playbooks", box=box.ROUNDED)
        table.add_column("Playbook", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Severity", style="yellow")
        table.add_column("Actions", style="green")
        
        severity_colors = {
            "CRITICAL": "[bold red]CRITICAL[/bold red]",
            "HIGH": "[bold orange]HIGH[/bold orange]",
            "MEDIUM": "[bold yellow]MEDIUM[/bold yellow]",
            "LOW": "[bold green]LOW[/bold green]"
        }
        
        for pb_name, pb_info in sorted(aws_playbooks.items()):
            severity_display = severity_colors.get(pb_info["severity"], pb_info["severity"])
            table.add_row(
                pb_info["name"],
                pb_info["category"],
                severity_display,
                str(pb_info["actions"])
            )
        
        console.print(table)


if __name__ == "__main__":
    # Example usage
    agent = AWSSecurityAgent(aws_profile="default")
    
    # Display remediation options
    agent.display_remediation_summary()
    
    # Example: Generate and export audit
    result = agent.generate_and_export_audit(export_format="json")
    print(f"\nAudit Result: {json.dumps(result, indent=2)}")
