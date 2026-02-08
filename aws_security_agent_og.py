#!/usr/bin/env python3
"""
AWS Security Agent with Gemini LLM and MCP Integration

This agent uses the aws_mcp_og implementation for secure AWS CLI command execution
with natural language understanding capabilities.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Union

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import interpret_natural_language function
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.aws_mcp_og.tools import interpret_natural_language

# Load environment variables
load_dotenv()

app = typer.Typer(help="AWS Security Agent with Gemini LLM and MCP Integration")
console = Console()

# System prompt for the LLM agent
SYSTEM_PROMPT = """You are AWSSecurityAssistant, an AI agent specialized in AWS security analysis and auditing.

Your capabilities:
1. Execute AWS CLI commands to inspect AWS resources and configurations
2. Analyze security configurations against best practices
3. Identify security vulnerabilities and compliance issues
4. Suggest remediation steps for security findings
5. Explain AWS security concepts in simple terms

When executing commands:
- Always explain what the command does before showing results
- Format outputs in a readable way (tables, JSON, etc.)
- Highlight any security issues or suspicious findings
- Suggest follow-up commands for deeper investigation
- Provide context and explain the security implications

Important restrictions:
- Never execute potentially destructive commands (delete, remove, terminate)
- Always prioritize security and compliance best practices
- When unsure about a command, ask for clarification
- Do not make assumptions about security configurations

