# Cloud Security Assistant - Complete Project Walkthrough

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Key Features](#key-features)
6. [Workflow](#workflow)
7. [Getting Started](#getting-started)
8. [Usage Examples](#usage-examples)

---

## Project Overview

The **Cloud Security Assistant** is a unified, AI-powered security platform that provides:
- Multi-agent architecture for comprehensive cloud security analysis
- Natural language understanding through Gemini LLM
- Seamless agent switching through a single CLI interface
- Real-time AWS security assessment
- Compliance verification against industry standards
- Security vulnerability detection in configurations
- Web-based research and article discovery

### Key Innovation
The project introduces an **agent-switching CLI paradigm** - a revolutionary approach where multiple specialized security tools are accessible through a single natural language interface, eliminating the need to learn different command syntaxes for different tools.

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────┐
│         Unified Cloud Security CLI (main_cli.py)        │
│                                                           │
│  - Natural Language Input Processing                    │
│  - Intent Detection & Agent Routing                     │
│  - Conversation History Management                      │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐   ┌──────────┐   ┌──────────────┐
    │ Agent  │   │ Security │   │  Compliance  │
    │ Pool   │   │Analyzer  │   │    Chat      │
    │        │   │          │   │              │
    │ AWS    │   │ Config   │   │ Benchmarks   │
    │ AWS MCP│   │ Analysis │   │ Knowledge    │
    │Article │   │ Poisoning│   │ Base         │
    │Search  │   │Detection │   │              │
    └────────┘   └──────────┘   └──────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │    Shared Services           │
        │                              │
        │ - Gemini LLM (2.5 Pro)       │
        │ - Vector Store (FAISS)       │
        │ - Web Search (SERPAPI)       │
        │ - Report Generation          │
        └──────────────────────────────┘
```

### Agent Orchestration
The system uses a **custom state-based routing mechanism** that:
1. Detects user intent through pattern matching and NLP
2. Routes queries to specialized agents based on context
3. Manages agent lifecycle (lazy loading, state preservation)
4. Maintains conversation history across agent transitions

---

## Directory Structure

```
cloudsec-agent/
│
├── main_cli.py                          # 🎯 Primary entry point - Unified CLI
├── aws_security_agent.py                # AWS Security Agent implementation
├── aws_security_agent_og.py             # Original AWS MCP implementation
├── quick_security_agent.py              # Quick assessment tool
│
├── src/
│   ├── agents/
│   │   ├── compliance_bot/              # 📋 Compliance verification agent
│   │   │   ├── agent.py                 # Main compliance agent
│   │   │   ├── compliance_assistant.py  # Compliance query processor
│   │   │   ├── vector_store.py          # FAISS vector indexing
│   │   │   ├── web_search.py            # Article search functionality
│   │   │   ├── llm.py                   # LLM configuration
│   │   │   ├── retriever.py             # Document retrieval
│   │   │   └── search.py                # Search verification
│   │   │
│   │   └── security_analyzer/           # 🛡️ Security analysis agent
│   │       ├── agent.py                 # Main analyzer agent
│   │       ├── analyzer.py              # Analysis logic
│   │       ├── extractor.py             # Config extraction
│   │       ├── cli.py                   # CLI interface
│   │       └── patterns.py              # Security patterns
│   │
│   ├── aws_mcp/                         # AWS Multi-Cloud Platform
│   │   └── client.py                    # AWS service client
│   │
│   └── data_pipeline/                   # Data processing utilities
│       └── embeddings/                  # Vector embeddings
│
├── data/
│   ├── raw/                             # Raw compliance PDFs
│   │   ├── CIS_AWS_Foundations_Benchmark_v5.0.0.pdf
│   │   ├── CIS_AWS_Database_Services_Benchmark_v1.0.0.pdf
│   │   └── ...
│   ├── processed/                       # Processed data
│   └── embeddings/
│       └── index/                       # FAISS vector index
│           ├── index.faiss              # Vector index
│           └── documents.json           # Document metadata
│
├── reports/                             # Generated security reports
│   └── *.pdf                            # Security analysis PDFs
│
├── config/
│   └── vertex.json                      # Google Cloud credentials
│
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables
└── README.md                            # Project documentation
```

---

## Core Components

### 1. 🎯 Unified CLI (`main_cli.py`)

**Purpose**: Central command hub for all agents

**Key Classes**:
- `CloudAssistant`: Main orchestrator class
- `AgentMode`: Enum for different agent modes

**Key Methods**:
- `_detect_agent_mode()`: Determines which agent should handle input
- `_load_agent()`: Lazy-loads agents on demand
- `process_command()`: Routes commands to appropriate agent
- `_process_with_current_agent()`: Executes agent-specific processing

**Features**:
- Intent-based routing with pattern matching
- Conversation history tracking
- Error recovery and fallback mechanisms
- Natural language mode switching

---

### 2. ☁️ AWS Security Agent (`aws_security_agent.py`)

**Purpose**: Analyzes AWS environment security posture

**Key Capabilities**:
- AWS CLI integration
- IAM, S3, EC2 security assessment
- Real-time configuration checking
- Security recommendations based on AWS best practices
- Natural language query interpretation

**Example Queries**:
- "Check my S3 bucket security"
- "List EC2 instances with public IP"
- "Show IAM users without MFA"

---

### 3. 🛡️ Security Analyzer (`src/agents/security_analyzer/`)

**Purpose**: Detects security poisoning and tampering in configurations

**Components**:
- `analyzer.py`: Core analysis logic for identifying security issues
- `extractor.py`: Configuration parsing and extraction
- `patterns.py`: Security anti-patterns and vulnerability signatures
- `cli.py`: Command-line interface with PDF export

**Detection Categories**:
- Excessive permissions
- Encryption weaknesses
- Hardcoded credentials
- Compliance tampering
- Configuration poisoning

**Output**: PDF reports with detailed findings and remediation suggestions

---

### 4. 📋 Compliance Chat (`src/agents/compliance_bot/`)

**Purpose**: Provides compliance guidance using security framework knowledge

**Key Components**:
- `agent.py`: Main compliance agent
- `vector_store.py`: FAISS-based document indexing
- `retriever.py`: Document retrieval with similarity search
- `web_search.py`: Article and publication search
- `llm.py`: LLM configuration and response generation

**Workflow**:
1. User asks compliance question
2. Query is vectorized using Gemini embeddings
3. FAISS retrieves relevant document chunks
4. LLM generates answer with citations
5. References to source documents provided

---

### 5. 📚 Article Search (`src/agents/compliance_bot/web_search.py`)

**Purpose**: Finds security articles and publications

**Features**:
- Natural language article search
- Author-specific searches
- Topic extraction and ranking
- Source attribution
- Content summarization

---

## Key Features

### 🔄 Agent Switching
Users can seamlessly transition between agents:
```
general> switch to aws-security
Switched from general to aws-security mode

aws-security> switch to compliance-chat
Switched from aws-security to compliance-chat mode
```

### 🧠 Natural Language Understanding
All agents accept natural language queries:
- AWS Agent: "What's the status of my S3 buckets?"
- Compliance: "What are the requirements for IAM encryption?"
- Analyzer: "Check this config file for vulnerabilities"
- Article Search: "Find posts about AWS security"

### 📊 Rich Terminal Output
- Colored tables and panels
- Progress indicators
- Formatted code highlighting
- Interactive prompts

### 🔐 Security-First Design
- Validated command execution
- No credential exposure
- Secure configuration handling
- Compliance-aware recommendations

---

## Workflow

### Level 1: High-Level Flow

```
1. START
   ↓
2. USER INPUT
   ↓
3. INTENT DETECTION
   ↓
4. AGENT SELECTION & LOADING
   ↓
5. QUERY PROCESSING
   ↓
6. RESULT GENERATION
   ↓
7. OUTPUT FORMATTING & DISPLAY
   ↓
8. HISTORY UPDATE
   ↓
9. WAIT FOR NEXT INPUT or EXIT
```

### Level 2: Detailed Processing

#### Step 3: Intent Detection
- Pattern matching for explicit mode switches
- Keyword detection for implicit intents
- Context-aware routing based on conversation history

#### Step 4: Agent Loading
- Check if agent already loaded
- Show loading spinner
- Initialize agent with required services
- Update current mode

#### Step 5: Query Processing
Varies by agent:
- **AWS Agent**: Parse natural language → AWS CLI command → Execute → Analyze
- **Compliance**: Vectorize query → Search embeddings → Retrieve docs → Generate answer
- **Analyzer**: Parse config → Extract patterns → Check against rules → Generate report
- **Article Search**: Extract entities → Web search → Rank results → Format output

#### Step 7: Output Formatting
- Agent-specific formatting (tables, panels, markdown)
- Rich terminal styling
- Error handling and user-friendly messages

---

## Getting Started

### Prerequisites
- Python 3.8+
- AWS CLI configured (for AWS Agent)
- Google API key (for Gemini LLM)
- SERPAPI key (for Article Search)

### Installation

1. **Clone the repository**:
```bash
cd /home/vboxuser/projects/cloudsec-agent
```

2. **Activate virtual environment**:
```bash
source cloudagent/bin/activate
```

3. **Set environment variables**:
```bash
export GOOGLE_API_KEY="your_google_api_key"
export SERPAPI_API_KEY="your_serpapi_key"
```

4. **Verify requirements are installed**:
```bash
pip install -r requirements.txt
```

### Launch the Application

**Main Unified CLI**:
```bash
python main_cli.py
```

**Standalone Agents**:
```bash
# AWS Security Agent
python aws_security_agent.py

# Compliance Chat
python -m src.agents.compliance_bot

# Security Analyzer CLI
python security_analyzer_cli.py

# Article Search
python article_search.py
```

---

## Usage Examples

### Example 1: AWS Security Analysis

```
general> switch to aws-security
Switched from general to aws-security mode

aws-security> List all S3 buckets and their encryption status
[Processing...]

Found 5 S3 buckets:
┌──────────────────────────┬────────────┐
│ Bucket Name              │ Encryption │
├──────────────────────────┼────────────┤
│ my-app-data              │ Enabled    │
│ backup-bucket            │ Disabled   │
│ logs-archive             │ Enabled    │
└──────────────────────────┴────────────┘

⚠️  WARNING: backup-bucket has encryption disabled
```

### Example 2: Compliance Verification

```
compliance-chat> What are the CIS AWS requirements for S3 bucket security?
[Processing...]

Based on CIS AWS Foundations Benchmark v5.0.0:

## S3 Bucket Security Requirements

### Encryption
- Enable server-side encryption on all S3 buckets
- Use AWS KMS for sensitive data
- Enable encryption by default

### Access Control
- Block public access at account level
- Use bucket policies for least privilege
- Enable versioning on critical buckets

**References:**
1. CIS AWS Foundations Benchmark v5.0.0
2. AWS Security Best Practices
```

### Example 3: Configuration Analysis

```
security-analyzer> scan data/test_config.json --pdf
[Analyzing configuration...]

╭─────────────────────────────────────╮
│ Security Analysis: CRITICAL Risk    │
│ test_config.json                    │
╰─────────────────────────────────────╯

Poisoning detected with 7 issues found.

┌─────────────────────────────────────────┐
│ Critical Issues                         │
├─────────────────────────────────────────┤
│ • Hardcoded credentials found           │
│ • Encryption disabled                   │
│ • Excessive permissions granted         │
└─────────────────────────────────────────┘

Analysis saved as PDF: reports/test_config_20251130.pdf
```

### Example 4: Article Search

```
article-search> Find articles about AWS S3 bucket security by Maciej Pocwierz
[Searching the web...]

Found 3 results for: Maciej Pocwierz AWS S3 bucket security

Result 1: Abandoned AWS S3 Buckets: The Hidden Supply Chain Risk
- Found by: @watchtowr on Twitter
- Published: 2024
- https://www.example.com/article

Result 2: S3 Bucket Naming Collisions: A Real-World Attack Vector
- Published: 2023
- https://www.example.com/article2
```

---

## Technology Stack

### Languages & Frameworks
- **Python 3.8+**: Primary language
- **Typer**: CLI framework
- **Rich**: Terminal UI

### AI & LLM
- **Google Gemini 2.5 Pro**: Language model
- **LangChain**: LLM orchestration
- **Google Embeddings 002**: Document embedding

### Data & Search
- **FAISS**: Vector similarity search
- **PyPDF2**: PDF processing
- **SERPAPI**: Web search integration

### AWS Integration
- **Boto3**: AWS SDK
- **AWS CLI**: Direct command execution

### Utilities
- **ReportLab**: PDF report generation
- **python-dotenv**: Configuration management
- **NumPy**: Numerical operations

---

## Configuration

### Environment Variables (`.env`)
```bash
# Google APIs
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-2.5-pro

# Search
SERPAPI_API_KEY=your_serpapi_key

# AWS (optional, uses AWS CLI config if not set)
AWS_REGION=us-east-1

# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=config/vertex.json
```

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `switch to aws-security` | Switch to AWS agent |
| `switch to compliance-chat` | Switch to compliance agent |
| `switch to security-analyzer` | Switch to analyzer agent |
| `switch to article-search` | Switch to article search agent |
| `help` or `?` | Show available commands |
| `clear` or `cls` | Clear screen |
| `exit` or `quit` | Exit application |

---

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file exists with API keys
   - Verify environment variables are set: `echo $GOOGLE_API_KEY`

2. **Agent Not Initializing**
   - Check API key format
   - Verify internet connection
   - Review logs for error messages

3. **AWS Commands Failing**
   - Run `aws configure` to set up AWS credentials
   - Verify IAM user has required permissions

4. **Vector Search Issues**
   - Rebuild embeddings: `python main.py`
   - Check FAISS index exists in `data/embeddings/index/`

---

## Future Enhancements

- Google Cloud security agent
- Azure security agent
- Multi-cloud compliance dashboard
- Real-time security alerts
- Integration with SIEM systems
- Machine learning-based anomaly detection

---

## Support & Contribution

For issues, questions, or contributions:
- Check the main README.md
- Review UNIFIED_CLI_README.md for CLI details
- Examine existing issues in the repository

---

**Last Updated**: November 30, 2025
**Project Version**: 1.0
**Maintained By**: Security Team
