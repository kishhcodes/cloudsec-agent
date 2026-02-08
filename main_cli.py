#!/usr/bin/env python3
"""
Unified Cloud Security Assistant CLI

This is a unified chatbot interface that allows switching between different agents
while maintaining natural language understanding. Similar to GitHub Copilot's interface
but specialized for cloud security.
"""

import os
import sys
import json
import time
import re
from typing import Dict, Any, List, Optional
import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.layout import Layout
from rich import box
from rich.style import Style
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import agents
from aws_security_agent import AWSSecurityAgent
from src.agents.security_analyzer.agent import SecurityPoisoningAgent
from src.agents.compliance_bot.web_search import WebSearcher
from src.agents.compliance_bot.compliance_assistant import ComplianceAssistant
from src.agents.gcp_security.agent import GCPSecurityAgent
from src.agents.azure_security.agent import AzureSecurityAgent
from src.aws_mcp.client import AWSMCPClient
from src.azure_mcp.client import AzureMCPClient
from src.gcp_mcp.client import GCPMCPClient

# For LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# Set Google credentials
if os.path.exists("config/vertex.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"

# Initialize Typer app
app = typer.Typer(help="Unified Cloud Security Assistant CLI")
console = Console()

class AgentMode:
    """Enum-like class for different agent modes"""
    AWS_SECURITY = "aws-security"
    AWS_MCP = "aws-mcp"
    GCP_SECURITY = "gcp-security"
    GCP_MCP = "gcp-mcp"
    AZURE_SECURITY = "azure-security"
    AZURE_MCP = "azure-mcp"
    SECURITY_ANALYZER = "security-analyzer"
    COMPLIANCE_CHAT = "compliance-chat"
    ARTICLE_SEARCH = "article-search"
    GENERAL = "general"

class CloudAssistant:
    """Unified chatbot interface for all agents"""
    
    def __init__(self):
        """Initialize the Cloud Assistant"""
        self.current_mode = AgentMode.GENERAL
        self.history = []
        self.agents = {}
        
        # Initialize LLM for general mode and mode switching
        self.llm = self._init_llm()
        
        # Lazy load agents when first needed
        self._load_agent(AgentMode.GENERAL)
    
    def _init_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the Gemini LLM."""
        try:
            # Check for environment variables
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                raise ValueError("No Google API key found in environment variables")
            
            # Initialize the LLM
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.2,
                top_p=0.85,
                convert_system_message_to_human=True
            )
        except Exception as e:
            console.print(f"[bold red]Error initializing LLM:[/bold red] {str(e)}")
            sys.exit(1)
    
    def _load_agent(self, mode: str):
        """Load an agent if it's not already loaded."""
        if mode in self.agents:
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]Loading {mode} agent...[/bold blue]"),
            transient=True,
        ) as progress:
            progress.add_task("Loading", total=None)
            
            try:
                if mode == AgentMode.AWS_SECURITY:
                    self.agents[mode] = AWSSecurityAgent()
                elif mode == AgentMode.AWS_MCP:
                    client = AWSMCPClient()
                    client.start()
                    self.agents[mode] = client
                elif mode == AgentMode.GCP_SECURITY:
                    self.agents[mode] = GCPSecurityAgent()
                elif mode == AgentMode.GCP_MCP:
                    client = GCPMCPClient()
                    client.start()
                    self.agents[mode] = client
                elif mode == AgentMode.AZURE_SECURITY:
                    self.agents[mode] = AzureSecurityAgent()
                elif mode == AgentMode.AZURE_MCP:
                    client = AzureMCPClient()
                    client.start()
                    self.agents[mode] = client
                elif mode == AgentMode.SECURITY_ANALYZER:
                    self.agents[mode] = SecurityPoisoningAgent()
                elif mode == AgentMode.COMPLIANCE_CHAT:
                    self.agents[mode] = ComplianceAssistant()
                elif mode == AgentMode.ARTICLE_SEARCH:
                    self.agents[mode] = WebSearcher()
                elif mode == AgentMode.GENERAL:
                    # General mode uses the base LLM
                    self.agents[mode] = self.llm
            except Exception as e:
                console.print(f"[bold red]Error loading agent {mode}:[/bold red] {str(e)}")
                # Fall back to general mode
                self.current_mode = AgentMode.GENERAL
    
    def _detect_agent_mode(self, user_input: str) -> str:
        """
        Detect which agent should handle the user input.
        Returns the agent mode.
        """
        # First check for explicit mode switching commands
        # NOTE: More specific patterns must come before less specific ones!
        mode_switch_patterns = {
            # MCP patterns (more specific, must come first)
            r"(?i)(?:switch|use|change) (?:to )?(?:aws\s+mcp)": AgentMode.AWS_MCP,
            r"(?i)(?:switch|use|change) (?:to )?(?:gcp\s+mcp)": AgentMode.GCP_MCP,
            r"(?i)(?:switch|use|change) (?:to )?(?:azure\s+mcp)": AgentMode.AZURE_MCP,
            # Agent patterns (less specific)
            r"(?i)(?:switch|use|change) (?:to )?(?:aws|aws security)": AgentMode.AWS_SECURITY,
            r"(?i)(?:switch|use|change) (?:to )?(?:gcp|google cloud|gcp security)": AgentMode.GCP_SECURITY,
            r"(?i)(?:switch|use|change) (?:to )?(?:azure|azure security|microsoft azure)": AgentMode.AZURE_SECURITY,
            r"(?i)(?:switch|use|change) (?:to )?security(?: analyzer)?": AgentMode.SECURITY_ANALYZER,
            r"(?i)(?:switch|use|change) (?:to )?compliance(?: chat)?": AgentMode.COMPLIANCE_CHAT,
            r"(?i)(?:switch|use|change) (?:to )?article(?: search)?": AgentMode.ARTICLE_SEARCH,
            r"(?i)(?:switch|use|change) (?:to )?general": AgentMode.GENERAL
        }
        
        for pattern, mode in mode_switch_patterns.items():
            if re.search(pattern, user_input):
                return mode
        
        # If not explicitly switching, use LLM to detect intent
        if self.current_mode == AgentMode.GENERAL:
            # Use patterns to detect intent if in general mode
            aws_patterns = [r"aws", r"cloud\s+trail", r"cloudwatch", r"s3\s+bucket", r"lambda", r"ec2"]
            aws_mcp_patterns = [r"aws\s+mcp", r"gcloud|gsutil.*aws", r"aws\s+command", r"run\s+aws\s+cli"]
            gcp_patterns = [r"gcp", r"google\s+cloud", r"cloud\s+storage", r"cloud\s+sql", r"compute\s+engine"]
            gcp_mcp_patterns = [r"gcp\s+mcp", r"gcloud\s+command", r"gsutil\s+command", r"run\s+gcloud"]
            azure_patterns = [r"azure", r"microsoft\s+azure", r"entra\s+id", r"azure\s+ad", r"storage\s+account", r"virtual\s+machine", r"azure\s+sql", r"sql\s+database", r"sql\s+server", r"cosmos\s+db"]
            azure_mcp_patterns = [r"azure\s+mcp", r"az\s+command", r"run\s+azure\s+cli"]
            security_patterns = [r"security\s+poison", r"benchmark", r"compliance\s+tamper", r"cis"]
            compliance_patterns = [r"compliance\s+question", r"standards", r"regulations", r"compliance\s+requirement"]
            article_patterns = [r"article", r"blog\s+post", r"publication", r"wrote", r"author"]
            
            # Check patterns (MCP patterns first for priority)
            for pattern in aws_mcp_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.AWS_MCP
            
            for pattern in gcp_mcp_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.GCP_MCP
            
            for pattern in azure_mcp_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.AZURE_MCP
            
            for pattern in aws_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.AWS_SECURITY
            
            for pattern in gcp_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.GCP_SECURITY
            
            for pattern in azure_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.AZURE_SECURITY
            
            for pattern in security_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.SECURITY_ANALYZER
            
            for pattern in compliance_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.COMPLIANCE_CHAT
            
            for pattern in article_patterns:
                if re.search(pattern, user_input.lower()):
                    return AgentMode.ARTICLE_SEARCH
        
        # Default to current mode if no pattern matches
        return self.current_mode
    
    def process_command(self, user_input: str):
        """Process a user command or query"""
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            console.print("[yellow]Goodbye! Stay secure![/yellow]")
            sys.exit(0)
        
        # Check for clear screen command
        if user_input.lower() in ["clear", "cls"]:
            self._clear_screen()
            display_welcome()
            return
        
        # Check for help command
        if user_input.lower() in ["help", "?"]:
            self._display_help()
            return
        
        # Detect which agent should handle this input
        detected_mode = self._detect_agent_mode(user_input)
        
        # If mode is changing, notify user and switch modes
        if detected_mode != self.current_mode:
            previous_mode = self.current_mode
            self.current_mode = detected_mode
            self._load_agent(detected_mode)
            console.print(f"[bold blue]Switched from {previous_mode} to {detected_mode} mode[/bold blue]")
        
        # Process the command with the appropriate agent
        self._process_with_current_agent(user_input)
    
    def _process_with_current_agent(self, user_input: str):
        """Process the input with the current agent"""
        # Track command in history
        self.history.append({"role": "user", "content": user_input})
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Processing...[/bold green]"),
            transient=True,
        ) as progress:
            progress.add_task("Processing", total=None)
            
            try:
                if self.current_mode == AgentMode.AWS_SECURITY:
                    agent = self.agents[AgentMode.AWS_SECURITY]
                    response = agent.process_command(user_input)
                    # AWS agent already prints output, so nothing needed here
                
                elif self.current_mode == AgentMode.AWS_MCP:
                    client = self.agents[AgentMode.AWS_MCP]
                    response = client.execute_command(user_input)
                    if response.get("status") == "success":
                        console.print(Markdown(response.get("output", "Command executed successfully")))
                    else:
                        console.print(f"[bold red]Error:[/bold red] {response.get('output', 'Unknown error')}")
                
                elif self.current_mode == AgentMode.GCP_SECURITY:
                    agent = self.agents[AgentMode.GCP_SECURITY]
                    response = agent.process_command(user_input)
                    console.print(Markdown(response))
                
                elif self.current_mode == AgentMode.GCP_MCP:
                    client = self.agents[AgentMode.GCP_MCP]
                    response = client.execute_command(user_input)
                    if response.get("status") == "success":
                        console.print(Markdown(response.get("output", "Command executed successfully")))
                    else:
                        console.print(f"[bold red]Error:[/bold red] {response.get('output', 'Unknown error')}")
                
                elif self.current_mode == AgentMode.AZURE_SECURITY:
                    agent = self.agents[AgentMode.AZURE_SECURITY]
                    response = agent.process_command(user_input)
                    console.print(Markdown(response))
                
                elif self.current_mode == AgentMode.AZURE_MCP:
                    client = self.agents[AgentMode.AZURE_MCP]
                    response = client.execute_command(user_input)
                    if response.get("status") == "success":
                        console.print(Markdown(response.get("output", "Command executed successfully")))
                    else:
                        console.print(f"[bold red]Error:[/bold red] {response.get('output', 'Unknown error')}")
                
                elif self.current_mode == AgentMode.SECURITY_ANALYZER:
                    # Convert input to appropriate command for security analyzer
                    agent = self.agents[AgentMode.SECURITY_ANALYZER]
                    if "analyze" in user_input.lower() or "scan" in user_input.lower() or "file" in user_input.lower():
                        # Check for PDF export flag
                        export_pdf = "--pdf" in user_input or "-p" in user_input or "-pdf" in user_input
                        
                        # Extract file path if present
                        # Use a more comprehensive regex to extract the file path
                        file_match = re.search(r"(?:analyze|check|scan)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+(?:--pdf|-pdf|-p))?$", user_input)
                        if file_match:
                            # Get the file path from the input (without flags)
                            file_path = file_match.group(1).strip()
                            
                            # Check if file exists (handles both relative and absolute paths)
                            if os.path.exists(file_path):
                                try:
                                    response = agent.analyze_file(file_path)
                                    self._display_security_results(response)
                                    
                                    # Export as PDF if requested
                                    if export_pdf:
                                        from src.agents.security_analyzer.cli import save_as_pdf
                                        pdf_path = save_as_pdf(response)
                                        console.print(f"[green]Analysis saved as PDF: [bold]{pdf_path}[/bold][/green]")
                                except Exception as e:
                                    error_msg = f"Error analyzing file: {str(e)}"
                                    console.print(f"[bold red]{error_msg}[/bold red]")
                                    response = error_msg
                            else:
                                error_msg = f"File not found: {file_path}"
                                console.print(f"[bold red]{error_msg}[/bold red]")
                                response = error_msg
                        else:
                            console.print("[yellow]Please specify a file to analyze.[/yellow]")
                            console.print("[dim]Example: scan data/test_config.json --pdf[/dim]")
                            response = "Please specify a file to analyze."
                    else:
                        # Use the LLM to generate a response based on security knowledge
                        response = self._get_llm_response_for_security(user_input)
                        console.print(Markdown(response))
                
                elif self.current_mode == AgentMode.COMPLIANCE_CHAT:
                    agent = self.agents[AgentMode.COMPLIANCE_CHAT]
                    response = agent.answer_question(user_input)
                    console.print(Markdown(response))
                
                elif self.current_mode == AgentMode.ARTICLE_SEARCH:
                    agent = self.agents[AgentMode.ARTICLE_SEARCH]
                    response = agent.find_article(user_input)
                    self._display_article_results(response)
                
                else:  # General mode
                    response = self._get_llm_response(user_input)
                    console.print(Markdown(response))
                
                # Add response to history
                self.history.append({"role": "assistant", "content": response if isinstance(response, str) else str(response)})
            
            except Exception as e:
                console.print(f"[bold red]Error processing command:[/bold red] {str(e)}")
                # Try to recover by falling back to general mode
                console.print("[yellow]Falling back to general mode...[/yellow]")
                self.current_mode = AgentMode.GENERAL
    
    def _get_llm_response(self, user_input: str) -> str:
        """Get a response from the LLM for general queries"""
        system_prompt = """
        You are an expert Cloud Security Assistant, specialized in AWS security, compliance, 
        and security analysis. You provide concise, helpful answers related to cloud security 
        topics. If the question is outside your knowledge domain, politely inform the user
        that you can best help with cloud security related questions.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error getting response: {str(e)}"
    
    def _get_llm_response_for_security(self, user_input: str) -> str:
        """Get a response from the LLM for security analyzer related queries"""
        system_prompt = """
        You are an expert in security poisoning analysis. You specialize in detecting malicious 
        tampering in security configurations and compliance benchmarks. Answer questions related
        to security poisoning, configuration tampering, compliance manipulation, and related topics.
        Be specific and detailed in your security advice.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error getting response: {str(e)}"
    
    def _display_security_results(self, results: Dict):
        """Display security analyzer results"""
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
        }.get(risk_level.lower(), "blue")
        
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
    
    def _display_article_results(self, results: Dict):
        """Display article search results"""
        if results["found"]:
            console.print(f"\n[bold green]Found results for:[/bold green] {results['query']}\n")
            
            for i, result in enumerate(results["results"], 1):
                console.print(Panel(
                    f"[bold cyan]{result['title']}[/bold cyan]\n"
                    f"{result['snippet']}\n\n"
                    f"[link={result['link']}]{result['link']}[/link]",
                    title=f"Result {i}",
                    border_style="blue"
                ))
        else:
            console.print(f"\n[bold yellow]No results found for:[/bold yellow] {results['query']}")
            if results.get("suggestion"):
                console.print(f"[yellow]Suggestion:[/yellow] {results['suggestion']}")
    
    def _display_help(self):
        """Display help information"""
        help_table = Table(title="Cloud Security Assistant Commands", box=box.ROUNDED)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="green")
        
        help_table.add_row("switch to aws", "Switch to AWS Security Agent mode")
        help_table.add_row("switch to aws mcp", "Switch to AWS MCP (Model Context Protocol) mode")
        help_table.add_row("switch to gcp", "Switch to Google Cloud Security Agent mode")
        help_table.add_row("switch to gcp mcp", "Switch to GCP MCP (gcloud CLI) mode")
        help_table.add_row("switch to azure", "Switch to Azure Security Agent mode")
        help_table.add_row("switch to azure mcp", "Switch to Azure MCP (az CLI) mode")
        help_table.add_row("switch to security", "Switch to Security Analyzer mode")
        help_table.add_row("switch to compliance", "Switch to Compliance Chat mode")
        help_table.add_row("switch to article", "Switch to Article Search mode")
        help_table.add_row("switch to general", "Switch to General Assistant mode")
        help_table.add_row("clear / cls", "Clear the screen")
        help_table.add_row("help / ?", "Display this help information")
        help_table.add_row("exit / quit", "Exit the application")
        
        console.print(help_table)
        
        # Display current mode
        console.print(f"\n[bold blue]Current mode:[/bold blue] {self.current_mode}")
        
        # Display mode-specific help
        if self.current_mode == AgentMode.GCP_SECURITY:
            console.print("\n[bold]GCP Security Commands:[/bold]")
            console.print("- Ask about IAM security configuration")
            console.print("  Example: [dim]Check my IAM security[/dim]")
            console.print("- Ask about Cloud Storage security")
            console.print("  Example: [dim]Analyze my Cloud Storage buckets[/dim]")
            console.print("- Ask about Compute Engine security")
            console.print("  Example: [dim]Review my Compute Engine instances[/dim]")
            console.print("- Ask about networking security")
            console.print("  Example: [dim]Check my VPC configuration[/dim]")
        elif self.current_mode == AgentMode.GCP_MCP:
            console.print("\n[bold]GCP MCP Commands:[/bold]")
            console.print("- Execute gcloud commands directly")
            console.print("  Example: [dim]gcloud compute instances list[/dim]")
            console.print("- Use natural language for gcloud commands")
            console.print("  Example: [dim]list my instances[/dim]")
            console.print("- Pipe commands with Unix utilities")
            console.print("  Example: [dim]gcloud compute instances list | grep running[/dim]")
            console.print("- Type [cyan]info[/cyan] to see current project")
        elif self.current_mode == AgentMode.AWS_MCP:
            console.print("\n[bold]AWS MCP Commands:[/bold]")
            console.print("- Execute aws CLI commands directly")
            console.print("  Example: [dim]aws ec2 describe-instances[/dim]")
            console.print("- Use natural language for aws commands")
            console.print("  Example: [dim]list my instances[/dim]")
            console.print("- Pipe commands with Unix utilities")
            console.print("  Example: [dim]aws ec2 describe-instances | grep running[/dim]")
        elif self.current_mode == AgentMode.AZURE_MCP:
            console.print("\n[bold]Azure MCP Commands:[/bold]")
            console.print("- Execute az CLI commands directly")
            console.print("  Example: [dim]az vm list[/dim]")
            console.print("- Use natural language for az commands")
            console.print("  Example: [dim]list my vms[/dim]")
            console.print("- Pipe commands with Unix utilities")
            console.print("  Example: [dim]az vm list | grep running[/dim]")
        elif self.current_mode == AgentMode.SECURITY_ANALYZER:
            console.print("\n[bold]Security Analyzer Commands:[/bold]")
            console.print("- [cyan]scan <file_path> [--pdf][/cyan]: Analyze a file for security poisoning")
            console.print("  Example: [dim]scan data/test_config.json --pdf[/dim]")
            console.print("- [cyan]analyze <file_path> [--pdf][/cyan]: Alternative command to analyze a file")
            console.print("  Add [cyan]--pdf[/cyan] or [cyan]-p[/cyan] to export analysis as PDF")
        elif self.current_mode == AgentMode.AWS_SECURITY:
            console.print("\n[bold]AWS Security Commands:[/bold]")
            console.print("- Ask any AWS security-related question")
            console.print("- Request recommendations for AWS services")
            console.print("- Get help with AWS security best practices")
        elif self.current_mode == AgentMode.COMPLIANCE_CHAT:
            console.print("\n[bold]Compliance Chat Commands:[/bold]")
            console.print("- Ask questions about compliance standards")
            console.print("- Get guidance on implementing compliance controls")
            console.print("- Learn about regulatory requirements")
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        if os.name == "nt":  # For Windows
            os.system("cls")
        else:  # For Unix/Linux/MacOS
            os.system("clear")


