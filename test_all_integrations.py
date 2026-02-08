#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Multi-Format Export & Remediation

Tests:
1. Module imports and availability
2. Exporter functionality (JSON, CSV, HTML)
3. Email service configuration
4. Playbook library and execution
5. CLI integration (if available)
6. Agent integration (if available)
7. End-to-end workflows

Run with: python test_all_integrations.py
"""

import sys
import os
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class IntegrationTester:
    """Main test runner for all integrations."""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warning_tests = 0
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self, text: str):
        """Print formatted header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")
    
    def print_section(self, text: str):
        """Print formatted section."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}")
        print(f"{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}\n")
    
    def log_result(self, test_name: str, status: str, message: str = "", details: str = ""):
        """Log test result."""
        self.total_tests += 1
        
        if status == "PASS":
            self.passed_tests += 1
            icon = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            self.failed_tests += 1
            icon = "❌"
            color = Colors.RED
        elif status == "WARN":
            self.warning_tests += 1
            icon = "⚠️ "
            color = Colors.YELLOW
        else:
            icon = "❓"
            color = Colors.WHITE
        
        print(f"{icon} {color}{test_name}{Colors.END}")
        if message:
            print(f"   {Colors.BOLD}Info:{Colors.END} {message}")
        if details:
            print(f"   {Colors.BOLD}Details:{Colors.END} {details}")
        
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "details": details
        })
    
    # ============================================================================
    # PHASE 1: MODULE IMPORTS
    # ============================================================================
    
    def test_module_imports(self):
        """Test that all modules can be imported."""
        self.print_section("PHASE 1: Module Imports & Availability")
        
        # Test exporter imports
        try:
            from src.audit.exporters import JSONExporter
            self.log_result("Import JSONExporter", "PASS", "JSONExporter available")
        except ImportError as e:
            self.log_result("Import JSONExporter", "FAIL", str(e))
        
        try:
            from src.audit.exporters import CSVExporter
            self.log_result("Import CSVExporter", "PASS", "CSVExporter available")
        except ImportError as e:
            self.log_result("Import CSVExporter", "FAIL", str(e))
        
        try:
            from src.audit.exporters import HTMLExporter
            self.log_result("Import HTMLExporter", "PASS", "HTMLExporter available")
        except ImportError as e:
            self.log_result("Import HTMLExporter", "FAIL", str(e))
        
        try:
            from src.audit.exporters import EmailService
            self.log_result("Import EmailService", "PASS", "EmailService available")
        except ImportError as e:
            self.log_result("Import EmailService", "FAIL", str(e))
        
        try:
            from src.audit.exporters import EmailScheduler
            self.log_result("Import EmailScheduler", "PASS", "EmailScheduler available")
        except ImportError as e:
            self.log_result("Import EmailScheduler", "FAIL", str(e))
        
        # Test remediation imports
        try:
            from src.remediation import RemediationPlaybook
            self.log_result("Import RemediationPlaybook", "PASS", "RemediationPlaybook available")
        except ImportError as e:
            self.log_result("Import RemediationPlaybook", "FAIL", str(e))
        
        try:
            from src.remediation import PlaybookExecutor
            self.log_result("Import PlaybookExecutor", "PASS", "PlaybookExecutor available")
        except ImportError as e:
            self.log_result("Import PlaybookExecutor", "FAIL", str(e))
        
        try:
            from src.remediation import PlaybookLibrary
            self.log_result("Import PlaybookLibrary", "PASS", "PlaybookLibrary available")
        except ImportError as e:
            self.log_result("Import PlaybookLibrary", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 2: MODULE EXPORTS
    # ============================================================================
    
    def test_module_exports(self):
        """Test that modules are properly exported."""
        self.print_section("PHASE 2: Module Exports from __init__.py")
        
        # Check src/audit/__init__.py
        audit_init_path = Path("src/audit/__init__.py")
        if audit_init_path.exists():
            content = audit_init_path.read_text()
            required_exports = ["JSONExporter", "CSVExporter", "HTMLExporter", "EmailService"]
            missing = [e for e in required_exports if e not in content]
            
            if not missing:
                self.log_result("src/audit/__init__.py exports", "PASS", 
                              "All exporters exported")
            else:
                self.log_result("src/audit/__init__.py exports", "WARN",
                              f"Missing exports: {', '.join(missing)}")
        else:
            self.log_result("src/audit/__init__.py exists", "FAIL",
                          "File not found")
        
        # Check src/remediation/__init__.py
        remediation_init_path = Path("src/remediation/__init__.py")
        if remediation_init_path.exists():
            content = remediation_init_path.read_text()
            required_exports = ["RemediationPlaybook", "PlaybookExecutor", "PlaybookLibrary"]
            missing = [e for e in required_exports if e not in content]
            
            if not missing:
                self.log_result("src/remediation/__init__.py exports", "PASS",
                              "All remediation classes exported")
            else:
                self.log_result("src/remediation/__init__.py exports", "WARN",
                              f"Missing exports: {', '.join(missing)}")
        else:
            self.log_result("src/remediation/__init__.py exists", "FAIL",
                          "File not found")
    
    # ============================================================================
    # PHASE 3: EXPORTER FUNCTIONALITY
    # ============================================================================
    
    def test_exporters(self):
        """Test exporter functionality."""
        self.print_section("PHASE 3: Exporter Functionality Tests")
        
        # Create test data
        test_report = {
            "account_id": "123456789012",
            "timestamp": datetime.now().isoformat(),
            "findings": [
                {
                    "id": "FIND-001",
                    "title": "Public S3 Bucket",
                    "severity": "CRITICAL",
                    "category": "Storage",
                    "resource": "test-bucket",
                    "description": "S3 bucket is publicly accessible",
                    "remediation": "Block public access"
                },
                {
                    "id": "FIND-002",
                    "title": "Unencrypted EBS",
                    "severity": "HIGH",
                    "category": "Compute",
                    "resource": "vol-123456",
                    "description": "EBS volume is not encrypted",
                    "remediation": "Enable encryption"
                }
            ],
            "metadata": {
                "provider": "aws",
                "scan_date": datetime.now().isoformat(),
                "total_findings": 2
            }
        }
        
        # Test JSONExporter
        try:
            from src.audit.exporters import JSONExporter
            exporter = JSONExporter()
            json_output = exporter.export_report(test_report, None)
            parsed = json.loads(json_output)
            
            if "metadata" in parsed and "findings" in parsed:
                self.log_result("JSONExporter.export_report()", "PASS",
                              "JSON export successful")
            else:
                self.log_result("JSONExporter.export_report()", "FAIL",
                              "Missing expected keys in JSON output")
        except Exception as e:
            self.log_result("JSONExporter.export_report()", "FAIL", str(e))
        
        # Test CSVExporter
        try:
            from src.audit.exporters import CSVExporter
            exporter = CSVExporter()
            csv_output = exporter.export_findings_to_csv(test_report["findings"], None)
            
            # Parse CSV to verify
            lines = csv_output.strip().split('\n')
            if len(lines) > 2:  # Header + 2 data rows
                self.log_result("CSVExporter.export_findings_to_csv()", "PASS",
                              f"CSV export successful ({len(lines)} rows)")
            else:
                self.log_result("CSVExporter.export_findings_to_csv()", "FAIL",
                              "CSV output incomplete")
        except Exception as e:
            self.log_result("CSVExporter.export_findings_to_csv()", "FAIL", str(e))
        
        # Test HTMLExporter
        try:
            from src.audit.exporters import HTMLExporter
            exporter = HTMLExporter()
            html_output = exporter.export_report_to_html(test_report, None)
            
            if "<html" in html_output.lower() and "findings" in html_output.lower():
                self.log_result("HTMLExporter.export_report_to_html()", "PASS",
                              "HTML export successful")
            else:
                self.log_result("HTMLExporter.export_report_to_html()", "FAIL",
                              "HTML output malformed")
        except Exception as e:
            self.log_result("HTMLExporter.export_report_to_html()", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 4: EMAIL SERVICE
    # ============================================================================
    
    def test_email_service(self):
        """Test email service configuration."""
        self.print_section("PHASE 4: Email Service Configuration")
        
        try:
            from src.audit.exporters import EmailService
            
            # Test instantiation
            email = EmailService()
            self.log_result("EmailService instantiation", "PASS",
                          "EmailService created successfully")
            
            # Check SMTP configuration
            smtp_configured = (
                os.getenv("SMTP_SERVER") and
                os.getenv("SENDER_EMAIL") and
                os.getenv("SENDER_PASSWORD")
            )
            
            if smtp_configured:
                self.log_result("EmailService SMTP config", "PASS",
                              "All SMTP variables configured")
            else:
                missing = []
                if not os.getenv("SMTP_SERVER"): missing.append("SMTP_SERVER")
                if not os.getenv("SENDER_EMAIL"): missing.append("SENDER_EMAIL")
                if not os.getenv("SENDER_PASSWORD"): missing.append("SENDER_PASSWORD")
                
                self.log_result("EmailService SMTP config", "WARN",
                              f"Missing config: {', '.join(missing)}",
                              "Set environment variables to enable email delivery")
            
            # Test EmailScheduler
            from src.audit.exporters import EmailScheduler
            scheduler = EmailScheduler(email)
            self.log_result("EmailScheduler instantiation", "PASS",
                          "EmailScheduler created successfully")
            
        except Exception as e:
            self.log_result("EmailService tests", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 5: PLAYBOOK LIBRARY
    # ============================================================================
    
    def test_playbook_library(self):
        """Test playbook library and functionality."""
        self.print_section("PHASE 5: Playbook Library & Functionality")
        
        try:
            from src.remediation import PlaybookLibrary
            
            # Get all playbooks
            playbooks = PlaybookLibrary.get_all_playbooks()
            
            if len(playbooks) > 0:
                self.log_result("PlaybookLibrary.get_all_playbooks()", "PASS",
                              f"Loaded {len(playbooks)} playbooks")
                
                # List playbooks
                print(f"   {Colors.BOLD}Available Playbooks:{Colors.END}")
                for name, playbook in sorted(playbooks.items()):
                    severity = playbook.severity if hasattr(playbook, 'severity') else 'N/A'
                    print(f"      • {name} ({severity})")
            else:
                self.log_result("PlaybookLibrary.get_all_playbooks()", "FAIL",
                              "No playbooks found")
            
            # Test playbook by category
            try:
                category_playbooks = PlaybookLibrary.get_playbook_by_category("Storage")
                if category_playbooks:
                    self.log_result("PlaybookLibrary.get_playbook_by_category()", "PASS",
                                  f"Found playbooks for 'Storage' category")
            except Exception as e:
                self.log_result("PlaybookLibrary.get_playbook_by_category()", "WARN",
                              f"Category filter not available: {str(e)}")
            
            # Test playbook by severity
            try:
                severity_playbooks = PlaybookLibrary.get_playbooks_by_severity("CRITICAL")
                if severity_playbooks:
                    self.log_result("PlaybookLibrary.get_playbooks_by_severity()", "PASS",
                                  f"Found {len(severity_playbooks)} CRITICAL playbooks")
            except Exception as e:
                self.log_result("PlaybookLibrary.get_playbooks_by_severity()", "WARN",
                              f"Severity filter not available: {str(e)}")
            
        except Exception as e:
            self.log_result("PlaybookLibrary tests", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 6: PLAYBOOK EXECUTION
    # ============================================================================
    
    def test_playbook_execution(self):
        """Test playbook execution engine."""
        self.print_section("PHASE 6: Playbook Execution Engine")
        
        try:
            from src.remediation import PlaybookExecutor, PlaybookLibrary
            
            # Instantiate executor
            executor = PlaybookExecutor()
            self.log_result("PlaybookExecutor instantiation", "PASS",
                          "PlaybookExecutor created successfully")
            
            # Get a playbook
            playbooks = PlaybookLibrary.get_all_playbooks()
            if playbooks:
                test_playbook = list(playbooks.values())[0]
                test_playbook_name = list(playbooks.keys())[0]
                
                # Create test finding
                test_finding = {
                    "id": "FIND-TEST",
                    "resource": "test-resource",
                    "title": "Test Finding",
                    "severity": "HIGH"
                }
                
                # Test dry-run execution
                try:
                    execution = executor.execute_playbook(
                        test_playbook,
                        test_finding,
                        initiated_by="test_user",
                        dry_run=True
                    )
                    
                    if execution and hasattr(execution, 'execution_id'):
                        self.log_result("PlaybookExecutor.execute_playbook() [dry-run]", "PASS",
                                      f"Execution {execution.execution_id} created in dry-run mode")
                    else:
                        self.log_result("PlaybookExecutor.execute_playbook() [dry-run]", "FAIL",
                                      "Execution object malformed")
                except Exception as e:
                    self.log_result("PlaybookExecutor.execute_playbook() [dry-run]", "FAIL",
                                  str(e))
                
                # Test playbook validation
                try:
                    is_valid = executor.validate_playbook(test_playbook)
                    if is_valid:
                        self.log_result("PlaybookExecutor.validate_playbook()", "PASS",
                                      "Playbook validation successful")
                    else:
                        self.log_result("PlaybookExecutor.validate_playbook()", "WARN",
                                      "Playbook validation returned False")
                except Exception as e:
                    self.log_result("PlaybookExecutor.validate_playbook()", "FAIL",
                                  str(e))
            else:
                self.log_result("PlaybookExecutor tests", "FAIL",
                              "No playbooks available for testing")
        
        except Exception as e:
            self.log_result("PlaybookExecutor tests", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 7: CLI INTEGRATION
    # ============================================================================
    
    def test_cli_integration(self):
        """Test CLI command availability."""
        self.print_section("PHASE 7: CLI Integration Status")
        
        cli_path = Path("main_cli.py")
        if not cli_path.exists():
            self.log_result("main_cli.py exists", "FAIL",
                          "main_cli.py not found at project root")
            return
        
        content = cli_path.read_text()
        
        # Check for export command
        if "@app.command" in content and "export" in content.lower():
            self.log_result("CLI export command", "PASS",
                          "export command found in CLI")
        else:
            self.log_result("CLI export command", "FAIL",
                          "export command not found in main_cli.py",
                          "Add: @app.command() def export(...)")
        
        # Check for remediate command
        if "@app.command" in content and "remediate" in content.lower():
            self.log_result("CLI remediate command", "PASS",
                          "remediate command found in CLI")
        else:
            self.log_result("CLI remediate command", "FAIL",
                          "remediate command not found in main_cli.py",
                          "Add: @app.command() def remediate(...)")
        
        # Check for playbook-list command
        if "@app.command" in content and "playbook" in content.lower():
            self.log_result("CLI playbook commands", "PASS",
                          "playbook commands found in CLI")
        else:
            self.log_result("CLI playbook commands", "FAIL",
                          "playbook commands not found in main_cli.py",
                          "Add: @app.command() def playbook_list(...)")
    
    # ============================================================================
    # PHASE 8: AGENT INTEGRATION
    # ============================================================================
    
    def test_agent_integration(self):
        """Test agent integration."""
        self.print_section("PHASE 8: Agent Integration Status")
        
        agents = [
            ("src/agents/aws_security/agent.py", "AWS"),
            ("src/agents/gcp_security/agent.py", "GCP"),
            ("src/agents/azure_security/agent.py", "Azure")
        ]
        
        for agent_path, provider in agents:
            path = Path(agent_path)
            if not path.exists():
                self.log_result(f"{provider} Agent exists", "WARN",
                              f"{agent_path} not found")
                continue
            
            content = path.read_text()
            
            # Check for exporter usage
            has_exporter = "JSONExporter" in content or "CSVExporter" in content or "HTMLExporter" in content
            
            # Check for remediation usage
            has_remediation = "PlaybookExecutor" in content or "PlaybookLibrary" in content
            
            if has_exporter and has_remediation:
                self.log_result(f"{provider} Agent integration", "PASS",
                              "Both exporters and remediation integrated")
            elif has_exporter or has_remediation:
                status = "exporters" if has_exporter else "remediation"
                self.log_result(f"{provider} Agent integration", "WARN",
                              f"Only {status} integrated",
                              f"Add: from src.audit.exporters import JSONExporter")
            else:
                self.log_result(f"{provider} Agent integration", "FAIL",
                              "Not integrated with export/remediation",
                              f"Update {agent_path} to use new modules")
    
    # ============================================================================
    # PHASE 9: END-TO-END WORKFLOW
    # ============================================================================
    
    def test_end_to_end(self):
        """Test complete workflow."""
        self.print_section("PHASE 9: End-to-End Workflow Test")
        
        try:
            from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
            from src.remediation import PlaybookExecutor, PlaybookLibrary
            
            # Create sample report
            sample_report = {
                "account_id": "test-123",
                "findings": [
                    {
                        "id": "E2E-TEST-001",
                        "title": "Test Finding",
                        "severity": "CRITICAL",
                        "category": "Storage",
                        "resource": "e2e-test-bucket",
                        "description": "End-to-end test finding"
                    }
                ],
                "metadata": {
                    "provider": "aws",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Step 1: Export to JSON
            try:
                json_exp = JSONExporter()
                json_output = json_exp.export_report(sample_report, None)
                if json_output and len(json_output) > 0:
                    self.log_result("E2E: Export to JSON", "PASS",
                                  f"Generated {len(json_output)} bytes")
                else:
                    self.log_result("E2E: Export to JSON", "FAIL",
                                  "Empty JSON output")
            except Exception as e:
                self.log_result("E2E: Export to JSON", "FAIL", str(e))
            
            # Step 2: Export to CSV
            try:
                csv_exp = CSVExporter()
                csv_output = csv_exp.export_findings_to_csv(sample_report["findings"], None)
                if csv_output and len(csv_output) > 0:
                    self.log_result("E2E: Export to CSV", "PASS",
                                  f"Generated {len(csv_output)} bytes")
                else:
                    self.log_result("E2E: Export to CSV", "FAIL",
                                  "Empty CSV output")
            except Exception as e:
                self.log_result("E2E: Export to CSV", "FAIL", str(e))
            
            # Step 3: Export to HTML
            try:
                html_exp = HTMLExporter()
                html_output = html_exp.export_report_to_html(sample_report, None)
                if html_output and len(html_output) > 0:
                    self.log_result("E2E: Export to HTML", "PASS",
                                  f"Generated {len(html_output)} bytes")
                else:
                    self.log_result("E2E: Export to HTML", "FAIL",
                                  "Empty HTML output")
            except Exception as e:
                self.log_result("E2E: Export to HTML", "FAIL", str(e))
            
            # Step 4: Get remediation playbook
            try:
                playbooks = PlaybookLibrary.get_all_playbooks()
                if playbooks:
                    self.log_result("E2E: Load playbooks", "PASS",
                                  f"Loaded {len(playbooks)} playbooks")
                else:
                    self.log_result("E2E: Load playbooks", "FAIL",
                                  "No playbooks available")
            except Exception as e:
                self.log_result("E2E: Load playbooks", "FAIL", str(e))
            
            # Step 5: Execute playbook (dry-run)
            try:
                executor = PlaybookExecutor()
                playbooks = PlaybookLibrary.get_all_playbooks()
                if playbooks:
                    test_playbook = list(playbooks.values())[0]
                    execution = executor.execute_playbook(
                        test_playbook,
                        sample_report["findings"][0],
                        "e2e_test",
                        dry_run=True
                    )
                    
                    if execution:
                        self.log_result("E2E: Execute playbook (dry-run)", "PASS",
                                      f"Execution {execution.execution_id} created")
                    else:
                        self.log_result("E2E: Execute playbook (dry-run)", "FAIL",
                                      "Execution returned None")
            except Exception as e:
                self.log_result("E2E: Execute playbook (dry-run)", "FAIL", str(e))
        
        except ImportError as e:
            self.log_result("E2E: Module imports", "FAIL", str(e))
    
    # ============================================================================
    # PHASE 10: DOCUMENTATION CHECK
    # ============================================================================
    
    def test_documentation(self):
        """Check documentation availability."""
        self.print_section("PHASE 10: Documentation Verification")
        
        docs = {
            "INTEGRATION_GUIDE.md": "Integration patterns and code examples",
            "EXPORT_REMEDIATION_GUIDE.md": "Complete API reference",
            "QUICK_START_EXPORT_REMEDIATION.md": "5-minute quick start",
            "INTEGRATION_STATUS.md": "Detailed status report",
            "INTEGRATION_CHECKLIST.md": "Step-by-step integration tasks"
        }
        
        for doc_name, description in docs.items():
            path = Path(doc_name)
            if path.exists():
                size = path.stat().st_size
                self.log_result(f"Documentation: {doc_name}", "PASS",
                              f"{size} bytes - {description}")
            else:
                self.log_result(f"Documentation: {doc_name}", "WARN",
                              f"Not found - {description}")
    
    # ============================================================================
    # SUMMARY REPORT
    # ============================================================================
    
    def print_summary(self):
        """Print summary report."""
        self.print_header("INTEGRATION TEST SUMMARY")
        
        # Calculate percentages
        pass_pct = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        fail_pct = (self.failed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        warn_pct = (self.warning_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Overall status
        if self.failed_tests == 0 and self.warning_tests == 0:
            overall = f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED{Colors.END}"
        elif self.failed_tests == 0:
            overall = f"{Colors.YELLOW}{Colors.BOLD}⚠️ TESTS PASSED WITH WARNINGS{Colors.END}"
        else:
            overall = f"{Colors.RED}{Colors.BOLD}❌ TESTS FAILED{Colors.END}"
        
        print(f"Overall Status: {overall}\n")
        
        # Statistics
        print(f"{Colors.BOLD}Test Results:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Passed:{Colors.END} {self.passed_tests}/{self.total_tests} ({pass_pct:.1f}%)")
        print(f"  {Colors.YELLOW}⚠️ Warnings:{Colors.END} {self.warning_tests}/{self.total_tests} ({warn_pct:.1f}%)")
        print(f"  {Colors.RED}❌ Failed:{Colors.END} {self.failed_tests}/{self.total_tests} ({fail_pct:.1f}%)")
        
        # Detailed breakdown by phase
        print(f"\n{Colors.BOLD}Breakdown by Phase:{Colors.END}")
        
        phases = {
            "Phase 1": "Module Imports & Availability",
            "Phase 2": "Module Exports",
            "Phase 3": "Exporter Functionality",
            "Phase 4": "Email Service",
            "Phase 5": "Playbook Library",
            "Phase 6": "Playbook Execution",
            "Phase 7": "CLI Integration",
            "Phase 8": "Agent Integration",
            "Phase 9": "End-to-End Workflow",
            "Phase 10": "Documentation"
        }
        
        for phase_name, description in phases.items():
            phase_tests = [r for r in self.results if phase_name in r["test"]]
            if phase_tests:
                phase_pass = sum(1 for t in phase_tests if t["status"] == "PASS")
                phase_fail = sum(1 for t in phase_tests if t["status"] == "FAIL")
                phase_warn = sum(1 for t in phase_tests if t["status"] == "WARN")
                
                status_icon = "✅" if phase_fail == 0 else "❌" if phase_pass == 0 else "⚠️"
                print(f"  {status_icon} {phase_name}: {description}")
                print(f"      {phase_pass}✅ {phase_fail}❌ {phase_warn}⚠️")
        
        # Failures and warnings
        failures = [r for r in self.results if r["status"] == "FAIL"]
        warnings = [r for r in self.results if r["status"] == "WARN"]
        
        if failures:
            print(f"\n{Colors.BOLD}{Colors.RED}Failed Tests:{Colors.END}")
            for result in failures:
                print(f"  ❌ {result['test']}")
                if result['message']:
                    print(f"      Message: {result['message']}")
                if result['details']:
                    print(f"      Action: {result['details']}")
        
        if warnings:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}Tests with Warnings:{Colors.END}")
            for result in warnings:
                print(f"  ⚠️ {result['test']}")
                if result['message']:
                    print(f"      Message: {result['message']}")
                if result['details']:
                    print(f"      Action: {result['details']}")
        
        # Recommendations
        if self.failed_tests > 0 or self.warning_tests > 0:
            print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
            if self.failed_tests > 0:
                print(f"  1. Fix {self.failed_tests} failing test(s)")
                print(f"  2. Review error messages for required actions")
            if self.warning_tests > 0:
                print(f"  3. Address {self.warning_tests} warning(s) for full integration")
            print(f"  4. Refer to INTEGRATION_CHECKLIST.md for step-by-step guidance")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All integrations are ready for use!{Colors.END}")
        
        # Save report
        self.save_report()
    
    def save_report(self):
        """Save test report to file."""
        report_path = Path(f"reports/integration_test_{self.timestamp}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": self.timestamp,
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "warnings": self.warning_tests,
                "pass_percentage": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
            },
            "results": self.results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{Colors.BOLD}Report saved to: {Colors.CYAN}{report_path}{Colors.END}")
    
    def run_all_tests(self):
        """Run all integration tests."""
        self.print_header("INTEGRATION TEST SUITE")
        print(f"{Colors.BOLD}Testing all module integrations...{Colors.END}\n")
        
        # Run all test phases
        self.test_module_imports()
        self.test_module_exports()
        self.test_exporters()
        self.test_email_service()
        self.test_playbook_library()
        self.test_playbook_execution()
        self.test_cli_integration()
        self.test_agent_integration()
        self.test_end_to_end()
        self.test_documentation()
        
        # Print summary
        self.print_summary()


def main():
    """Main entry point."""
    tester = IntegrationTester()
    tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
