# Cloud Compliance Chatbot

This is an interactive CLI-based cloud compliance chatbot that uses:

- RAG (Retrieval-Augmented Generation) with FAISS vector database
- Google's Gemini LLM
- SERPAPI for cross-verification of information
- Rich library for beautiful CLI output

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
- `SERPAPI_API_KEY`: Get from [SerpApi](https://serpapi.com/)
- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google credentials JSON file

## Usage

Run the chatbot:

```bash
python -m src.agents.compliance_bot
```

Or run with custom options:

```bash
python -m src.agents.compliance_bot --no-search  # Disable SERPAPI search
python -m src.agents.compliance_bot -e /path/to/embeddings  # Custom embeddings path
```

## Features

- **Retrieval**: Finds relevant documents from the vector database
- **Cross-verification**: Uses SERPAPI to verify information from the web
- **LLM Generation**: Uses Gemini to generate accurate responses
- **Beautiful CLI**: Rich text formatting and interactive elements

## Example Questions

- "What are the CIS benchmarks for AWS S3?"
- "How should I configure RDS for compliance?"
- "What are the best practices for IAM security in AWS?"
- "Explain the CIS controls for EC2 instances"
