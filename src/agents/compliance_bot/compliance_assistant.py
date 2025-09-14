#!/usr/bin/env python3
"""
Compliance Assistant class for the unified CLI
"""

import os
from typing import Dict, Any, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from .agent import CloudComplianceAgent
from .web_search import WebSearcher


class ComplianceAssistant:
    """
    Compliance Assistant class that combines the capabilities of
    CloudComplianceAgent and WebSearcher for the unified CLI.
    """
    
    def __init__(self):
        """Initialize the Compliance Assistant with required components."""
        self.compliance_agent = CloudComplianceAgent()
        self.web_searcher = WebSearcher()
    
    def answer_question(self, query: str) -> str:
        """
        Answer a compliance-related question.
        
        Args:
            query: The user's question or query
            
        Returns:
            A formatted response string
        """
        # Determine if this is a web search query or a compliance question
        if self._is_article_search_query(query):
            results = self.web_searcher.find_article(query)
            if results["found"]:
                return self._format_article_results(results)
            else:
                return f"No articles found matching your query: '{query}'\n\nTry using different keywords or be more specific about the author or topic."
        
        # Otherwise treat as a compliance question
        result = self.compliance_agent.process_query(query)
        return result["response"]
    
    def _is_article_search_query(self, query: str) -> bool:
        """
        Determine if the query is asking about articles, blog posts, or publications.
        
        Args:
            query: The user's query
            
        Returns:
            True if this appears to be an article search query
        """
        article_keywords = [
            "article", "blog", "post", "publication", "wrote", 
            "author", "published", "write", "written"
        ]
        
        query_lower = query.lower()
        for keyword in article_keywords:
            if keyword in query_lower:
                return True
                
        return False
    
    def _format_article_results(self, results: Dict) -> str:
        """
        Format article search results into a readable string.
        
        Args:
            results: The results dictionary from WebSearcher
            
        Returns:
            A formatted string with article information
        """
        output = f"# Article Search Results for: {results['query']}\n\n"
        
        for i, result in enumerate(results["results"], 1):
            output += f"## {i}. {result['title']}\n\n"
            output += f"{result['snippet']}\n\n"
            output += f"[Read more]({result['link']})\n\n"
            output += "---\n\n"
        
        if not results["results"]:
            output += "No articles found matching your query.\n"
        
        return output
