# src/agents/security_analyzer/cli.py
import os
import sys
import typer
import datetime
import tempfile
import io
import base64
from typing import Optional, List, Dict, Any
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from dotenv import load_dotenv
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as PDFTable, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import StringIO, BytesIO
from rich.console import RenderableType

from .agent import SecurityPoisoningAgent

# Load environment variables
load_dotenv()

# Initialize Rich components
console = Console()
app = typer.Typer()

def display_welcome():
    """Display a welcome message when the CLI starts."""
    console.print()
    console.print(Panel.fit(
        "[bold red]Security Poisoning Analyzer[/bold red]\n"
        "[dim]Your guardian against malicious compliance tampering[/dim]",
        border_style="red",
        padding=(1, 2)
    ))
    console.print()
    console.print("[dim]This tool helps detect potential security poisoning in compliance configurations.[/dim]")
    console.print("[dim]You can analyze files, compare configurations, or scan entire directories.[/dim]")
    console.print()
    console.print("[dim]Commands:[/dim]")
    console.print("[dim]- Type [bold]'analyze {file_path} [--pdf]'[/bold] to analyze a specific file[/dim]")
    console.print("[dim]- Type [bold]'scan {directory} [--pdf]'[/bold] to analyze all files in a directory[/dim]")
    console.print("[dim]- Type [bold]'compare {file1} {file2} [--pdf]'[/bold] to compare two configurations[/dim]")
    console.print("[dim]- Type [bold]'benchmark {file_path} [--pdf]'[/bold] to check a benchmark for tampering[/dim]")
    console.print("[dim]- Type [bold]'clear'[/bold] or [bold]'cls'[/bold] to clear the screen[/dim]")
    console.print("[dim]- Type [bold]'exit'[/bold] or [bold]'quit'[/bold] to end the session[/dim]")
    console.print("[dim]- Add [bold]'--pdf'[/bold] or [bold]'-p'[/bold] to any analysis command to export results as PDF[/dim]")
    console.print()

def display_file_analysis(results):
    """Display file analysis results."""
    if not results.get("success", False):
        console.print(f"[bold red]Error:[/bold red] {results.get('error', 'Unknown error')}")
        return
        
    risk_level = results.get("risk_level", "unknown")
    risk_color = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "green",
        "unknown": "blue"
    }.get(risk_level, "blue")
    
    # Display header with risk level
    console.print()
    console.print(Panel.fit(
        f"[bold {risk_color}]Security Analysis: {risk_level.upper()} Risk[/bold {risk_color}]",
        subtitle=f"[dim]{os.path.basename(results['file_path'])}[/dim]",
        border_style=risk_color
    ))
    
    # Display findings summary
    if results.get("poisoning_detected", False):
        console.print(Markdown(f"**Poisoning detected with {len(results['findings'])} issues found.**"))
        
        # Display findings table
        table = Table(title="Security Issues", box=box.ROUNDED)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Matched Text", style="yellow")
        table.add_column("Context", style="green")
        
        for finding in results.get("findings", []):
            table.add_row(
                finding["type"].replace("_", " ").title(),
                finding["matched_text"],
                finding["context"][:50] + "..." if len(finding["context"]) > 50 else finding["context"]
            )
        
        console.print(table)
        
        # Display remediations
        if results.get("suggested_remediations"):
            console.print()
            console.print("[bold]Suggested Remediations:[/bold]")
            for i, remediation in enumerate(results["suggested_remediations"], 1):
                console.print(f"{i}. {remediation}")
                
        # Display LLM explanation if available
        if results.get("explanation"):
            console.print()
            console.print(Panel(
                Markdown(results["explanation"]),
                title="[bold]Expert Analysis[/bold]",
                border_style="blue",
                expand=False
            ))
    else:
        console.print("[bold green]No security poisoning detected.[/bold green]")