def display_welcome():
    """Display a welcome message when the CLI starts."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Cloud Security Assistant[/bold blue]\n"
        "[dim]Your unified interface for cloud security, compliance, and analysis[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()
    console.print("[dim]Available agents:[/dim]")
    console.print("[dim]- [bold]AWS Security[/bold]: For AWS security questions and commands[/dim]")
    console.print("[dim]- [bold]AWS MCP[/bold]: For direct AWS CLI (aws) command execution[/dim]")
    console.print("[dim]- [bold]GCP Security[/bold]: For Google Cloud Platform security analysis[/dim]")
    console.print("[dim]- [bold]GCP MCP[/bold]: For direct GCP CLI (gcloud/gsutil) command execution[/dim]")
    console.print("[dim]- [bold]Azure Security[/bold]: For Microsoft Azure security analysis[/dim]")
    console.print("[dim]- [bold]Azure MCP[/bold]: For direct Azure CLI (az) command execution[/dim]")
    console.print("[dim]- [bold]Security Analyzer[/bold]: For detecting security poisoning and configuration tampering[/dim]")
    console.print("[dim]- [bold]Compliance Chat[/bold]: For questions about security compliance standards[/dim]")
    console.print("[dim]- [bold]Article Search[/bold]: For finding relevant security articles and publications[/dim]")
    console.print("[dim]- [bold]General[/bold]: For general cloud security questions[/dim]")
    console.print()
    console.print("[dim]Commands:[/dim]")
    console.print("[dim]- Type [bold]'switch to [agent]'[/bold] to change agents[/dim]")
    console.print("[dim]- Type [bold]'help'[/bold] for more information[/dim]")
    console.print("[dim]- Type [bold]'clear'[/bold] or [bold]'cls'[/bold] to clear the screen[/dim]")
    console.print("[dim]- Type [bold]'exit'[/bold] or [bold]'quit'[/bold] to end the session[/dim]")
    console.print()


@app.command()
def export(
    format: str = typer.Option("json", help="Export format: json, csv, html"),
    report_id: str = typer.Option("demo-report", help="Report ID to export"),
    output: str = typer.Option(None, help="Output file path (optional)")
):
    """Export audit report in multiple formats."""
    try:
        from src.audit.exporters import JSONExporter, CSVExporter, HTMLExporter
        
        console.print(f"\n[bold cyan]Exporting Report to {format.upper()}[/bold cyan]")
        
        # Create sample report data
        report_data = {
            "id": report_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "findings": [
                {
                    "id": "FIND-001",
                    "severity": "CRITICAL",
                    "category": "Storage",
                    "title": "Public S3 Bucket",
                    "resource": "my-bucket",
                    "description": "Bucket is publicly accessible"
                },
                {
                    "id": "FIND-002", 
                    "severity": "HIGH",
                    "category": "Security",
                    "title": "Unencrypted EBS",
                    "resource": "vol-12345",
                    "description": "EBS volume not encrypted"
                }
            ],
            "statistics": {
                "total_findings": 2,
                "critical": 1,
                "high": 1,
                "medium": 0
            }
        }
        
        if format.lower() == "json":
            exporter = JSONExporter()
            output_file = output or f"reports/export_{report_id}.json"
            exporter.export_report(report_data, output_file)
            console.print(f"[green]✅ JSON export successful[/green]")
            console.print(f"[dim]File: {output_file}[/dim]")
            
        elif format.lower() == "csv":
            exporter = CSVExporter()
            output_file = output or f"reports/export_{report_id}.csv"
            exporter.export_findings_to_csv(report_data["findings"], output_file)
            console.print(f"[green]✅ CSV export successful[/green]")
            console.print(f"[dim]File: {output_file}[/dim]")
            
        elif format.lower() == "html":
            exporter = HTMLExporter()
            output_file = output or f"reports/export_{report_id}.html"
            exporter.export_email_template(report_data, output_file)
            console.print(f"[green]✅ HTML export successful[/green]")
            console.print(f"[dim]File: {output_file}[/dim]")
            
        else:
            console.print(f"[red]❌ Unknown format: {format}[/red]")
            console.print(f"[dim]Supported formats: json, csv, html[/dim]")
            sys.exit(1)
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def remediate(
    finding_id: str = typer.Option(..., help="Finding ID to remediate"),
    dry_run: bool = typer.Option(True, help="Test without making changes"),
    auto_approve: bool = typer.Option(False, help="Auto-approve without asking")
):
    """Execute remediation playbook for a finding."""
    try:
        from src.remediation import PlaybookExecutor, PlaybookLibrary
        from src.audit.exporters import CSVExporter
        
        console.print("\n[bold cyan]Starting Remediation Workflow[/bold cyan]")
        
        # Load playbooks
        executor = PlaybookExecutor()
        playbooks = PlaybookLibrary.get_all_playbooks()
        
        console.print(f"[dim]Finding ID: {finding_id}[/dim]")
        console.print(f"[dim]Dry-run mode: {dry_run}[/dim]")
        
        # Try to find matching playbook
        matching_playbook = None
        for pb_name, pb in playbooks.items():
            if finding_id.upper() in pb_name:
                matching_playbook = pb
                break
        
        if not matching_playbook:
            # Default to AWS-PUBLIC-S3 for demo
            matching_playbook = playbooks.get("AWS-PUBLIC-S3")
            console.print(f"[yellow]No exact match found, using {matching_playbook.name}[/yellow]")
        
        # Execute playbook
        execution = executor.execute_playbook(
            playbook=matching_playbook,
            finding_data={"id": finding_id, "resource": "test-resource"},
            initiated_by=os.getenv("USER", "system"),
            dry_run=dry_run
        )
        
        console.print(f"\n[bold green]✅ Execution Created[/bold green]")
        console.print(f"[dim]Execution ID: {execution.execution_id}[/dim]")
        console.print(f"[dim]Status: {execution.status.value}[/dim]")
        console.print(f"[dim]Playbook: {execution.playbook_name}[/dim]")
        console.print(f"[dim]Actions: {len(execution.actions)}[/dim]")
        
        # Show approval workflow
        if execution.approval_required and not dry_run:
            if auto_approve:
                executor.approve_execution(execution.execution_id, "auto-system")
                console.print(f"[green]✅ Auto-approved[/green]")
            else:
                console.print(f"\n[yellow]⏳ Waiting for approval...[/yellow]")
                console.print(f"[dim]To approve, run: remediate {finding_id} --auto-approve[/dim]")
        
        console.print("\n[bold green]Remediation workflow ready[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def playbook_list(
    severity: str = typer.Option(None, help="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)")
):
    """List all available remediation playbooks."""
    try:
        from src.remediation import PlaybookLibrary
        
        console.print("\n[bold cyan]Available Remediation Playbooks[/bold cyan]\n")
        
        playbooks = PlaybookLibrary.get_all_playbooks()
        
        # Create table
        table = Table(box=box.ROUNDED, title="Playbook Library")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Severity", style="yellow")
        table.add_column("Description", style="green")
        table.add_column("Actions", style="dim")
        
        severity_colors = {
            "CRITICAL": "[bold red]CRITICAL[/bold red]",
            "HIGH": "[bold orange]HIGH[/bold orange]",
            "MEDIUM": "[bold yellow]MEDIUM[/bold yellow]",
            "LOW": "[bold green]LOW[/bold green]"
        }
        
        # Filter by severity if specified
        for pb_name, pb in sorted(playbooks.items()):
            if severity and pb.severity != severity.upper():
                continue
            
            severity_display = severity_colors.get(pb.severity, pb.severity)
            
            table.add_row(
                pb.name,
                pb.category,
                severity_display,
                pb.description[:40] + "..." if len(pb.description) > 40 else pb.description,
                str(len(pb.actions))
            )
        
        console.print(table)
        
        # Show summary
        total = len(playbooks)
        critical_count = sum(1 for p in playbooks.values() if p.severity == "CRITICAL")
        high_count = sum(1 for p in playbooks.values() if p.severity == "HIGH")
        
        console.print(f"\n[dim]Total Playbooks: {total}[/dim]")
        console.print(f"[bold red]CRITICAL: {critical_count}[/bold red] | [bold orange]HIGH: {high_count}[/bold orange]")
        console.print(f"\n[dim]Usage: remediate --finding-id <finding-id> --dry-run[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def main():
    """Run the main CLI application."""
    # Load environment variables
    load_dotenv()
    
    # Set Google application credentials if available
    if os.path.exists("config/vertex.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"
    
    # Display welcome message
    display_welcome()
    
    # Initialize the assistant
    assistant = CloudAssistant()
    
    # Main loop
    while True:
        # Get user input with appropriate prompt based on mode
        mode_colors = {
            AgentMode.AWS_SECURITY: "cyan",
            AgentMode.AWS_MCP: "bright_cyan",
            AgentMode.GCP_SECURITY: "magenta",
            AgentMode.GCP_MCP: "bright_magenta",
            AgentMode.AZURE_SECURITY: "bright_blue",
            AgentMode.AZURE_MCP: "blue",
            AgentMode.SECURITY_ANALYZER: "red",
            AgentMode.COMPLIANCE_CHAT: "green",
            AgentMode.ARTICLE_SEARCH: "yellow",
            AgentMode.GENERAL: "blue"
        }
        
        mode_color = mode_colors.get(assistant.current_mode, "blue")
        prompt_text = f"[bold {mode_color}]{assistant.current_mode}>[/bold {mode_color}]"
        
        user_input = Prompt.ask(f"\n{prompt_text}")
        
        # Process the command
        assistant.process_command(user_input)


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! Stay secure![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
