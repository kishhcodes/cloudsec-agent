#!/usr/bin/env python3
"""
HTML Export Module for Audit Reports

Exports audit reports in HTML format with responsive email templates,
inline CSS, and professional styling.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class HTMLExporter:
    """Export audit reports to HTML format with email templates."""
    
    def __init__(self):
        """Initialize the HTML exporter."""
        self.logger = logging.getLogger(__name__)
    
    def export_report_to_html(
        self,
        report_data: Dict[str, Any],
        output_path: Optional[str] = None,
        include_toc: bool = True,
        include_charts: bool = True
    ) -> str:
        """
        Export full report to HTML.
        
        Args:
            report_data: Report dictionary
            output_path: File path to save HTML (None = return string)
            include_toc: Whether to include table of contents
            include_charts: Whether to include embedded charts
            
        Returns:
            HTML content string or path to created HTML file
        """
        try:
            html_content = self._build_html_report(
                report_data,
                include_toc,
                include_charts
            )
            
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(html_content)
                self.logger.info(f"Report exported to HTML: {output_path}")
                return output_path
            
            return html_content
            
        except IOError as e:
            self.logger.error(f"Failed to write HTML file: {e}")
            raise
    
    def export_email_template(
        self,
        report_data: Dict[str, Any],
        output_path: str,
        recipient_name: Optional[str] = None,
        include_cta: bool = True
    ) -> str:
        """
        Export email-friendly HTML template.
        
        Args:
            report_data: Report dictionary
            output_path: File path to save HTML
            recipient_name: Name to include in greeting
            include_cta: Include call-to-action buttons
            
        Returns:
            Path to created HTML file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            html_content = self._build_email_template(
                report_data,
                recipient_name,
                include_cta
            )
            
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Email template exported to HTML: {output_path}")
            return output_path
            
        except IOError as e:
            self.logger.error(f"Failed to write HTML file: {e}")
            raise
    
    def export_executive_summary_html(
        self,
        report_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Export executive summary as standalone HTML.
        
        Args:
            report_data: Report dictionary
            output_path: File path to save HTML
            
        Returns:
            Path to created HTML file
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            html_content = self._build_executive_summary(report_data)
            
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Executive summary exported to HTML: {output_path}")
            return output_path
            
        except IOError as e:
            self.logger.error(f"Failed to write HTML file: {e}")
            raise
    
    def _build_html_report(
        self,
        report_data: Dict[str, Any],
        include_toc: bool,
        include_charts: bool
    ) -> str:
        """Build complete HTML report."""
        account_name = report_data.get('account_name', 'Cloud Account')
        score = report_data.get('security_score', 0)
        findings = report_data.get('findings', [])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report - {account_name}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <h1>Security Audit Report</h1>
                <p class="subtitle">{account_name}</p>
                <p class="report-date">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </header>
        
        <div class="score-card score-{self._get_score_class(score)}">
            <div class="score-value">{score}</div>
            <div class="score-label">Security Score</div>
            <div class="score-status">{self._get_score_status(score)}</div>
        </div>
        
        <section class="findings-summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item critical">
                    <span class="count">{len([f for f in findings if f.get('severity') == 'CRITICAL'])}</span>
                    <span class="label">Critical</span>
                </div>
                <div class="summary-item high">
                    <span class="count">{len([f for f in findings if f.get('severity') == 'HIGH'])}</span>
                    <span class="label">High</span>
                </div>
                <div class="summary-item medium">
                    <span class="count">{len([f for f in findings if f.get('severity') == 'MEDIUM'])}</span>
                    <span class="label">Medium</span>
                </div>
                <div class="summary-item low">
                    <span class="count">{len([f for f in findings if f.get('severity') == 'LOW'])}</span>
                    <span class="label">Low</span>
                </div>
            </div>
        </section>
        
        {self._build_findings_section(findings)}
        {self._build_compliance_section(report_data.get('compliance', {}))}
        {self._build_recommendations_section(report_data.get('recommendations', []))}
        
        <footer class="footer">
            <p>&copy; 2026 Cloud Security Team. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _build_email_template(
        self,
        report_data: Dict[str, Any],
        recipient_name: Optional[str],
        include_cta: bool
    ) -> str:
        """Build email-friendly HTML template."""
        account_name = report_data.get('account_name', 'Cloud Account')
        score = report_data.get('security_score', 0)
        findings = report_data.get('findings', [])
        
        greeting = f"Hi {recipient_name}," if recipient_name else "Hello,"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report - {account_name}</title>
    <style>
        {self._get_email_css()}
    </style>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px;">Security Audit Report</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">{account_name}</p>
        </div>
        
        <!-- Greeting -->
        <div style="padding: 30px 20px;">
            <p style="margin: 0 0 20px 0; font-size: 16px;">{greeting}</p>
            <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.6;">
                Your latest security audit is ready for review. Below is a summary of key findings and recommendations.
            </p>
        </div>
        
        <!-- Score Card -->
        <div style="padding: 0 20px 20px 20px;">
            <div style="background: {self._get_score_bg_color(score)}; color: white; padding: 30px; border-radius: 8px; text-align: center;">
                <div style="font-size: 48px; font-weight: bold; margin-bottom: 10px;">{score}</div>
                <div style="font-size: 18px; margin-bottom: 5px;">Security Score</div>
                <div style="font-size: 12px; opacity: 0.9;">{self._get_score_status(score)}</div>
            </div>
        </div>
        
        <!-- Summary -->
        <div style="padding: 0 20px 20px 20px;">
            <h2 style="margin: 0 0 15px 0; font-size: 20px; color: #333;">Key Metrics</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Critical</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; color: #dc3545;"><strong>{len([f for f in findings if f.get('severity') == 'CRITICAL'])}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>High</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; color: #fd7e14;"><strong>{len([f for f in findings if f.get('severity') == 'HIGH'])}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Medium</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right; color: #ffc107;"><strong>{len([f for f in findings if f.get('severity') == 'MEDIUM'])}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px;"><strong>Low</strong></td>
                    <td style="padding: 10px; text-align: right; color: #17a2b8;"><strong>{len([f for f in findings if f.get('severity') == 'LOW'])}</strong></td>
                </tr>
            </table>
        </div>
        
        <!-- Critical Findings Preview -->
        {self._build_email_critical_findings(findings)}
        
        <!-- CTA Buttons -->
        {self._build_cta_buttons() if include_cta else ''}
        
        <!-- Footer -->
        <div style="background-color: #f9f9f9; padding: 20px; text-align: center; border-top: 1px solid #eee;">
            <p style="margin: 0; font-size: 12px; color: #666;">
                &copy; 2026 Cloud Security Team<br>
                This report contains sensitive security information.
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _build_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Build executive summary HTML."""
        account_name = report_data.get('account_name', 'Cloud Account')
        score = report_data.get('security_score', 0)
        findings = report_data.get('findings', [])
        compliance = report_data.get('compliance', {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Summary - {account_name}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Executive Summary</h1>
            <p class="subtitle">{account_name}</p>
        </header>
        
        <section class="executive-section">
            <h2>Security Posture</h2>
            <p>The security assessment of <strong>{account_name}</strong> reveals a security score of <strong>{score}/100</strong>.</p>
            <p>{self._get_executive_assessment(score)}</p>
        </section>
        
        <section class="executive-section">
            <h2>Key Findings</h2>
            <ul>
                <li><strong>{len([f for f in findings if f.get('severity') == 'CRITICAL'])}</strong> Critical issues requiring immediate attention</li>
                <li><strong>{len([f for f in findings if f.get('severity') == 'HIGH'])}</strong> High-risk findings</li>
                <li><strong>{len([f for f in findings if f.get('severity') == 'MEDIUM'])}</strong> Medium-priority items</li>
                <li><strong>{len([f for f in findings if f.get('severity') == 'LOW'])}</strong> Low-risk findings</li>
            </ul>
        </section>
        
        {self._build_compliance_overview(compliance)}
        
        <section class="executive-section">
            <h2>Next Steps</h2>
            <ol>
                <li>Review critical findings in detail</li>
                <li>Prioritize remediation based on risk level</li>
                <li>Implement recommended security controls</li>
                <li>Schedule follow-up audit in 30 days</li>
            </ol>
        </section>
    </div>
</body>
</html>"""
        
        return html
    
    def _build_findings_section(self, findings: List[Dict[str, Any]]) -> str:
        """Build findings section HTML."""
        if not findings:
            return "<section><h2>Findings</h2><p>No findings detected.</p></section>"
        
        findings_html = "<section><h2>Findings</h2><div class='findings-list'>"
        
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            title = finding.get('title', 'Unknown Finding')
            description = finding.get('description', 'N/A')
            remediation = finding.get('remediation', 'N/A')
            
            findings_html += f"""
            <div class="finding-card {severity.lower()}">
                <div class="finding-header">
                    <span class="severity-badge {severity.lower()}">{severity}</span>
                    <h3>{title}</h3>
                </div>
                <p class="finding-description">{description}</p>
                <div class="finding-remediation">
                    <strong>Remediation:</strong> {remediation}
                </div>
            </div>
            """
        
        findings_html += "</div></section>"
        return findings_html
    
    def _build_compliance_section(self, compliance: Dict[str, Any]) -> str:
        """Build compliance section HTML."""
        if not compliance:
            return ""
        
        compliance_html = "<section><h2>Compliance Status</h2><div class='compliance-grid'>"
        
        for framework, data in compliance.items():
            coverage = data.get('coverage', 0)
            status = data.get('status', 'UNKNOWN')
            
            compliance_html += f"""
            <div class="compliance-card {status.lower()}">
                <h4>{framework}</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {coverage}%"></div>
                </div>
                <p>{coverage}% Coverage</p>
            </div>
            """
        
        compliance_html += "</div></section>"
        return compliance_html
    
    def _build_recommendations_section(self, recommendations: List[str]) -> str:
        """Build recommendations section HTML."""
        if not recommendations:
            return ""
        
        recs_html = "<section><h2>Recommendations</h2><ul>"
        for rec in recommendations:
            recs_html += f"<li>{rec}</li>"
        recs_html += "</ul></section>"
        
        return recs_html
    
    def _build_email_critical_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Build critical findings for email."""
        critical = [f for f in findings if f.get('severity') == 'CRITICAL']
        
        if not critical:
            return ""
        
        html = '<div style="padding: 20px; background-color: #fff3cd; border-left: 4px solid #dc3545;">'
        html += '<h3 style="margin-top: 0; color: #dc3545;">⚠️ Critical Issues Requiring Immediate Attention</h3>'
        
        for finding in critical[:3]:  # Show top 3
            html += f'<p style="margin: 10px 0;"><strong>{finding.get("title", "N/A")}</strong></p>'
        
        if len(critical) > 3:
            html += f'<p style="margin: 10px 0; font-size: 12px;"><em>...and {len(critical) - 3} more critical issues</em></p>'
        
        html += '</div>'
        return html
    
    def _build_cta_buttons(self) -> str:
        """Build call-to-action buttons."""
        return """
        <div style="padding: 30px 20px; text-align: center;">
            <table style="width: 100%; max-width: 400px; margin: 0 auto;">
                <tr>
                    <td style="padding: 10px;">
                        <a href="#" style="display: inline-block; padding: 12px 24px; background-color: #667eea; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">View Full Report</a>
                    </td>
                    <td style="padding: 10px;">
                        <a href="#" style="display: inline-block; padding: 12px 24px; background-color: #17a2b8; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">View Dashboard</a>
                    </td>
                </tr>
            </table>
        </div>
        """
    
    def _build_compliance_overview(self, compliance: Dict[str, Any]) -> str:
        """Build compliance overview for executive summary."""
        if not compliance:
            return ""
        
        html = '<section class="executive-section"><h2>Compliance Frameworks</h2><ul>'
        for framework, data in compliance.items():
            coverage = data.get('coverage', 0)
            html += f'<li><strong>{framework}:</strong> {coverage}% compliant</li>'
        html += '</ul></section>'
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get main CSS styles."""
        return """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; color: #333; }
        .container { max-width: 900px; margin: 0 auto; background-color: white; }
        header.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 30px; text-align: center; }
        header.header h1 { font-size: 36px; margin-bottom: 10px; }
        header.header .subtitle { font-size: 18px; opacity: 0.9; }
        header.header .report-date { font-size: 12px; opacity: 0.8; margin-top: 10px; }
        
        .score-card { padding: 40px; text-align: center; margin: 40px; border-radius: 8px; background-color: #f9f9f9; }
        .score-card.score-excellent { border-left: 4px solid #28a745; }
        .score-card.score-good { border-left: 4px solid #17a2b8; }
        .score-card.score-fair { border-left: 4px solid #ffc107; }
        .score-card.score-poor { border-left: 4px solid #fd7e14; }
        .score-card.score-critical { border-left: 4px solid #dc3545; }
        
        .score-value { font-size: 48px; font-weight: bold; margin-bottom: 10px; color: #667eea; }
        .score-label { font-size: 18px; margin-bottom: 10px; }
        .score-status { font-size: 14px; color: #666; }
        
        section { padding: 30px; border-bottom: 1px solid #eee; }
        section:last-child { border-bottom: none; }
        h2 { font-size: 24px; margin-bottom: 20px; color: #333; }
        h3 { font-size: 18px; margin-bottom: 15px; }
        
        .findings-summary { background-color: #f9f9f9; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        .summary-item { padding: 20px; border-radius: 8px; text-align: center; color: white; }
        .summary-item.critical { background-color: #dc3545; }
        .summary-item.high { background-color: #fd7e14; }
        .summary-item.medium { background-color: #ffc107; color: #333; }
        .summary-item.low { background-color: #17a2b8; }
        .summary-item .count { font-size: 32px; font-weight: bold; display: block; margin-bottom: 5px; }
        .summary-item .label { font-size: 12px; display: block; }
        
        .findings-list { margin-top: 20px; }
        .finding-card { padding: 20px; margin-bottom: 15px; border-left: 4px solid #ddd; background-color: #f9f9f9; border-radius: 4px; }
        .finding-card.critical { border-left-color: #dc3545; background-color: #fff5f5; }
        .finding-card.high { border-left-color: #fd7e14; background-color: #fff8f0; }
        .finding-card.medium { border-left-color: #ffc107; background-color: #fffbf0; }
        .finding-card.low { border-left-color: #17a2b8; background-color: #f0f8fb; }
        
        .finding-header { display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }
        .severity-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }
        .severity-badge.critical { background-color: #dc3545; }
        .severity-badge.high { background-color: #fd7e14; }
        .severity-badge.medium { background-color: #ffc107; color: #333; }
        .severity-badge.low { background-color: #17a2b8; }
        
        .finding-description { margin-bottom: 10px; line-height: 1.6; }
        .finding-remediation { padding-top: 10px; border-top: 1px solid #ddd; font-size: 14px; }
        
        .compliance-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .compliance-card { padding: 20px; border-radius: 8px; background-color: #f9f9f9; }
        .compliance-card.pass { border-left: 4px solid #28a745; }
        .compliance-card.review { border-left: 4px solid #ffc107; }
        .compliance-card.fail { border-left: 4px solid #dc3545; }
        
        .progress-bar { width: 100%; height: 8px; background-color: #ddd; border-radius: 4px; margin: 10px 0; overflow: hidden; }
        .progress-fill { height: 100%; background-color: #28a745; }
        
        .executive-section { padding: 40px; }
        .executive-section h2 { font-size: 28px; margin-bottom: 20px; color: #667eea; }
        .executive-section p { line-height: 1.8; margin-bottom: 15px; }
        .executive-section ul, .executive-section ol { margin-left: 30px; line-height: 2; }
        
        footer.footer { background-color: #f9f9f9; padding: 30px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #ddd; }
        """
    
    def _get_email_css(self) -> str:
        """Get email-specific CSS."""
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        a { color: #667eea; text-decoration: none; }
        """
    
    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "poor"
        else:
            return "critical"
    
    def _get_score_status(self, score: float) -> str:
        """Get human-readable score status."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def _get_score_bg_color(self, score: float) -> str:
        """Get background color for score."""
        if score >= 80:
            return "#28a745"
        elif score >= 60:
            return "#17a2b8"
        elif score >= 40:
            return "#ffc107"
        elif score >= 20:
            return "#fd7e14"
        else:
            return "#dc3545"
    
    def _get_executive_assessment(self, score: float) -> str:
        """Get executive assessment text."""
        if score >= 80:
            return "The infrastructure demonstrates strong security practices with well-implemented controls. Continue maintaining current security posture and address any medium/low findings."
        elif score >= 60:
            return "The infrastructure has a reasonable security foundation but requires attention to address gaps. Prioritize high-risk findings for remediation."
        elif score >= 40:
            return "The infrastructure has significant security gaps that need urgent attention. Implement the recommended security controls immediately."
        else:
            return "The infrastructure has critical security issues that require immediate remediation. Consider disabling affected resources until issues are resolved."
