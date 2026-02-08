#!/usr/bin/env python3
"""
Compliance Framework Mapper

Maps security findings to compliance frameworks (CIS, PCI-DSS, HIPAA, SOC2, ISO27001, NIST).
Provides compliance coverage analysis and gap assessment.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


class ComplianceMapper:
    """Map security findings to compliance frameworks"""
    
    def __init__(self):
        """Initialize compliance mapper with framework definitions"""
        self.frameworks = self._load_frameworks()
        self.finding_mappings = {}  # Cache for finding -> framework mappings
    
    def _load_frameworks(self) -> Dict[str, Any]:
        """Load compliance frameworks from template file"""
        template_path = Path(__file__).parent / 'templates' / 'compliance_frameworks.json'
        
        if not template_path.exists():
            console.print(f"[yellow]Warning: Compliance frameworks file not found at {template_path}[/yellow]")
            return {}
        
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading frameworks: {e}[/red]")
            return {}
    
    def map_finding_to_frameworks(
        self,
        finding: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Map a finding to relevant compliance frameworks.
        
        Args:
            finding: Finding dictionary with title and description
            
        Returns:
            Dictionary mapping framework names to matching controls
        """
        finding_text = (
            f"{finding.get('title', '')} {finding.get('description', '')}"
        ).lower()
        
        mappings = {}
        
        for framework_key, framework_data in self.frameworks.items():
            matched_controls = []
            
            for control_key, control_data in framework_data.get('controls', {}).items():
                # Check if control keywords match finding
                keywords = control_data.get('keywords', [])
                
                for keyword in keywords:
                    if keyword.lower() in finding_text:
                        matched_controls.append(
                            f"{control_data.get('id', '')}: {control_data.get('title', '')}"
                        )
                        break
            
            if matched_controls:
                framework_name = framework_data.get('name', framework_key)
                mappings[framework_name] = matched_controls
        
        return mappings
    
    def calculate_framework_coverage(
        self,
        findings: List[Dict[str, Any]],
        framework_name: str
    ) -> float:
        """
        Calculate compliance coverage percentage for a framework.
        
        Args:
            findings: List of findings
            framework_name: Name of framework to assess
            
        Returns:
            Coverage percentage (0-100)
        """
        if not findings:
            return 0.0
        
        # Find framework key
        framework_key = None
        for key, data in self.frameworks.items():
            if data.get('name') == framework_name:
                framework_key = key
                break
        
        if not framework_key:
            return 0.0
        
        framework_data = self.frameworks[framework_key]
        total_controls = len(framework_data.get('controls', {}))
        
        if total_controls == 0:
            return 0.0
        
        covered_controls = set()
        
        for finding in findings:
            mappings = self.map_finding_to_frameworks(finding)
            
            if framework_name in mappings:
                # Each mapping represents a covered control
                covered_controls.update(mappings[framework_name])
        
        # Calculate coverage as percentage of controls with findings
        coverage = (len(covered_controls) / total_controls) * 100
        return min(100.0, coverage)  # Cap at 100%
    
    def get_framework_gap_analysis(
        self,
        findings: List[Dict[str, Any]],
        framework_name: str
    ) -> Dict[str, Any]:
        """
        Perform gap analysis for a framework.
        
        Args:
            findings: List of findings
            framework_name: Name of framework
            
        Returns:
            Gap analysis with covered and missing controls
        """
        # Find framework key
        framework_key = None
        for key, data in self.frameworks.items():
            if data.get('name') == framework_name:
                framework_key = key
                break
        
        if not framework_key:
            return {'error': f'Framework {framework_name} not found'}
        
        framework_data = self.frameworks[framework_key]
        all_controls = framework_data.get('controls', {})
        
        # Find covered controls
        covered_control_ids = set()
        covered_control_details = {}
        
        for finding in findings:
            mappings = self.map_finding_to_frameworks(finding)
            
            if framework_name in mappings:
                for control_str in mappings[framework_name]:
                    # Extract control ID
                    control_id = control_str.split(':')[0].strip()
                    covered_control_ids.add(control_id)
                    
                    if control_id not in covered_control_details:
                        covered_control_details[control_id] = {
                            'control_str': control_str,
                            'finding_count': 0
                        }
                    
                    covered_control_details[control_id]['finding_count'] += 1
        
        # Find missing controls
        missing_controls = []
        
        for control_key, control_data in all_controls.items():
            control_id = control_data.get('id')
            
            if control_id not in covered_control_ids:
                missing_controls.append({
                    'id': control_id,
                    'title': control_data.get('title'),
                    'description': control_data.get('description')
                })
        
        coverage = self.calculate_framework_coverage(findings, framework_name)
        
        return {
            'framework': framework_name,
            'coverage_percentage': coverage,
            'total_controls': len(all_controls),
            'covered_controls': len(covered_control_ids),
            'missing_controls': len(missing_controls),
            'covered_details': covered_control_details,
            'missing_details': missing_controls
        }
    
    def get_all_framework_coverage(
        self,
        findings: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Get coverage for all frameworks.
        
        Args:
            findings: List of findings
            
        Returns:
            Dictionary mapping framework names to coverage percentages
        """
        coverage = {}
        
        for framework_key, framework_data in self.frameworks.items():
            framework_name = framework_data.get('name')
            coverage[framework_name] = self.calculate_framework_coverage(findings, framework_name)
        
        return coverage
    
    def get_compliance_status_table(
        self,
        findings: List[Dict[str, Any]]
    ) -> Table:
        """
        Generate a Rich table showing compliance status.
        
        Args:
            findings: List of findings
            
        Returns:
            Rich Table object
        """
        table = Table(title="Compliance Framework Coverage", box="rounded")
        
        table.add_column("Framework", style="cyan")
        table.add_column("Coverage", style="magenta")
        table.add_column("Status", style="green")
        
        coverage = self.get_all_framework_coverage(findings)
        
        for framework_name, percentage in sorted(coverage.items(), key=lambda x: x[1], reverse=True):
            # Determine status
            if percentage >= 80:
                status = "✓ PASS"
                status_color = "green"
            elif percentage >= 60:
                status = "⚠ REVIEW"
                status_color = "yellow"
            else:
                status = "✗ FAIL"
                status_color = "red"
            
            # Create progress bar
            bar_length = 20
            filled = int(bar_length * percentage / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            table.add_row(
                framework_name,
                f"{bar} {percentage:.1f}%",
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        return table
    
    def get_remediation_priority_by_compliance(
        self,
        findings: List[Dict[str, Any]],
        frameworks: Optional[List[str]] = None
    ) -> List[Tuple[Dict, List[str]]]:
        """
        Get findings prioritized by compliance impact.
        
        Args:
            findings: List of findings
            frameworks: List of frameworks to consider (None = all)
            
        Returns:
            List of tuples (finding, [matching_frameworks])
        """
        if frameworks is None:
            frameworks = [data.get('name') for data in self.frameworks.values()]
        
        finding_framework_map = []
        
        for finding in findings:
            mappings = self.map_finding_to_frameworks(finding)
            
            # Filter to requested frameworks
            relevant_frameworks = [
                fw for fw in mappings.keys()
                if fw in frameworks
            ]
            
            if relevant_frameworks:
                # Score by severity and compliance impact
                severity = finding.get('severity', 'low').lower()
                
                severity_weight = {
                    'critical': 4,
                    'high': 3,
                    'medium': 2,
                    'low': 1
                }
                
                score = (
                    severity_weight.get(severity, 0) * 100 +
                    len(relevant_frameworks)  # More frameworks = higher priority
                )
                
                finding_framework_map.append((finding, relevant_frameworks, score))
        
        # Sort by score (highest first)
        finding_framework_map.sort(key=lambda x: x[2], reverse=True)
        
        return [(item[0], item[1]) for item in finding_framework_map]
    
    def display_framework_details(
        self,
        findings: List[Dict[str, Any]],
        framework_name: str
    ) -> None:
        """
        Display detailed framework gap analysis.
        
        Args:
            findings: List of findings
            framework_name: Name of framework
        """
        gap_analysis = self.get_framework_gap_analysis(findings, framework_name)
        
        if 'error' in gap_analysis:
            console.print(f"[red]{gap_analysis['error']}[/red]")
            return
        
        # Header
        console.print(f"\n[bold blue]{framework_name} Gap Analysis[/bold blue]")
        console.print(f"Coverage: {gap_analysis['coverage_percentage']:.1f}%")
        console.print(f"Covered: {gap_analysis['covered_controls']}/{gap_analysis['total_controls']} controls\n")
        
        # Covered controls
        if gap_analysis['covered_details']:
            console.print("[green]✓ Covered Controls:[/green]")
            for control_id, details in gap_analysis['covered_details'].items():
                console.print(f"  {details['control_str']} ({details['finding_count']} findings)")
        
        # Missing controls
        if gap_analysis['missing_details']:
            console.print("\n[red]✗ Missing Controls:[/red]")
            for control in gap_analysis['missing_details'][:5]:  # Show top 5
                console.print(f"  {control['id']}: {control['title']}")
            
            if len(gap_analysis['missing_details']) > 5:
                console.print(f"  ... and {len(gap_analysis['missing_details']) - 5} more")
