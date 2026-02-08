#!/usr/bin/env python3
"""
Email Service Module

Handles email delivery of audit reports with SMTP configuration,
attachment support, and scheduling.
"""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending audit reports via email."""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None
    ):
        """
        Initialize the email service.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (default: 587)
            sender_email: Sender email address
            sender_password: Sender password or API key
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD")
        self.logger = logging.getLogger(__name__)
        
        if not self.sender_email or not self.sender_password:
            self.logger.warning(
                "Email credentials not configured. Set SENDER_EMAIL and SENDER_PASSWORD "
                "environment variables to enable email delivery."
            )
    
    def send_report(
        self,
        recipient_emails: List[str],
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send audit report via email.
        
        Args:
            recipient_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of email body
            attachments: Optional list of file paths to attach
            cc: Optional list of CC email addresses
            bcc: Optional list of BCC email addresses
            reply_to: Optional reply-to email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            self.logger.error("Email service not configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipient_emails)
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if reply_to:
                message["Reply-To"] = reply_to
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    self._attach_file(message, attachment_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                all_recipients = recipient_emails.copy()
                if cc:
                    all_recipients.extend(cc)
                if bcc:
                    all_recipients.extend(bcc)
                
                server.sendmail(self.sender_email, all_recipients, message.as_string())
            
            self.logger.info(f"Report sent successfully to {len(recipient_emails)} recipient(s)")
            return True
            
        except smtplib.SMTPException as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}")
            return False
    
    def send_report_with_attachment(
        self,
        recipient_emails: List[str],
        subject: str,
        html_content: str,
        report_file_path: str,
        report_format: str = "pdf"
    ) -> bool:
        """
        Send report with file attachment.
        
        Args:
            recipient_emails: List of recipients
            subject: Email subject
            html_content: Email body HTML
            report_file_path: Path to report file
            report_format: Format of report (pdf, html, json, csv)
            
        Returns:
            True if successful
        """
        if not Path(report_file_path).exists():
            self.logger.error(f"Report file not found: {report_file_path}")
            return False
        
        return self.send_report(
            recipient_emails,
            subject,
            html_content,
            attachments=[report_file_path]
        )
    
    def send_scheduled_report(
        self,
        recipient_emails: List[str],
        report_data: Dict[str, Any],
        html_template: str,
        schedule_time: Optional[datetime] = None,
        recipient_name: Optional[str] = None
    ) -> bool:
        """
        Send report with optional scheduling.
        
        Args:
            recipient_emails: List of recipients
            report_data: Report data dictionary
            html_template: HTML template string
            schedule_time: When to send (None = immediately)
            recipient_name: Name for personalization
            
        Returns:
            True if scheduled/sent successfully
        """
        account_name = report_data.get('account_name', 'Cloud Account')
        score = report_data.get('security_score', 0)
        
        # Format subject
        subject = f"Security Audit Report - {account_name} (Score: {score}/100)"
        
        # Prepare HTML content
        html_content = self._format_email_content(
            html_template,
            report_data,
            recipient_name
        )
        
        if schedule_time and schedule_time > datetime.now():
            # TODO: Implement proper scheduling with background job queue
            delay_seconds = (schedule_time - datetime.now()).total_seconds()
            self.logger.info(
                f"Report scheduled for delivery in {delay_seconds} seconds"
            )
            # For now, send immediately
            return self.send_report(recipient_emails, subject, html_content)
        else:
            # Send immediately
            return self.send_report(recipient_emails, subject, html_content)
    
    def send_critical_alert(
        self,
        recipient_emails: List[str],
        finding_data: Dict[str, Any],
        escalation_level: str = "HIGH"
    ) -> bool:
        """
        Send critical finding alert email.
        
        Args:
            recipient_emails: Alert recipients
            finding_data: Critical finding details
            escalation_level: Escalation level (HIGH, CRITICAL, EMERGENCY)
            
        Returns:
            True if email sent
        """
        subject = f"🚨 CRITICAL SECURITY ALERT - {finding_data.get('title', 'Unknown')}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 40px;">
                <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 4px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 CRITICAL SECURITY ALERT</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">Escalation Level: {escalation_level}</p>
                </div>
                
                <h2>Finding Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px; font-weight: bold;">Title</td>
                        <td style="padding: 10px;">{finding_data.get('title', 'N/A')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px; font-weight: bold;">Resource</td>
                        <td style="padding: 10px;">{finding_data.get('resource', 'N/A')}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px; font-weight: bold;">Description</td>
                        <td style="padding: 10px;">{finding_data.get('description', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Remediation</td>
                        <td style="padding: 10px;">{finding_data.get('remediation', 'N/A')}</td>
                    </tr>
                </table>
                
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-top: 20px;">
                    <strong>Action Required:</strong> Please address this critical issue immediately.
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_report(recipient_emails, subject, html_content)
    
    def _attach_file(self, message: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message."""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = Path(file_path).name
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}"
            )
            message.attach(part)
            
        except IOError as e:
            self.logger.error(f"Failed to attach file {file_path}: {e}")
    
    def _format_email_content(
        self,
        template: str,
        report_data: Dict[str, Any],
        recipient_name: Optional[str]
    ) -> str:
        """Format email content from template and report data."""
        content = template
        
        # Replace placeholders
        content = content.replace("{ACCOUNT_NAME}", report_data.get('account_name', 'N/A'))
        content = content.replace("{SCORE}", str(report_data.get('security_score', 0)))
        content = content.replace("{DATE}", datetime.now().strftime('%Y-%m-%d'))
        content = content.replace("{RECIPIENT_NAME}", recipient_name or "User")
        
        return content
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SMTP connection and return configuration status."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            self.logger.info("SMTP connection successful")
            return {
                "configured": True,
                "smtp_server": self.smtp_server,
                "sender_email": self.sender_email,
                "status": "Connected"
            }
        except Exception as e:
            self.logger.error(f"SMTP connection failed: {e}")
            return {
                "configured": False,
                "smtp_server": self.smtp_server,
                "sender_email": self.sender_email,
                "status": f"Failed: {str(e)}"
            }


class EmailScheduler:
    """Scheduler for automated report email delivery."""
    
    def __init__(self, email_service: EmailService):
        """
        Initialize the email scheduler.
        
        Args:
            email_service: EmailService instance
        """
        self.email_service = email_service
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def schedule_daily_report(
        self,
        schedule_id: str,
        recipient_emails: List[str],
        report_generator_func,
        hour: int = 9,
        minute: int = 0
    ) -> bool:
        """
        Schedule daily report delivery.
        
        Args:
            schedule_id: Unique schedule identifier
            recipient_emails: Email recipients
            report_generator_func: Function that generates report
            hour: Hour of day to send (0-23)
            minute: Minute of hour to send (0-59)
            
        Returns:
            True if scheduled successfully
        """
        self.schedules[schedule_id] = {
            "type": "daily",
            "recipients": recipient_emails,
            "generator": report_generator_func,
            "hour": hour,
            "minute": minute,
            "enabled": True
        }
        
        self.logger.info(
            f"Daily report scheduled: {schedule_id} at {hour:02d}:{minute:02d}"
        )
        return True
    
    def schedule_weekly_report(
        self,
        schedule_id: str,
        recipient_emails: List[str],
        report_generator_func,
        day_of_week: int = 0,
        hour: int = 9,
        minute: int = 0
    ) -> bool:
        """
        Schedule weekly report delivery.
        
        Args:
            schedule_id: Unique schedule identifier
            recipient_emails: Email recipients
            report_generator_func: Function that generates report
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day to send
            minute: Minute of hour to send
            
        Returns:
            True if scheduled successfully
        """
        self.schedules[schedule_id] = {
            "type": "weekly",
            "recipients": recipient_emails,
            "generator": report_generator_func,
            "day_of_week": day_of_week,
            "hour": hour,
            "minute": minute,
            "enabled": True
        }
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.logger.info(
            f"Weekly report scheduled: {schedule_id} on {days[day_of_week]} at {hour:02d}:{minute:02d}"
        )
        return True
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id]["enabled"] = False
            self.logger.info(f"Schedule disabled: {schedule_id}")
            return True
        return False
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """List all configured schedules."""
        return list(self.schedules.values())
