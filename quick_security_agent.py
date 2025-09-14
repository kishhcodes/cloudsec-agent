#!/usr/bin/env python3
"""
Quick AWS Security Agent - Minimal startup time
"""

import os
import sys
import json
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

sys.path.insert(0, 'src')
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
console = Console()

def quick_aws_command(command):
    """Execute AWS command directly without Docker."""
    console.print(f"[blue]Executing:[/blue] {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            console.print("[green]✓ Success[/green]")
            return {"status": "success", "output": result.stdout}
        else:
            console.print(f"[red]✗ Error: {result.stderr}[/red]")
            return {"status": "error", "output": result.stderr}
            
    except Exception as e:
        console.print(f"[red]✗ Exception: {str(e)}[/red]")
        return {"status": "error", "output": str(e)}

def analyze_with_gemini(command, output):
    """Analyze AWS output with Gemini."""
    if not os.environ.get("GOOGLE_API_KEY"):
        console.print("[yellow]No GOOGLE_API_KEY - skipping AI analysis[/yellow]")
        return
    
    console.print("[yellow]🤖 Gemini analyzing...[/yellow]")
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
        
        messages = [
            SystemMessage(content="You are an AWS security expert. Analyze this AWS command output for security issues and provide specific recommendations."),
            HumanMessage(content=f"Command: {command}\n\nOutput:\n{output}\n\nProvide security analysis:")
        ]
        
        response = llm.invoke(messages)
        console.print(Panel(response.content, title="🤖 Gemini Analysis", border_style="green"))
        
    except Exception as e:
        console.print(f"[red]AI analysis failed: {str(e)}[/red]")

def main():
    console.print(Panel("⚡ Quick AWS Security Agent", border_style="blue"))
    
    # Quick credential check
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        console.print("[red]Missing AWS_ACCESS_KEY_ID[/red]")
        return
    
    # Test AWS connection
    console.print("\n[bold]Testing AWS connection...[/bold]")
    result = quick_aws_command("aws sts get-caller-identity")
    
    if result["status"] == "success":
        try:
            data = json.loads(result["output"])
            console.print(f"[green]✓ Connected to Account: {data.get('Account')}[/green]")
        except:
            pass
        
        analyze_with_gemini("aws sts get-caller-identity", result["output"])
    else:
        console.print("[red]AWS connection failed - check credentials[/red]")
        return
    
    # Quick security checks
    security_commands = [
        "aws iam get-account-password-policy",
        "aws iam get-account-summary", 
        "aws s3 ls",
        "aws ec2 describe-security-groups --max-items 3"
    ]
    
    for cmd in security_commands:
        console.print(f"\n{'='*50}")
        result = quick_aws_command(cmd)
        
        if result["status"] == "success":
            console.print(f"[dim]Output: {result['output'][:200]}...[/dim]")
            analyze_with_gemini(cmd, result["output"])

if __name__ == "__main__":
    main()