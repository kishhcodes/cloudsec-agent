# src/agents/compliance_bot/search.py
import os
from serpapi import GoogleSearch
from typing import List, Dict, Any, Optional

class SearchVerifier:
    """Uses SERPAPI to cross-verify compliance information."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the search verifier.
        
        Args:
            api_key: SERPAPI API key (defaults to SERPAPI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI API key not found. Please set SERPAPI_API_KEY environment variable.")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information to cross-verify.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        # Add cloud security compliance keywords to the query
        enhanced_query = f"cloud security compliance {query}"
        
        search_params = {
            "engine": "google",
            "q": enhanced_query,
            "api_key": self.api_key,
            "num": num_results,
        }
        
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"SERPAPI error: {results['error']}")
            
        if "organic_results" not in results:
            return []
            
        return [
            {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            }
            for result in results["organic_results"][:num_results]
        ]
    
    def get_compliance_verification(self, topic: str) -> Dict[str, Any]:
        """
        Get compliance verification information.
        
        Args:
            topic: The compliance topic to verify
            
        Returns:
            Dict with verification information
        """
        query = f"cloud security compliance standards {topic}"
        results = self.search(query, num_results=3)
        
        return {
            "query": query,
            "results": results
        }