def display_benchmark_analysis(results):
    """Display benchmark tampering analysis results."""
    if not results.get("success", False):
        console.print(f"[bold red]Error:[/bold red] {results.get('error', 'Unknown error')}")
        return
        
    risk_level = results.get("risk_level", "unknown")
    risk_color = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "green",
        "unknown": "blue"
    }.get(risk_level, "blue")
    
    # Display header with risk level
    console.print()
    console.print(Panel.fit(
        f"[bold {risk_color}]Benchmark Analysis: {risk_level.upper()} Risk[/bold {risk_color}]",
        subtitle=f"[dim]{os.path.basename(results['file_path'])}[/dim]",
        border_style=risk_color
    ))
    
    # Display findings summary
    if results.get("tampering_detected", False):
        console.print(Markdown(f"**Tampering detected with {len(results['suspicious_sections'])} suspicious sections found.**"))
        
        # Display findings table
        table = Table(title="Suspicious Sections", box=box.ROUNDED)
        table.add_column("Description", style="cyan", no_wrap=True)
        table.add_column("Section", style="yellow")
        table.add_column("Matched Text", style="red")
        
        for section in results.get("suspicious_sections", []):
            table.add_row(
                section["description"],
                section["section"][:30] + "..." if len(section["section"]) > 30 else section["section"],
                section["matched_text"]
            )
        
        console.print(table)
        
        # Display recommendations
        if results.get("recommendations"):
            console.print()
            console.print("[bold]Recommendations:[/bold]")
            for i, rec in enumerate(results["recommendations"], 1):
                console.print(f"{i}. {rec}")
                
        # Display LLM explanation if available
        if results.get("explanation"):
            console.print()
            console.print(Panel(
                Markdown(results["explanation"]),
                title="[bold]Expert Analysis[/bold]",
                border_style="blue",
                expand=False
            ))
    else:
        console.print("[bold green]No benchmark tampering detected.[/bold green]")

def display_drift_analysis(results):
    """Display configuration drift analysis results."""
    if not results.get("success", False):
        console.print(f"[bold red]Error:[/bold red] {results.get('error', 'Unknown error')}")
        return
        
    risk_level = results.get("risk_level", "unknown")
    risk_color = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "green",
        "unknown": "blue"
    }.get(risk_level, "blue")
    
    # Display header with risk level
    console.print()
    console.print(Panel.fit(
        f"[bold {risk_color}]Configuration Drift: {risk_level.upper()} Risk[/bold {risk_color}]",
        subtitle=f"[dim]{os.path.basename(results['current_file'])} vs {os.path.basename(results['reference_file'])}[/dim]",
        border_style=risk_color
    ))
    
    # Display summary
    if results.get("drift_detected", False):
        console.print(Markdown(f"**Drift detected with {len(results['additions'])} additions and {len(results['removals'])} removals.**"))
        
        # Display additions
        if results.get("additions"):
            console.print()
            console.print("[bold green]Additions:[/bold green]")
            additions_table = Table(box=box.SIMPLE)
            additions_table.add_column("Line", style="dim")
            additions_table.add_column("Content", style="green")
            
            for addition in results["additions"][:10]:  # Limit to 10 to avoid overwhelming
                additions_table.add_row(
                    str(addition.get("line_number", "")),
                    addition["content"]
                )
            
            if len(results["additions"]) > 10:
                additions_table.add_row("", f"... and {len(results['additions']) - 10} more additions")
                
            console.print(additions_table)
        
        # Display removals
        if results.get("removals"):
            console.print()
            console.print("[bold red]Removals:[/bold red]")
            removals_table = Table(box=box.SIMPLE)
            removals_table.add_column("Line", style="dim")
            removals_table.add_column("Content", style="red")
            
            for removal in results["removals"][:10]:  # Limit to 10
                removals_table.add_row(
                    str(removal.get("line_number", "")),
                    removal["content"]
                )
            
            if len(results["removals"]) > 10:
                removals_table.add_row("", f"... and {len(results['removals']) - 10} more removals")
                
            console.print(removals_table)
                
        # Display LLM explanation if available
        if results.get("explanation"):
            console.print()
            console.print(Panel(
                Markdown(results["explanation"]),
                title="[bold]Expert Analysis[/bold]",
                border_style="blue",
                expand=False
            ))
    else:
        console.print("[bold green]No configuration drift detected.[/bold green]")