You can respond to natural language instructions and translate them to AWS CLI commands.
Always focus on helping the user improve their AWS security posture."""

class AWSSecurityAgent:
    """AWS Security Agent using MCP and Gemini LLM."""
    
    def __init__(self, aws_profile=None, aws_region=None):
        """
        Initialize the AWS Security Agent.
        
        Args:
            aws_profile: AWS profile to use
            aws_region: AWS region to use
        """
        self.aws_profile = aws_profile
        self.aws_region = aws_region
        self.conversation_history = []
        
        # Initialize system message
        self.conversation_history.append(SystemMessage(content=SYSTEM_PROMPT))
        
        # Initialize Gemini LLM
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=api_key
            )
        else:
            console.print(
                Panel(
                    "[bold red]Error: GOOGLE_API_KEY environment variable not found.[/]\n"
                    "Please set this variable to use Gemini LLM capabilities.",
                    title="Configuration Error"
                )
            )
            sys.exit(1)
    
    def handle_query(self, query: str) -> None:
        """
        Process a user query using LLM and execute AWS commands if needed.
        
        Args:
            query: User input query
        """
        # Add user message to conversation
        self.conversation_history.append(HumanMessage(content=query))
        
        # Get LLM response
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Thinking...[/]"),
            transient=True,
        ) as progress:
            progress.start()
            try:
                response = self.llm.invoke(self.conversation_history)
                self.conversation_history.append(response)
            except Exception as e:
                progress.stop()
                console.print(
                    Panel(
                        f"[bold red]Error from Gemini LLM: {e}[/]",
                        title="AI Error"
                    )
                )
                return
        
        # Display AI response
        console.print(Markdown(response.content))
        
        # Check if we need to execute an AWS command
        aws_commands = self._extract_aws_commands(response.content)
        
        if aws_commands:
            self._execute_aws_commands(aws_commands)
    
    def _extract_aws_commands(self, text: str) -> List[str]:
        """
        Extract AWS CLI commands from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            List of AWS CLI commands to execute
        """
        commands = []
        
        # Look for code blocks with aws commands
        import re
        code_blocks = re.findall(r'```(?:bash|shell|sh)?\n(.*?)\n```', text, re.DOTALL)
        
        for block in code_blocks:
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('aws '):
                    commands.append(line)
        
        return commands
    
    def _execute_aws_commands(self, commands: List[str]) -> None:
        """
        Execute AWS CLI commands and update conversation with results.
        
        Args:
            commands: List of AWS CLI commands to execute
        """
        results = []
        
        for command in commands:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Executing: {command}[/]"),
                transient=True,
            ) as progress:
                progress.start()
                try:
                    # Execute command using subprocess
                    import subprocess
                    
                    # Set environment variables if profile/region specified
                    env = os.environ.copy()
                    if self.aws_profile:
                        env['AWS_PROFILE'] = self.aws_profile
                    if self.aws_region:
                        env['AWS_DEFAULT_REGION'] = self.aws_region
                    
                    # Execute command
                    result = subprocess.run(
                        command, 
                        shell=True,
                        capture_output=True,
                        text=True,
                        env=env
                    )
                    
                    if result.returncode == 0:
                        # Try to parse JSON output
                        try:
                            output_json = json.loads(result.stdout)
                            output_str = json.dumps(output_json, indent=2)
                            console.print(Syntax(output_str, "json", theme="monokai"))
                            results.append(f"Command: {command}\nStatus: Success\n```json\n{output_str}\n```")
                        except json.JSONDecodeError:
                            console.print(result.stdout)
                            results.append(f"Command: {command}\nStatus: Success\n```\n{result.stdout}\n```")
                    else:
                        # Format error
                        console.print(f"[bold red]Error:[/] {result.stderr}")
                        results.append(f"Command: {command}\nStatus: Error\n```\n{result.stderr}\n```")
                        
                except Exception as e:
                    progress.stop()
                    console.print(f"[bold red]Error executing command:[/] {e}")
                    results.append(f"Command: {command}\nStatus: Error\n```\n{str(e)}\n```")
        
        # Add command results to conversation history
        if results:
            results_message = "Here are the results of the AWS commands I executed:\n\n" + "\n\n".join(results)
            self.conversation_history.append(HumanMessage(content=results_message))
            
            # Get LLM to analyze the results
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold green]Analyzing results...[/]"),
                transient=True,
            ) as progress:
                progress.start()
                try:
                    analysis = self.llm.invoke(self.conversation_history)
                    self.conversation_history.append(analysis)
                    
                    # Display analysis
                    console.print("\n[bold blue]Analysis:[/]")
                    console.print(Markdown(analysis.content))
                except Exception as e:
                    progress.stop()
                    console.print(
                        Panel(
                            f"[bold red]Error analyzing results: {e}[/]",
                            title="AI Error"
                        )
                    )

    def run_command(self, command: str) -> None:
        """
        Execute an AWS CLI command or natural language query.
        
        Args:
            command: AWS CLI command or natural language query
        """
        # Check if command is a direct AWS CLI command
        if command.startswith('aws '):
            # Execute AWS command directly
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Executing: {command}[/]"),
                transient=True,
            ) as progress:
                progress.start()
                try:
                    # Execute command using subprocess
                    import subprocess
                    
                    # Set environment variables if profile/region specified
                    env = os.environ.copy()
                    if self.aws_profile:
                        env['AWS_PROFILE'] = self.aws_profile
                    if self.aws_region:
                        env['AWS_DEFAULT_REGION'] = self.aws_region
                    
                    # Execute command
                    result = subprocess.run(
                        command, 
                        shell=True,
                        capture_output=True,
                        text=True,
                        env=env
                    )
                    
                    if result.returncode == 0:
                        # Try to parse JSON output
                        try:
                            output_json = json.loads(result.stdout)
                            output_str = json.dumps(output_json, indent=2)
                            console.print(Syntax(output_str, "json", theme="monokai"))
                        except json.JSONDecodeError:
                            console.print(result.stdout)
                    else:
                        # Format error
                        console.print(f"[bold red]Error:[/] {result.stderr}")
                        
                except Exception as e:
                    progress.stop()
                    console.print(f"[bold red]Error executing command:[/] {e}")
        else:
            # Try to interpret as natural language
            aws_cmd = interpret_natural_language(command)
            
            if aws_cmd:
                console.print(f"[dim]Interpreted as: [/][blue]{aws_cmd}[/]")
                self.run_command(aws_cmd)
            else:
                # Use LLM to handle complex queries
                self.handle_query(command)

    def run_interactive(self) -> None:
        """Run the agent in interactive mode."""
        console.print(
            Panel(
                "[bold green]AWS Security Agent with Gemini LLM[/]\n\n"
                "Type your security questions or AWS commands.\n"
                "Type 'exit' to quit.",
                title="🔒 AWS Security Assistant",
                border_style="blue"
            )
        )
        
        while True:
            try:
                query = Prompt.ask("\n[bold blue]>[/]")
                if query.lower() in ('exit', 'quit', 'q'):
                    break
                    
                self.run_command(query)
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/] {e}")
        
        console.print("[bold blue]Goodbye![/]")

@app.command()
def run(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile to use"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region to use")
):
    """Run the AWS Security Agent in interactive mode."""
    agent = AWSSecurityAgent(aws_profile=profile, aws_region=region)
    agent.run_interactive()

if __name__ == "__main__":
    app()
