# src/agents/compliance_bot/llm.py
import os
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

class ComplianceLLM:
    """Handles interactions with the Gemini LLM for the compliance bot."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini LLM.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            # We'll use the application default credentials if no API key is provided
            pass
        else:
            genai.configure(api_key=self.api_key)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.2
        )
    
    def generate_response(self, 
                          query: str, 
                          retrieved_docs: List[Dict[str, Any]], 
                          search_results: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a response using Gemini LLM.
        
        Args:
            query: The user's query
            retrieved_docs: Documents retrieved from the vector store
            search_results: Optional search results for cross-verification
            
        Returns:
            The generated response
        """
        # Prepare system prompt
        system_prompt = """You are a Cloud Security Compliance Expert assistant. Your purpose is to help users understand cloud security 
compliance standards, best practices, and configurations.

You have access to information from various compliance documents including CIS benchmarks for AWS services.

When responding to questions:
1. Be precise and accurate about compliance requirements
2. Cite specific compliance standards and benchmarks when applicable
3. Explain the security rationale behind compliance requirements
4. Suggest practical implementation steps when relevant
5. Note if there are conflicting requirements across different standards

Focus on being helpful, educational, and providing actionable advice."""
        
        # Prepare context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}\nSource: {doc.get('metadata', {}).get('source', 'Unknown')}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # Add search results if available
        search_context = ""
        if search_results:
            search_context = "\n\n".join([
                f"Search Result {i+1}:\nTitle: {result.get('title', '')}\nSnippet: {result.get('snippet', '')}\nURL: {result.get('link', '')}"
                for i, result in enumerate(search_results)
            ])
        
        # Create context message
        context_content = f"""Context from compliance documents:
{context}

{("Online search results for cross-verification:\n" + search_context) if search_results else ""}

User Question: {query}

Please provide a comprehensive, accurate response addressing the user's question about cloud compliance."""

        # Create messages using the proper LangChain message types
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context_content)
        ]
        
        # Generate response
        response = self.llm.invoke(messages)
        return response.content