def display_directory_scan(results):
    """Display directory scan results."""
    if not results.get("success", False):
        console.print(f"[bold red]Error:[/bold red] {results.get('error', 'Unknown error')}")
        return
    
    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold blue]Directory Scan Results[/bold blue]",
        subtitle=f"[dim]{results['directory']}[/dim]",
        border_style="blue"
    ))
    
    # Display summary
    files_analyzed = results["files_analyzed"]
    files_with_issues = results["files_with_issues"]
    
    console.print(f"Analyzed [bold]{files_analyzed}[/bold] files, found issues in [bold]{files_with_issues}[/bold] files.")
    
    if files_with_issues > 0:
        # Risk level stats
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for result in results["analysis_results"]:
            if result.get("poisoning_detected", False):
                risk_level = result.get("risk_level", "low")
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Display risk stats
        console.print()
        console.print("[bold]Risk Level Breakdown:[/bold]")
        risk_table = Table(box=box.SIMPLE)
        risk_table.add_column("Risk Level", style="cyan")
        risk_table.add_column("Count", style="magenta")
        
        for level, count in risk_counts.items():
            if count > 0:
                level_color = {
                    "critical": "red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green"
                }.get(level, "white")
                risk_table.add_row(
                    f"[{level_color}]{level.upper()}[/{level_color}]",
                    str(count)
                )
        
        console.print(risk_table)
        
        # Display files with issues
        console.print()
        console.print("[bold]Files with Security Issues:[/bold]")
        files_table = Table(box=box.SIMPLE)
        files_table.add_column("File", style="cyan")
        files_table.add_column("Risk", style="magenta")
        files_table.add_column("Issues", style="yellow")
        
        # Sort by risk level
        risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_results = sorted(
            [r for r in results["analysis_results"] if r.get("poisoning_detected", False)],
            key=lambda x: risk_order.get(x.get("risk_level", "low"), 0),
            reverse=True
        )
        
        for result in sorted_results[:10]:  # Limit to 10
            file_name = os.path.basename(result["file_path"])
            risk_level = result.get("risk_level", "low")
            level_color = {
                "critical": "red",
                "high": "red",
                "medium": "yellow",
                "low": "green"
            }.get(risk_level, "white")
            
            # Count issues by type
            issue_types = {}
            for finding in result.get("findings", []):
                finding_type = finding["type"]
                issue_types[finding_type] = issue_types.get(finding_type, 0) + 1
                
            issues_summary = ", ".join([f"{count} {t.replace('_', ' ')}" 
                                      for t, count in issue_types.items()])
            
            files_table.add_row(
                file_name,
                f"[{level_color}]{risk_level.upper()}[/{level_color}]",
                issues_summary
            )
        
        if len(sorted_results) > 10:
            files_table.add_row(
                f"... and {len(sorted_results) - 10} more files", "", ""
            )
            
        console.print(files_table)
    else:
        console.print("[bold green]No security issues found in any files.[/bold green]")

def parse_command(command: str) -> tuple:
    """Parse a command string into command and arguments."""
    parts = command.split()
    if not parts:
        return ("", [])
        
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    return (cmd, args)

def clear_screen():
    """Clear the terminal screen."""
    # Clear screen - works for both Windows and Unix/Linux
    if os.name == "nt":  # For Windows
        os.system("cls")
    else:  # For Unix/Linux/MacOS
        os.system("clear")

