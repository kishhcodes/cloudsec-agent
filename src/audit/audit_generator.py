#!/usr/bin/env python3
"""
Comprehensive Audit Report Generator

Generates full audit reports for AWS and GCP with PDF export.
Supports EC2, S3, VPC, IAM analysis and multi-cloud environments.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table as PDFTable, TableStyle, PageTemplate, Frame,
    KeepTogether, Image
)
from reportlab.pdfgen import canvas

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


class AuditHeader:
    """Page header for audit reports"""
    
    def __init__(self, title: str, organization: str = "Cloud Security Audit"):
        self.title = title
        self.organization = organization
    
    def draw(self, canvas_obj, doc):
        """Draw header on each page"""
        canvas_obj.saveState()
        
        # Header line
        canvas_obj.setLineWidth(2)
        canvas_obj.setStrokeColor(colors.HexColor("#1f77b4"))
        canvas_obj.line(0.5*inch, letter[1]-0.5*inch, letter[0]-0.5*inch, letter[1]-0.5*inch)
        
        # Organization and title
        canvas_obj.setFont("Helvetica-Bold", 10)
        canvas_obj.drawString(0.75*inch, letter[1]-0.35*inch, self.organization)
        
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawRightString(letter[0]-0.75*inch, letter[1]-0.35*inch, 
                                   f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        canvas_obj.restoreState()


class AuditFooter:
    """Page footer for audit reports"""
    
    def __init__(self, report_id: str):
        self.report_id = report_id
    
    def draw(self, canvas_obj, doc):
        """Draw footer on each page"""
        canvas_obj.saveState()
        
        # Footer line
        canvas_obj.setLineWidth(1)
        canvas_obj.setStrokeColor(colors.HexColor("#cccccc"))
        canvas_obj.line(0.5*inch, 0.5*inch, letter[0]-0.5*inch, 0.5*inch)
        
        # Report ID and page number
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(0.75*inch, 0.3*inch, f"Report ID: {self.report_id}")
        canvas_obj.drawRightString(letter[0]-0.75*inch, 0.3*inch, 
                                   f"Page {doc.page}")
        
        canvas_obj.restoreState()


class AuditReport:
    """Base audit report generator"""
    
    def __init__(self, cloud_provider: str, project_id: str, output_dir: str = "reports"):
        """
        Initialize audit report.
        
        Args:
            cloud_provider: "aws" or "gcp"
            project_id: AWS account ID or GCP project ID
            output_dir: Directory to save reports
        """
        self.cloud_provider = cloud_provider.lower()
        self.project_id = project_id
        self.output_dir = output_dir
        self.report_id = f"{cloud_provider.upper()}-AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.timestamp = datetime.now()
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Report sections
        self.sections = []
        self.summary_data = {
            "total_findings": 0,
            "critical_issues": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "compliant_items": 0
        }
    
    def add_section(self, title: str, content: Dict[str, Any]) -> None:
        """Add a section to the audit report"""
        self.sections.append({
            "title": title,
            "content": content,
            "timestamp": datetime.now()
        })
    
    def add_iam_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add IAM security analysis section"""
        self.add_section("IAM Security Analysis", analysis)
        self._update_summary(analysis)
    
    def add_storage_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add storage (S3 or GCS) security analysis section"""
        self.add_section("Storage Security Analysis", analysis)
        self._update_summary(analysis)
    
    def add_compute_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add compute (EC2 or GCE) security analysis section"""
        self.add_section("Compute Security Analysis", analysis)
        self._update_summary(analysis)
    
    def add_network_analysis(self, analysis: Dict[str, Any]) -> None:
        """Add network (VPC) security analysis section"""
        self.add_section("Network Security Analysis", analysis)
        self._update_summary(analysis)
    
    def _update_summary(self, analysis: Dict[str, Any]) -> None:
        """Update summary statistics from analysis data"""
        if isinstance(analysis, dict):
            # Count findings
            findings = analysis.get("findings", [])
            if isinstance(findings, list):
                self.summary_data["total_findings"] += len(findings)
                
                for finding in findings:
                    severity = finding.get("severity", "").lower() if isinstance(finding, dict) else ""
                    if "critical" in severity:
                        self.summary_data["critical_issues"] += 1
                    elif "high" in severity:
                        self.summary_data["high_risk"] += 1
                    elif "medium" in severity:
                        self.summary_data["medium_risk"] += 1
                    elif "low" in severity:
                        self.summary_data["low_risk"] += 1
                    elif "compliant" in severity or "pass" in severity:
                        self.summary_data["compliant_items"] += 1
    
    def generate_pdf(self) -> str:
        """Generate PDF report and return file path"""
        output_path = os.path.join(
            self.output_dir,
            f"{self.report_id}.pdf"
        )
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.0*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story with content
        story = []
        styles = self._get_styles()
        
        # Title page
        story.extend(self._build_title_page(styles))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_summary(styles))
        story.append(PageBreak())
        
        # Detailed sections
        for section in self.sections:
            story.extend(self._build_section(section, styles))
            story.append(PageBreak())
        
        # Recommendations
        story.extend(self._build_recommendations(styles))
        
        # Build PDF with header and footer
        header = AuditHeader(f"{self.cloud_provider.upper()} Security Audit", "Cloud Security Assistant")
        footer = AuditFooter(self.report_id)
        
        # Add header/footer to document
        doc.build(story, onFirstPage=lambda c, d: [header.draw(c, d), footer.draw(c, d)],
                 onLaterPages=lambda c, d: [header.draw(c, d), footer.draw(c, d)])
        
        console.print(f"[green]✓[/green] PDF report generated: [bold]{output_path}[/bold]")
        return output_path
    
    def _get_styles(self) -> Dict[str, ParagraphStyle]:
        """Get default styles for PDF"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='Title_Custom',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Heading_Custom',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor("#1f77b4"),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Critical',
            parent=styles['Normal'],
            textColor=colors.HexColor("#d32f2f"),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='High',
            parent=styles['Normal'],
            textColor=colors.HexColor("#f57c00"),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Medium',
            parent=styles['Normal'],
            textColor=colors.HexColor("#fbc02d"),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Low',
            parent=styles['Normal'],
            textColor=colors.HexColor("#0288d1"),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Pass',
            parent=styles['Normal'],
            textColor=colors.HexColor("#388e3c"),
            fontName='Helvetica-Bold'
        ))
        
        return styles
    
    def _build_title_page(self, styles) -> List:
        """Build title page content"""
        story = []
        
        story.append(Spacer(1, 2*inch))
        
        # Title
        title = f"{self.cloud_provider.upper()} Security Audit Report"
        story.append(Paragraph(title, styles['Title_Custom']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        story.append(Paragraph(
            f"Project/Account: <b>{self.project_id}</b>",
            styles['Heading2']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Report info
        info_data = [
            ["Report ID:", self.report_id],
            ["Generated:", self.timestamp.strftime("%B %d, %Y at %H:%M:%S")],
            ["Cloud Provider:", self.cloud_provider.upper()],
            ["Report Type:", "Comprehensive Security Audit"]
        ]
        
        info_table = PDFTable(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 1*inch))
        
        # Disclaimer
        story.append(Paragraph(
            "<i>This audit report contains confidential security analysis. "
            "Unauthorized access, use, or distribution is prohibited.</i>",
            styles['Normal']
        ))
        
        return story
    
    def _build_summary(self, styles) -> List:
        """Build executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", styles['Heading_Custom']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary statistics
        summary_text = f"""
        This comprehensive security audit examines your {self.cloud_provider.upper()} infrastructure
        across multiple security domains including Identity & Access Management (IAM), Storage,
        Compute Resources, and Networking. The assessment identifies security gaps, misconfigurations,
        and provides actionable recommendations for remediation.
        <br/><br/>
        <b>Audit Scope:</b><br/>
        • Identity & Access Management (IAM)<br/>
        • Storage Security (S3/GCS)<br/>
        • Compute Resources (EC2/GCE)<br/>
        • Network & VPC Configuration<br/>
        <br/>
        <b>Total Findings: {self.summary_data['total_findings']}</b><br/>
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary table
        summary_data = [
            ["Critical", "High Risk", "Medium Risk", "Low Risk", "Compliant"],
            [
                str(self.summary_data['critical_issues']),
                str(self.summary_data['high_risk']),
                str(self.summary_data['medium_risk']),
                str(self.summary_data['low_risk']),
                str(self.summary_data['compliant_items'])
            ]
        ]
        
        summary_table = PDFTable(summary_data, colWidths=[1.2*inch]*5)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#ffebee")),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor("#fff3e0")),
            ('BACKGROUND', (2, 1), (2, 1), colors.HexColor("#fffde7")),
            ('BACKGROUND', (3, 1), (3, 1), colors.HexColor("#e3f2fd")),
            ('BACKGROUND', (4, 1), (4, 1), colors.HexColor("#e8f5e9")),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('TOPPADDING', (0, 1), (-1, 1), 12),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ]))
        
        story.append(summary_table)
        
        return story
    
    def _build_section(self, section: Dict, styles) -> List:
        """Build a detailed section"""
        story = []
        
        # Section title
        story.append(Paragraph(section['title'], styles['Heading_Custom']))
        story.append(Spacer(1, 0.2*inch))
        
        content = section['content']
        
        # Section description
        if 'description' in content:
            story.append(Paragraph(content['description'], styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Findings
        if 'findings' in content and content['findings']:
            story.append(Paragraph("Findings", styles['SectionHeading']))
            
            for finding in content['findings']:
                if isinstance(finding, dict):
                    severity = finding.get('severity', 'Unknown').lower()
                    title = finding.get('title', 'Untitled')
                    description = finding.get('description', '')
                    
                    # Choose style based on severity
                    if 'critical' in severity:
                        severity_style = styles['Critical']
                        severity_text = '⚠ CRITICAL'
                    elif 'high' in severity:
                        severity_style = styles['High']
                        severity_text = '⚠ HIGH'
                    elif 'medium' in severity:
                        severity_style = styles['Medium']
                        severity_text = '⚠ MEDIUM'
                    elif 'low' in severity:
                        severity_style = styles['Low']
                        severity_text = 'ℹ LOW'
                    else:
                        severity_style = styles['Pass']
                        severity_text = '✓ PASS'
                    
                    # Finding header
                    story.append(Paragraph(f"{severity_text}: {title}", severity_style))
                    
                    # Finding description
                    if description:
                        story.append(Paragraph(description, styles['Normal']))
                    
                    # Recommendation
                    if 'recommendation' in finding:
                        story.append(Paragraph(
                            f"<b>Recommendation:</b> {finding['recommendation']}",
                            styles['Normal']
                        ))
                    
                    story.append(Spacer(1, 0.1*inch))
        
        # Summary points
        if 'summary' in content:
            story.append(Paragraph("Summary", styles['SectionHeading']))
            for point in content['summary']:
                story.append(Paragraph(f"• {point}", styles['Normal']))
        
        return story
    
    def _build_recommendations(self, styles) -> List:
        """Build recommendations section"""
        story = []
        
        story.append(Paragraph("Remediation Roadmap", styles['Heading_Custom']))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = [
            ("Immediate (0-7 days)", [
                "Address all Critical findings",
                "Disable unused IAM users and roles",
                "Enable MFA on root accounts",
                "Review public access to storage buckets"
            ]),
            ("Short-term (1-4 weeks)", [
                "Remediate all High-risk findings",
                "Implement encryption at rest",
                "Enable logging on all resources",
                "Review and update security group rules"
            ]),
            ("Medium-term (1-2 months)", [
                "Remediate Medium-risk findings",
                "Implement automated compliance monitoring",
                "Deploy intrusion detection",
                "Review backup and disaster recovery procedures"
            ]),
            ("Long-term (Ongoing)", [
                "Continuous monitoring and alerting",
                "Regular security assessments",
                "Keep systems patched and updated",
                "Security training for teams"
            ])
        ]
        
        for phase, items in recommendations:
            story.append(Paragraph(phase, styles['SectionHeading']))
            for item in items:
                story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def display_summary(self) -> None:
        """Display summary to console"""
        table = Table(
            title=f"[bold]{self.cloud_provider.upper()} Audit Summary[/bold]",
            box=box.ROUNDED
        )
        
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")
        
        table.add_row("Total Findings", str(self.summary_data['total_findings']))
        table.add_row("[red]Critical Issues[/red]", str(self.summary_data['critical_issues']))
        table.add_row("[yellow]High Risk[/yellow]", str(self.summary_data['high_risk']))
        table.add_row("[yellow3]Medium Risk[/yellow3]", str(self.summary_data['medium_risk']))
        table.add_row("[blue]Low Risk[/blue]", str(self.summary_data['low_risk']))
        table.add_row("[green]Compliant Items[/green]", str(self.summary_data['compliant_items']))
        
        console.print(table)


class AWSAuditReport(AuditReport):
    """AWS-specific audit report"""
    
    def __init__(self, account_id: str, output_dir: str = "reports"):
        super().__init__("aws", account_id, output_dir)


class GCPAuditReport(AuditReport):
    """GCP-specific audit report"""
    
    def __init__(self, project_id: str, output_dir: str = "reports"):
        super().__init__("gcp", project_id, output_dir)
