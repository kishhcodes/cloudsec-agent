# security_analyzer_demo.py
"""
Demo script for the Security Poisoning Analyzer.
This script demonstrates how to use the Security Poisoning Analyzer to analyze
a configuration file for security poisoning.
"""

import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

from src.agents.security_analyzer.agent import SecurityPoisoningAgent

def main():
    # Load environment variables
    load_dotenv()
    
    # Set Google application credentials if available
    if os.path.exists("config/vertex.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"
    
    # Initialize console for rich output
    console = Console()
    
    # Display welcome message
    console.print(Panel.fit(
        "[bold red]Security Poisoning Analyzer Demo[/bold red]",
        border_style="red"
    ))
    console.print("This demo will analyze a test configuration file for security poisoning.")
    console.print()
    
    # Path to test configuration
    test_file = "data/test_config.json"
    
    # Create agent
    console.print("Creating security poisoning agent...")
    agent = SecurityPoisoningAgent()
    
    # Analyze file
    console.print(f"Analyzing {test_file}...")
    results = agent.analyze_file(test_file)
    
    # Display results
    console.print()
    if results["success"]:
        poisoning_detected = results["poisoning_detected"]
        risk_level = results["risk_level"]
        
        risk_color = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "green"
        }.get(risk_level, "blue")
        
        title = f"Security Analysis: {risk_level.upper()} RISK" if poisoning_detected else "Security Analysis: No Issues Found"
        
        console.print(Panel.fit(
            f"[bold {risk_color}]{title}[/bold {risk_color}]",
            border_style=risk_color
        ))
        
        if poisoning_detected:
            console.print(f"Found [bold red]{len(results['findings'])}[/bold red] security issues in configuration.")
            console.print()
            
            # Display findings
            for i, finding in enumerate(results["findings"], 1):
                console.print(f"[bold]Issue {i}: {finding['type'].replace('_', ' ').title()}[/bold]")
                console.print(f"  Matched: [yellow]{finding['matched_text']}[/yellow]")
                console.print(f"  Context: {finding['context'][:50]}...")
                console.print()
            
            # Display LLM explanation if available
            if "explanation" in results:
                console.print(Panel(
                    Markdown(results["explanation"]),
                    title="Expert Analysis",
                    border_style="blue"
                ))
        else:
            console.print("[green]No security poisoning detected in configuration.[/green]")
    else:
        console.print(f"[bold red]Error:[/bold red] {results['error']}")
    
    # Display summary
    console.print()
    console.print(Panel.fit(
        "To explore more features, run: [bold]python security_analyzer_cli.py[/bold]",
        border_style="blue"
    ))

if __name__ == "__main__":
    main()