def create_vulnerability_chart(findings):
    """
    Create an enhanced pie chart showing the distribution of vulnerability types.
    
    Args:
        findings: List of findings from the analysis
        
    Returns:
        Image object for embedding in PDF
    """
    # Count vulnerability types
    vuln_types = [finding["type"].replace("_", " ").title() for finding in findings]
    vuln_counts = Counter(vuln_types)
    
    # Create figure with enhanced styling and background
    plt.figure(figsize=(8, 6), facecolor='#f8f9fa')
    
    # Create a pie chart with enhanced color palette and styling
    chart_colors = [
        '#ff6b6b',  # Red
        '#4dabf7',  # Blue
        '#69db7c',  # Green
        '#ffa94d',  # Orange
        '#da77f2',  # Purple
        '#4c6ef5',  # Indigo
        '#fcc419',  # Yellow
        '#15aabf',  # Cyan
        '#fa5252',  # Bright Red
        '#228be6'   # Bright Blue
    ]
    
    wedges, texts, autotexts = plt.pie(
        vuln_counts.values(), 
        labels=vuln_counts.keys(),
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        explode=[0.07] * len(vuln_counts),  # Increase explode for better separation
        colors=chart_colors,
        textprops={'fontsize': 11},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}  # Add edge to wedges for better contrast
    )
    
    # Style the text and percentage labels with improved readability
    for text in texts:
        text.set_fontsize(11)
        text.set_fontweight('bold')
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        # Add stroke effect for better readability on colored backgrounds
        try:
            autotext.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground='black')
            ])
        except:
            pass  # Fallback if path_effects not available
    
    plt.title('Vulnerability Distribution by Type', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
    
    # Save the chart to a BytesIO object
    img_data = BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
    img_data.seek(0)
    plt.close()
    
    # Create a ReportLab Image object
    img = Image(img_data, width=6*inch, height=4*inch)
    return img

def create_risk_level_chart(risk_counts):
    """
    Create a pie chart showing the distribution of risk levels.
    
    Args:
        risk_counts: Dictionary of risk levels and their counts
        
    Returns:
        Image object for embedding in PDF
    """
    # Filter out zero counts
    filtered_counts = {k: v for k, v in risk_counts.items() if v > 0}
    
    if not filtered_counts:
        return None
    
    # Create figure with enhanced styling
    plt.figure(figsize=(8, 6), facecolor='#f8f9fa')
    
    # Define enhanced colors for risk levels with better contrast
    risk_colors = {
        'critical': '#ff0000',  # Bright Red
        'high': '#ff4500',      # OrangeRed
        'medium': '#ffa500',    # Orange
        'low': '#008000',       # Green
        'unknown': '#4a6fa5'    # Steel Blue (more appealing than grey)
    }
    
    # Get the colors for each risk level present
    colors = [risk_colors.get(level.lower(), '#4a6fa5') for level in filtered_counts.keys()]
    
    # Create pie chart with enhanced styling
    labels = [level.upper() for level in filtered_counts.keys()]
    values = list(filtered_counts.values())
    
    wedges, texts, autotexts = plt.pie(
        values, 
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        explode=[0.07] * len(filtered_counts),  # Increased for better separation
        colors=colors,
        textprops={'fontsize': 12},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}  # Add white border for contrast
    )
    
    # Style the text with improved visibility and emphasis
    for text in texts:
        text.set_fontsize(12)
        text.set_fontweight('bold')
    
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        # Add stroke effect for better readability against colored backgrounds
        try:
            autotext.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground='black')
            ])
        except:
            pass  # Fallback if path_effects not available
    
    plt.title('Distribution by Risk Level', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')
    
    # Save chart to BytesIO
    img_data = BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight', dpi=150)
    img_data.seek(0)
    plt.close()
    
    # Create ReportLab Image
    from reportlab.lib.units import inch
    img = Image(img_data, width=6*inch, height=4*inch)
    return img
    
def save_as_pdf(results: dict, output_path: str = None) -> str:
    """
    Save analysis results as a colorized PDF file with charts.
    
    Args:
        results: The analysis results dictionary
        output_path: Path where to save the PDF file (optional)
        
    Returns:
        The path to the saved PDF file
    """
    # Import necessary modules
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    # Generate default filename if none provided
    if not output_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_type = ""
        
        if "file_path" in results:
            filename = os.path.basename(results["file_path"])
            analysis_type = "file"
        elif "current_file" in results and "reference_file" in results:
            filename = f"compare_{os.path.basename(results['current_file'])}_{os.path.basename(results['reference_file'])}"
            analysis_type = "compare"
        elif "directory" in results:
            dir_name = os.path.basename(results["directory"])
            filename = f"scan_{dir_name}"
            analysis_type = "scan"
        else:
            filename = "security_analysis"
            
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.getcwd(), "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        output_path = os.path.join(reports_dir, f"{filename}_{timestamp}.pdf")
    
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Define custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    normal_style = styles["Normal"]
    
    # Define risk level color mapping with hex values for consistent coloring
    risk_color_map = {
        "critical": "#FF0000",  # Red
        "high": "#FF4500",      # OrangeRed
        "medium": "#FFA500",    # Orange
        "low": "#008000",       # Green
        "unknown": "#0000FF"    # Blue
    }
    
    # Also maintain the ReportLab color objects for styling elements
    risk_colors = {
        "critical": colors.red,
        "high": colors.orangered,
        "medium": colors.orange,
        "low": colors.green,
        "unknown": colors.blue
    }
    
    # Create title based on analysis type with colored risk level
    if "file_path" in results and "risk_level" in results:
        # File analysis
        risk_level = results.get("risk_level", "unknown").lower()
        risk_color_hex = risk_color_map.get(risk_level, "#0000FF")
        
        file_name = os.path.basename(results.get("file_path", ""))
        title_text = f"Security Analysis Report: <font color='{risk_color_hex}'>{risk_level.upper()}</font> Risk"
        subtitle_text = f"File: {file_name}"
        
        # Create enhanced title style with drop shadow effect
        enhanced_title_style = ParagraphStyle(
            name='EnhancedTitle',
            parent=title_style,
            borderColor=colors.lightgrey,
            borderWidth=1,
            borderPadding=10,
            borderRadius=5
        )
        
        elements.append(Paragraph(title_text, enhanced_title_style))
        elements.append(Paragraph(subtitle_text, ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            alignment=TA_CENTER
        )))
        
    elif "current_file" in results and "reference_file" in results:
        # Comparison analysis
        risk_level = results.get("risk_level", "unknown").lower()
        risk_color_hex = risk_color_map.get(risk_level, "#0000FF")
        
        file1 = os.path.basename(results.get("current_file", ""))
        file2 = os.path.basename(results.get("reference_file", ""))
        title_text = f"Configuration Drift Analysis: <font color='{risk_color_hex}'>{risk_level.upper()}</font> Risk"
        subtitle_text = f"Comparing {file1} vs {file2}"
        
        elements.append(Paragraph(title_text, title_style))
        elements.append(Paragraph(subtitle_text, ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            alignment=TA_CENTER
        )))
        
    elif "directory" in results:
        # Directory scan
        dir_name = results.get("directory", "")
        title_text = f"Directory Scan Results"
        subtitle_text = f"Directory: {dir_name}"
        
        elements.append(Paragraph(title_text, title_style))
        elements.append(Paragraph(subtitle_text, ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            alignment=TA_CENTER
        )))
    
    # Add date
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated: {timestamp}", ParagraphStyle(
        name='DateStyle',
        parent=styles["Italic"],
        alignment=TA_CENTER
    )))
    elements.append(Spacer(1, 20))
    
    # Add summary section
    elements.append(Paragraph("Summary", heading_style))
    
    # File Analysis Content
    if "file_path" in results and "findings" in results:
        if results.get("poisoning_detected", False):
            # Create colorized summary text
            risk_level = results.get("risk_level", "unknown").lower()
            risk_color = risk_color_map.get(risk_level, colors.blue)
            
            summary_text = (
                f"Poisoning detected with <b>{len(results['findings'])}</b> issues found. "
                f"Overall risk level: <font color='{risk_color_hex}'><b>{risk_level.upper()}</b></font>"
            )
            elements.append(Paragraph(summary_text, normal_style))
            elements.append(Spacer(1, 10))
            
            # Add vulnerability pie chart
            if results.get("findings"):
                elements.append(Paragraph("Vulnerability Distribution", heading_style))
                chart = create_vulnerability_chart(results["findings"])
                elements.append(chart)
                elements.append(Spacer(1, 15))
            
            # Add findings table with colorized styling
            elements.append(Paragraph("Security Issues Detail", heading_style))
            
            # Create table data
            table_data = [["Type", "Matched Text", "Context"]]
            for finding in results.get("findings", []):
                finding_type = finding["type"].replace("_", " ").title()
                table_data.append([
                    finding_type,
                    finding["matched_text"],
                    finding["context"][:100] + "..." if len(finding["context"]) > 100 else finding["context"]
                ])
            
            # Create table with enhanced styling and gradients
            table = PDFTable(table_data, repeatRows=1)
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),  # Darker blue for header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),  # Slightly larger font for header
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),  # Added top padding for header
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),  # Lighter grid color
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.HexColor('#e9ecef')]),  # Subtle alternating colors
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0d47a1'))  # Thicker line below header
            ]
            
            # Add alternating row colors
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    bg_color = colors.whitesmoke
                else:
                    bg_color = colors.lightgrey
                table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
            
            table.setStyle(TableStyle(table_style))
            elements.append(table)
            
            # Add remediations with colorized bullets
            if results.get("suggested_remediations"):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Suggested Remediations", heading_style))
                
                for i, remediation in enumerate(results["suggested_remediations"], 1):
                    bullet_style = ParagraphStyle(
                        f'BulletStyle{i}',
                        parent=normal_style,
                        leftIndent=20,
                        firstLineIndent=-20,
                    )
                    elements.append(Paragraph(
                        f"<font color='#00008B'><b>{i}.</b></font> {remediation}",
                        bullet_style
                    ))
                    elements.append(Spacer(1, 6))
                    
            # Add explanation with styled header
            if results.get("explanation"):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Expert Analysis", heading_style))
                
                # Style the explanation with enhanced formatting for better readability
                explanation_style = ParagraphStyle(
                    'ExplanationStyle',
                    parent=normal_style,
                    leftIndent=15,
                    rightIndent=15,
                    spaceAfter=12,
                    borderColor=colors.HexColor('#adb5bd'),  # Darker border color
                    borderWidth=1,
                    borderPadding=12,  # More padding
                    backColor=colors.HexColor('#f0f4f8'),  # Slightly blue-tinted background
                    leading=14,  # Better line spacing for readability
                    firstLineIndent=10,  # First line indent for paragraph style
                    bulletIndent=5  # Better bullet point alignment
                )
                
                elements.append(Paragraph(results["explanation"], explanation_style))
        else:
            elements.append(Paragraph(
                "<font color='green'><b>No security poisoning detected.</b></font>",
                normal_style
            ))
    
    # Directory scan content with enhanced styling
    elif "directory" in results and "files_analyzed" in results:
        files_analyzed = results["files_analyzed"]
        files_with_issues = results["files_with_issues"]
        
        if files_with_issues > 0:
            elements.append(Paragraph(
                f"Analyzed <b>{files_analyzed}</b> files, found issues in <font color='red'><b>{files_with_issues}</b></font> files.",
                normal_style
            ))
            
            # Risk level stats with chart
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("Risk Level Breakdown", heading_style))
            
            risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for result in results["analysis_results"]:
                if result.get("poisoning_detected", False):
                    risk_level = result.get("risk_level", "low")
                    risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            # Add risk level pie chart
            chart = create_risk_level_chart(risk_counts)
            if chart:
                elements.append(chart)
                elements.append(Spacer(1, 15))
            
            # Create risk table with colored risk levels
            risk_table_data = [["Risk Level", "Count"]]
            for level, count in risk_counts.items():
                if count > 0:
                    level_color_hex = risk_color_map.get(level, "#000000")
                    risk_table_data.append([
                        f"<font color='{level_color_hex}'><b>{level.upper()}</b></font>",
                        str(count)
                    ])
            
            risk_table = PDFTable(risk_table_data, repeatRows=1)
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),  # Darker blue for header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),  # Slightly larger font for header
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),  # Added top padding for header
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),  # Lighter grid color
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.HexColor('#e9ecef')]),  # Subtle alternating colors
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0d47a1')),  # Thicker line below header
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#7a7a7a'))  # Box around the table
            ]))
            elements.append(risk_table)
            
            # Files with issues
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Files with Security Issues", heading_style))
            
            # Sort by risk level
            risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            sorted_results = sorted(
                [r for r in results["analysis_results"] if r.get("poisoning_detected", False)],
                key=lambda x: risk_order.get(x.get("risk_level", "low"), 0),
                reverse=True
            )
            
            # Create files table with colored risk levels
            files_table_data = [["File", "Risk", "Issues"]]
            for result in sorted_results:
                file_name = os.path.basename(result["file_path"])
                risk_level = result.get("risk_level", "low")
                risk_color_hex = risk_color_map.get(risk_level, "#000000")
                
                # Count issues by type
                issue_types = {}
                for finding in result.get("findings", []):
                    finding_type = finding["type"]
                    issue_types[finding_type] = issue_types.get(finding_type, 0) + 1
                    
                issues_summary = ", ".join([f"{count} {t.replace('_', ' ')}" 
                                          for t, count in issue_types.items()])
                
                files_table_data.append([
                    file_name,
                    f"<font color='{risk_color_hex}'><b>{risk_level.upper()}</b></font>",
                    issues_summary
                ])
            
            files_table = PDFTable(files_table_data, repeatRows=1)
            files_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),  # Darker blue for header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),  # Slightly larger font for header
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),  # Added top padding for header
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),  # Lighter grid color
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.HexColor('#e9ecef')]),  # Subtle alternating colors
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0d47a1')),  # Thicker line below header
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#7a7a7a'))  # Box around the table
            ]))
            elements.append(files_table)
        else:
            elements.append(Paragraph(
                "<font color='green'><b>No security issues found in any files.</b></font>",
                normal_style
            ))
    
    # Drift analysis content with enhanced styling
    elif "current_file" in results and "reference_file" in results:
        if results.get("drift_detected", False):
            additions_count = len(results.get('additions', []))
            removals_count = len(results.get('removals', []))
            
            # Create a pie chart for additions vs removals if both exist
            if additions_count > 0 or removals_count > 0:
                plt.figure(figsize=(6, 4))
                labels = []
                sizes = []
                colors = []
                
                if additions_count > 0:
                    labels.append('Additions')
                    sizes.append(additions_count)
                    colors.append('#66b3ff')  # Blue
                    
                if removals_count > 0:
                    labels.append('Removals')
                    sizes.append(removals_count)
                    colors.append('#ff9999')  # Red
                
                if labels:
                    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                           startangle=90, shadow=True, explode=[0.05] * len(labels))
                    plt.title('Configuration Changes', fontsize=14, fontweight='bold')
                    plt.axis('equal')
                    
                    # Save to BytesIO
                    drift_img_data = BytesIO()
                    plt.savefig(drift_img_data, format='png', bbox_inches='tight', dpi=150)
                    drift_img_data.seek(0)
                    plt.close()
                    
                    # Add to PDF
                    from reportlab.lib.units import inch
                    drift_img = Image(drift_img_data, width=4*inch, height=3*inch)
                    
                    elements.append(Paragraph(
                        f"Drift detected with <font color='blue'><b>{additions_count}</b></font> additions and "
                        f"<font color='red'><b>{removals_count}</b></font> removals.",
                        normal_style
                    ))
                    elements.append(drift_img)
                    elements.append(Spacer(1, 15))
            else:
                elements.append(Paragraph(
                    f"Drift detected with {additions_count} additions and {removals_count} removals.",
                    normal_style
                ))
            
            # Additions with enhanced styling
            if results.get("additions"):
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(
                    "<font color='blue'><b>Additions</b></font>", 
                    heading_style
                ))
                
                additions_data = [["Line", "Content"]]
                for addition in results["additions"]:
                    additions_data.append([
                        str(addition.get("line_number", "")),
                        addition["content"]
                    ])
                
                additions_table = PDFTable(additions_data, repeatRows=1)
                additions_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),  # Dark blue for header
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                    # Light blue background for additions
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e6f2ff'), colors.HexColor('#d9e8ff')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0047ab')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#7a7a7a'))
                ]))
                elements.append(additions_table)
            
            # Removals with enhanced styling
            if results.get("removals"):
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(
                    "<font color='red'><b>Removals</b></font>", 
                    heading_style
                ))
                
                removals_data = [["Line", "Content"]]
                for removal in results["removals"]:
                    removals_data.append([
                        str(removal.get("line_number", "")),
                        removal["content"]
                    ])
                
                removals_table = PDFTable(removals_data, repeatRows=1)
                removals_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#881c1c')),  # Dark red for header
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
                    # Light red background for removals
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffe6e6'), colors.HexColor('#ffd9d9')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#8b0000')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#7a7a7a'))
                ]))
                elements.append(removals_table)
            
            # Add explanation with styled header
            if results.get("explanation"):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Expert Analysis", heading_style))
                
                explanation_style = ParagraphStyle(
                    'ExplanationStyle',
                    parent=normal_style,
                    leftIndent=10,
                    rightIndent=10,
                    spaceAfter=12,
                    borderColor=colors.lightgrey,
                    borderWidth=1,
                    borderPadding=10,
                    backColor=colors.whitesmoke
                )
                
                elements.append(Paragraph(results["explanation"], explanation_style))
        else:
            elements.append(Paragraph(
                "<font color='green'><b>No configuration drift detected.</b></font>",
                normal_style
            ))
    
    # Add enhanced footer with logo and styling
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#505050'),  # Darker gray for better readability
        alignment=TA_CENTER,
        leading=12,  # Better line height
        borderColor=colors.HexColor('#e0e0e0'),
        borderWidth=0.5,
        borderPadding=10,
        borderRadius=3
    )
    
    elements.append(Spacer(1, 40))
    
    # Add horizontal rule before footer
    elements.append(Paragraph(
        "<hr width='100%' color='#cccccc' thickness=1 />",
        ParagraphStyle(
            'HRStyle',
            parent=styles['Normal'],
            alignment=TA_CENTER
        )
    ))
    
    # Enhanced footer with current date and time for more professional look
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph(
        f"<b>Security Poisoning Analyzer</b> | Report generated on {current_datetime} | CONFIDENTIAL",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    return output_path

def interactive_mode(agent: SecurityPoisoningAgent):
    """Run the interactive CLI mode."""
    display_welcome()
    
    while True:
        # Get user command
        command_str = Prompt.ask("\n[bold red]Security>[/bold red]")
        
        # Exit conditions
        if command_str.lower() in ["exit", "quit", "q", "bye"]:
            console.print("[yellow]Goodbye! Stay secure![/yellow]")
            sys.exit(0)
            
        # Clear screen command
        if command_str.lower() in ["clear", "cls"]:
            clear_screen()
            display_welcome()
            continue
            
        # Skip empty commands
        if not command_str.strip():
            continue
            
        # Parse command
        cmd, args = parse_command(command_str)
        
        if cmd == "analyze":
            if not args:
                console.print("[bold red]Error:[/bold red] Missing file path. Usage: analyze {file_path} [--pdf]")
                continue
            
            # Check for PDF export flag
            export_pdf = "--pdf" in args or "-p" in args
            if export_pdf:
                args = [arg for arg in args if arg not in ("--pdf", "-p")]
            
            if not args:
                console.print("[bold red]Error:[/bold red] Missing file path. Usage: analyze {file_path} [--pdf]")
                continue
                
            file_path = args[0]
            
            # Check if file exists
            if not os.path.exists(file_path):
                console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
                continue
                
            # Analyze the file
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Analyzing {os.path.basename(file_path)}...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("Analyzing...", total=None)
                results = agent.analyze_file(file_path)
            
            # Display results
            display_file_analysis(results)
            
            # Export as PDF if requested
            if export_pdf and results.get("success", False):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Generating PDF report...[/bold blue]"),
                    transient=True,
                ) as progress:
                    progress.add_task("Generating...", total=None)
                    pdf_path = save_as_pdf(results)
                    
                console.print(f"[bold green]PDF report saved to:[/bold green] {pdf_path}")
            
        elif cmd == "benchmark":
            if not args:
                console.print("[bold red]Error:[/bold red] Missing file path. Usage: benchmark {file_path} [--pdf]")
                continue
            
            # Check for PDF export flag
            export_pdf = "--pdf" in args or "-p" in args
            if export_pdf:
                args = [arg for arg in args if arg not in ("--pdf", "-p")]
            
            if not args:
                console.print("[bold red]Error:[/bold red] Missing file path. Usage: benchmark {file_path} [--pdf]")
                continue
                
            file_path = args[0]
            
            # Check if file exists
            if not os.path.exists(file_path):
                console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
                continue
                
            # Analyze the benchmark
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Analyzing benchmark {os.path.basename(file_path)}...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("Analyzing...", total=None)
                results = agent.analyze_benchmark(file_path)
            
            # Display results
            display_benchmark_analysis(results)
            
            # Export as PDF if requested
            if export_pdf and results.get("success", False):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Generating PDF report...[/bold blue]"),
                    transient=True,
                ) as progress:
                    progress.add_task("Generating...", total=None)
                    pdf_path = save_as_pdf(results)
                    
                console.print(f"[bold green]PDF report saved to:[/bold green] {pdf_path}")
            
        elif cmd == "compare":
            # Check for PDF export flag
            export_pdf = "--pdf" in args or "-p" in args
            if export_pdf:
                args = [arg for arg in args if arg not in ("--pdf", "-p")]
            
            if len(args) < 2:
                console.print("[bold red]Error:[/bold red] Missing file paths. Usage: compare {current_file} {reference_file} [--pdf]")
                continue
                
            current_file = args[0]
            reference_file = args[1]
            
            # Check if files exist
            if not os.path.exists(current_file):
                console.print(f"[bold red]Error:[/bold red] File not found: {current_file}")
                continue
                
            if not os.path.exists(reference_file):
                console.print(f"[bold red]Error:[/bold red] File not found: {reference_file}")
                continue
                
            # Compare the files
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Comparing configurations...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("Comparing...", total=None)
                results = agent.compare_configurations(current_file, reference_file)
            
            # Display results
            display_drift_analysis(results)
            
            # Export as PDF if requested
            if export_pdf and results.get("success", False):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Generating PDF report...[/bold blue]"),
                    transient=True,
                ) as progress:
                    progress.add_task("Generating...", total=None)
                    pdf_path = save_as_pdf(results)
                    
                console.print(f"[bold green]PDF report saved to:[/bold green] {pdf_path}")
            
        elif cmd == "scan":
            if not args:
                console.print("[bold red]Error:[/bold red] Missing directory path. Usage: scan {directory_path} [--no-recursive] [--pdf]")
                continue
            
            # Check for PDF export flag
            export_pdf = "--pdf" in args or "-p" in args
            if export_pdf:
                args = [arg for arg in args if arg not in ("--pdf", "-p")]
                
            if not args:
                console.print("[bold red]Error:[/bold red] Missing directory path. Usage: scan {directory_path} [--no-recursive] [--pdf]")
                continue
                
            dir_path = args[0]
            recursive = "--no-recursive" not in args and "-nr" not in args
            
            # Check if directory exists
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                console.print(f"[bold red]Error:[/bold red] Directory not found: {dir_path}")
                continue
                
            # Scan the directory
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Scanning {dir_path}...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("Scanning...", total=None)
                results = agent.analyze_directory(dir_path, recursive)
            
            # Display results
            display_directory_scan(results)
            
            # Export as PDF if requested
            if export_pdf and results.get("success", False):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Generating PDF report...[/bold blue]"),
                    transient=True,
                ) as progress:
                    progress.add_task("Generating...", total=None)
                    pdf_path = save_as_pdf(results)
                    
                console.print(f"[bold green]PDF report saved to:[/bold green] {pdf_path}")
            
        elif cmd == "help":
            display_welcome()
            
        else:
            # If not a known command, try to process as a question
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Processing your question...[/bold blue]"),
                transient=True,
            ) as progress:
                progress.add_task("Processing...", total=None)
                
                try:
                    result = agent.process_query(command_str)
                    if result.get("success", False):
                        console.print(Panel(
                            Markdown(result["response"]),
                            title="[bold]Response[/bold]",
                            border_style="green",
                            expand=False
                        ))
                    else:
                        console.print(f"[bold red]Error:[/bold red] {result.get('error', 'Unknown error')}")
                except Exception as e:
                    console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def cli(
    google_api_key: Optional[str] = typer.Option(
        None, 
        "--google-api-key", 
        help="Google API key (overrides environment variable)"
    )
):
    """Interactive Security Poisoning Analyzer CLI."""
    try:
        # Initialize agent
        agent = SecurityPoisoningAgent(
            google_api_key=google_api_key or os.getenv("GOOGLE_API_KEY")
        )
        
        # Start interactive mode
        interactive_mode(agent)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    app()
