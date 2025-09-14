# main.py
"""
AWS Compliance Document Processor

This script processes AWS security benchmark PDFs from data/raw directory
into embeddings that can be used for compliance-related searches and 
knowledge retrieval in the RAG system. While not directly used by the 
aws_mcp_og implementation, this supports other functionality like compliance checks.
"""

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/vertex.json"

from src.data_pipeline.pdf_loader import load_pdfs
from src.data_pipeline.text_cleaner import chunk_documents
from src.data_pipeline.embedder import build_vectorstore

def main():
    print("📥 Loading PDFs...")
    docs = load_pdfs("data/raw")
    
    print("✂️ Splitting into chunks...")
    chunks = chunk_documents(docs)
    
    print("🧠 Converting to embeddings + saving...")
    vectorstore = build_vectorstore(chunks, persist_path="data/embeddings/index")
    
    print("✅ Done! Embeddings stored in ./data/embeddings/")

if __name__ == "__main__":
    main()
