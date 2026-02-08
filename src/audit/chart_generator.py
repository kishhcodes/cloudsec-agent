#!/usr/bin/env python3
"""
Chart Generator for Audit Reports

Generates visual charts and graphs for security audit reports using matplotlib.
Supports pie charts, bar charts, risk matrices, and gauge charts.
"""

import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle
import numpy as np
from PIL import Image

from rich.console import Console

console = Console()


class ChartGenerator:
    """Generate charts and visualizations for audit reports"""
    
    # Color schemes
    SEVERITY_COLORS = {
        'critical': '#d32f2f',     # Red
        'high': '#f57c00',         # Orange
        'medium': '#fbc02d',       # Yellow
        'low': '#0288d1',          # Blue
        'pass': '#388e3c',         # Green
        'compliant': '#388e3c'     # Green
    }
    
    CHART_COLORS = ['#d32f2f', '#f57c00', '#fbc02d', '#0288d1', '#388e3c']
    
    def __init__(self, dpi: int = 100, figsize: Tuple[int, int] = (10, 6)):
        """
        Initialize chart generator.
        
        Args:
            dpi: Dots per inch for resolution
            figsize: Figure size as (width, height) in inches
        """
        self.dpi = dpi
        self.figsize = figsize
    
    def severity_distribution_pie(self, findings: List[Dict[str, Any]]) -> bytes:
        """
        Generate pie chart of findings by severity.
        
        Args:
            findings: List of finding dictionaries with 'severity' key
            
        Returns:
            PNG image as bytes
        """
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'pass': 0
        }
        
        # Count findings by severity
        for finding in findings:
            severity = finding.get('severity', '').lower()
            if 'critical' in severity:
                severity_counts['critical'] += 1
            elif 'high' in severity:
                severity_counts['high'] += 1
            elif 'medium' in severity:
                severity_counts['medium'] += 1
            elif 'low' in severity:
                severity_counts['low'] += 1
            else:
                severity_counts['pass'] += 1
        
        # Remove zero counts
        data = {k: v for k, v in severity_counts.items() if v > 0}
        
        if not data:
            return self._empty_chart_placeholder("No findings to display")
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        colors = [self.SEVERITY_COLORS[severity] for severity in data.keys()]
        wedges, texts, autotexts = ax.pie(
            data.values(),
            labels=data.keys(),
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )
        
        # Improve text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('Finding Severity Distribution', fontsize=14, weight='bold', pad=20)
        
        return self._fig_to_bytes(fig)
    
    def findings_by_category_bar(self, sections: List[Dict[str, Any]]) -> bytes:
        """
        Generate bar chart of findings by category.
        
        Args:
            sections: List of audit sections with findings
            
        Returns:
            PNG image as bytes
        """
        categories = []
        counts = []
        
        for section in sections:
            title = section.get('title', 'Unknown')
            findings = section.get('content', {}).get('findings', [])
            count = len([f for f in findings if isinstance(f, dict)])
            
            if count > 0:
                categories.append(title)
                counts.append(count)
        
        if not categories:
            return self._empty_chart_placeholder("No categories with findings")
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        bars = ax.bar(
            range(len(categories)),
            counts,
            color=self.CHART_COLORS[:len(categories)],
            edgecolor='black',
            linewidth=1.5
        )
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=10,
                weight='bold'
            )
        
        ax.set_xlabel('Category', fontsize=11, weight='bold')
        ax.set_ylabel('Number of Findings', fontsize=11, weight='bold')
        ax.set_title('Findings by Category', fontsize=14, weight='bold', pad=20)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)
    
    def risk_matrix_scatter(self, findings: List[Dict[str, Any]]) -> bytes:
        """
        Generate risk matrix (impact vs. likelihood) scatter plot.
        
        Args:
            findings: List of findings with severity and other attributes
            
        Returns:
            PNG image as bytes
        """
        # Map severity to risk scores
        severity_scores = {
            'critical': (4, 4),      # High impact, high likelihood
            'high': (3, 3),          # Medium-high impact/likelihood
            'medium': (2, 2),        # Medium impact/likelihood
            'low': (1, 1),           # Low impact/likelihood
            'pass': (0, 0)           # No risk
        }
        
        impact_scores = []
        likelihood_scores = []
        colors_list = []
        sizes = []
        
        for finding in findings:
            severity = finding.get('severity', 'low').lower()
            
            # Skip pass/compliant findings
            if 'pass' in severity or 'compliant' in severity:
                continue
            
            # Get score and add some variance for visibility
            base_impact, base_likelihood = severity_scores.get(
                severity, (1, 1)
            )
            
            # Add small variance to avoid overlapping points
            impact = base_impact + np.random.normal(0, 0.15)
            likelihood = base_likelihood + np.random.normal(0, 0.15)
            
            impact_scores.append(max(0, min(5, impact)))
            likelihood_scores.append(max(0, min(5, likelihood)))
            colors_list.append(self.SEVERITY_COLORS.get(severity, '#999999'))
            sizes.append(200)
        
        if not impact_scores:
            return self._empty_chart_placeholder("No findings to plot")
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        scatter = ax.scatter(
            likelihood_scores,
            impact_scores,
            s=sizes,
            c=colors_list,
            alpha=0.6,
            edgecolors='black',
            linewidth=1
        )
        
        # Add quadrant lines
        ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.axvline(x=2.5, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Label quadrants
        ax.text(1.25, 4.25, 'Low Impact\nHigh Likelihood', ha='center', alpha=0.5, fontsize=9)
        ax.text(3.75, 4.25, 'High Impact\nHigh Likelihood', ha='center', alpha=0.5, fontsize=9)
        ax.text(1.25, 0.75, 'Low Impact\nLow Likelihood', ha='center', alpha=0.5, fontsize=9)
        ax.text(3.75, 0.75, 'High Impact\nLow Likelihood', ha='center', alpha=0.5, fontsize=9)
        
        ax.set_xlabel('Likelihood of Exploitation →', fontsize=11, weight='bold')
        ax.set_ylabel('Impact if Exploited →', fontsize=11, weight='bold')
        ax.set_title('Risk Matrix: Impact vs. Likelihood', fontsize=14, weight='bold', pad=20)
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        ax.grid(True, alpha=0.3, linestyle=':')
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)
    
    def compliance_coverage_gauge(
        self,
        framework_name: str,
        coverage_percentage: float
    ) -> bytes:
        """
        Generate gauge chart for compliance framework coverage.
        
        Args:
            framework_name: Name of compliance framework
            coverage_percentage: Coverage percentage (0-100)
            
        Returns:
            PNG image as bytes
        """
        fig, ax = plt.subplots(figsize=(8, 6), dpi=self.dpi)
        
        # Draw gauge background
        gauge_range = np.linspace(0, 180, 100)
        colors_gradient = ['#d32f2f', '#f57c00', '#fbc02d', '#0288d1', '#388e3c']
        
        for i in range(len(colors_gradient)-1):
            start_angle = i * 36
            end_angle = (i + 1) * 36
            wedges, _ = ax.pie(
                [1],
                colors=[colors_gradient[i]],
                radius=1,
                startangle=180-start_angle,
                counterclock=False,
                wedgeprops=dict(width=0.3, edgecolor='white')
            )
        
        # Draw needle
        angle = 180 - (coverage_percentage / 100) * 180
        angle_rad = np.radians(angle)
        needle_x = [0.7 * np.cos(angle_rad), 0]
        needle_y = [0.7 * np.sin(angle_rad), 0]
        ax.plot(needle_x, needle_y, 'k-', linewidth=3)
        
        # Draw center circle
        center_circle = Circle((0, 0), 0.15, color='white', ec='black', linewidth=2, zorder=10)
        ax.add_patch(center_circle)
        
        # Add percentage text
        ax.text(0, -0.5, f'{coverage_percentage:.1f}%', ha='center', fontsize=24, weight='bold')
        ax.text(0, -0.65, framework_name, ha='center', fontsize=12, weight='bold')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)
    
    def remediation_progress_bar(
        self,
        total_findings: int,
        resolved_findings: int
    ) -> bytes:
        """
        Generate horizontal progress bar for remediation status.
        
        Args:
            total_findings: Total number of findings
            resolved_findings: Number of resolved findings
            
        Returns:
            PNG image as bytes
        """
        if total_findings == 0:
            progress = 0
        else:
            progress = (resolved_findings / total_findings) * 100
        
        fig, ax = plt.subplots(figsize=(10, 3), dpi=self.dpi)
        
        # Background bar
        ax.barh(0, 100, color='#e0e0e0', height=0.5, edgecolor='black', linewidth=1)
        
        # Progress bar
        ax.barh(0, progress, color='#388e3c', height=0.5, edgecolor='black', linewidth=1)
        
        # Add percentage text
        ax.text(
            progress / 2,
            0,
            f'{progress:.1f}%',
            ha='center',
            va='center',
            fontsize=14,
            weight='bold',
            color='white'
        )
        
        # Labels
        ax.text(
            -5,
            0,
            'Remediation Progress',
            ha='right',
            va='center',
            fontsize=11,
            weight='bold'
        )
        
        ax.text(
            105,
            0,
            f'{resolved_findings}/{total_findings}',
            ha='left',
            va='center',
            fontsize=11,
            weight='bold'
        )
        
        ax.set_xlim(-20, 120)
        ax.set_ylim(-1, 1)
        ax.axis('off')
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)
    
    def security_score_gauge(self, score: float) -> bytes:
        """
        Generate security score gauge (0-100).
        
        Args:
            score: Security score (0-100)
            
        Returns:
            PNG image as bytes
        """
        score = max(0, min(100, score))  # Clamp to 0-100
        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=self.dpi)
        
        # Determine color based on score
        if score >= 80:
            color = '#388e3c'  # Green
            status = 'Excellent'
        elif score >= 60:
            color = '#0288d1'  # Blue
            status = 'Good'
        elif score >= 40:
            color = '#fbc02d'  # Yellow
            status = 'Fair'
        elif score >= 20:
            color = '#f57c00'  # Orange
            status = 'Poor'
        else:
            color = '#d32f2f'  # Red
            status = 'Critical'
        
        # Create gauge
        theta = np.linspace(np.pi, 2*np.pi, 100)
        radius = 1
        
        # Background arc
        ax.plot(
            radius * np.cos(theta),
            radius * np.sin(theta),
            'o-',
            color='#e0e0e0',
            linewidth=10,
            markersize=0
        )
        
        # Score arc
        score_angle = np.pi + (score / 100) * np.pi
        theta_score = np.linspace(np.pi, score_angle, int(100 * (score / 100)))
        ax.plot(
            radius * np.cos(theta_score),
            radius * np.sin(theta_score),
            'o-',
            color=color,
            linewidth=10,
            markersize=0
        )
        
        # Score text
        ax.text(0, 0.3, f'{score:.0f}', ha='center', fontsize=36, weight='bold', color=color)
        ax.text(0, -0.1, status, ha='center', fontsize=14, weight='bold', color=color)
        ax.text(0, -0.3, 'Security Score', ha='center', fontsize=12, weight='bold', color='#666666')
        
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)
    
    def _fig_to_bytes(self, fig) -> bytes:
        """Convert matplotlib figure to PNG bytes"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf.getvalue()
    
    def _empty_chart_placeholder(self, message: str) -> bytes:
        """Create a placeholder chart with message"""
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        ax.text(
            0.5,
            0.5,
            message,
            ha='center',
            va='center',
            fontsize=14,
            transform=ax.transAxes,
            style='italic',
            color='gray'
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        return self._fig_to_bytes(fig)
