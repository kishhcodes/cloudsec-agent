# src/agents/compliance_bot/agent.py
import os
import re
from typing import Optional, Dict, Any, List
from .retriever import ComplianceRetriever
from .search import SearchVerifier
from .llm import ComplianceLLM
from .web_search import WebSearcher

class CloudComplianceAgent:
    """
    Main agent class that orchestrates retrieval, verification, and response generation.
    """
    
    def __init__(
        self,
        embeddings_path: str = "data/embeddings/index",
        serpapi_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        use_search: bool = True
    ):
        """
        Initialize the compliance agent.
        
        Args:
            embeddings_path: Path to the vector store
            serpapi_key: SERPAPI API key (defaults to env variable)
            google_api_key: Google API key (defaults to env variable)
            use_search: Whether to use SERPAPI for cross-verification
        """
        # Initialize components
        self.retriever = ComplianceRetriever(embeddings_path)
        self.use_search = use_search
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_API_KEY")
        
        # Initialize search verifier if enabled
        if use_search:
            try:
                self.search = SearchVerifier(api_key=self.serpapi_key)
            except ValueError:
                self.use_search = False
                print("Warning: SERPAPI API key not found. Search verification disabled.")
        
        # Initialize web searcher if SERPAPI key is available
        if self.serpapi_key:
            try:
                self.web_searcher = WebSearcher(api_key=self.serpapi_key)
            except ValueError:
                print("Warning: SERPAPI API key not found. Web search disabled.")
                self.web_searcher = None
        else:
            self.web_searcher = None
        
        # Initialize LLM
        self.llm = ComplianceLLM(api_key=google_api_key)
    
    def is_article_search_query(self, query: str) -> bool:
        """
        Determine if a query is likely asking about a specific article or post.
        
        Args:
            query: The user query
            
        Returns:
            True if the query appears to be asking about an article or post
        """
        # Define patterns that suggest article search queries
        article_patterns = [
            r'(?:wrote|posted|published|authored|written).*(?:article|post|blog)',
            r'(?:article|post|blog).*(?:by|from|written by).*',
            r'(?:what|find).*(?:article|post|blog)',
            r'(?:article|post|blog).*(?:about|regarding|on the topic of)',
        ]
        
        # Check for author names (capitalized words)
        has_capitalized_name = bool(re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', query))
        
        # Check for article patterns
        for pattern in article_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
                
        # If there's a capitalized name and mentions "article" or "post" or "blog", it's likely an article search
        if has_capitalized_name and any(term in query.lower() for term in ["article", "post", "blog"]):
            return True
            
        return False
    
    def search_for_article(self, query: str) -> Dict[str, Any]:
        """
        Search for articles based on a query.
        
        Args:
            query: The query about an article or post
            
        Returns:
            Dict with search results and LLM-generated response
        """
        if not self.web_searcher:
            return {
                "query": query,
                "response": "Sorry, I can't search for articles right now because the SERPAPI key is not configured.",
                "retrieved_docs": [],
                "search_results": [],
                "is_article_search": True
            }
            
        # Get article search results
        article_results = self.web_searcher.search_specific_content(query)
        
        # Extract content from results for the LLM to summarize
        article_content = ""
        if article_results.get("found") and article_results.get("results"):
            for i, result in enumerate(article_results["results"], 1):
                article_content += f"Article {i}:\nTitle: {result.get('title', '')}\n"
                article_content += f"Snippet: {result.get('snippet', '')}\n"
                article_content += f"Source: {result.get('source', '')}\n"
                article_content += f"Link: {result.get('link', '')}\n"
                if result.get('date'):
                    article_content += f"Date: {result.get('date', '')}\n"
                article_content += "\n"
                
        # Get the LLM to generate a response about the articles
        llm_prompt = f"""
Based on a search for articles related to the query: "{query}", 
the following information was found:

{article_content if article_content else "No specific articles were found."}

Please provide a helpful response to the user's query about these articles.
If no articles were found, suggest alternative search terms or approaches.
"""
        
        # Generate LLM response
        response = self.llm.llm.invoke(llm_prompt).content
        
        return {
            "query": query,
            "response": response,
            "retrieved_docs": [],  # No compliance docs used here
            "search_results": article_results.get("results", []),
            "is_article_search": True
        }

    def process_query(self, query: str, k: int = 5, use_search: Optional[bool] = None) -> Dict[str, Any]:
        """
        Process a user query and generate a response.
        
        Args:
            query: The user's query
            k: Number of documents to retrieve
            use_search: Override the default search setting
            
        Returns:
            Dict with response and supporting information
        """
        # Check if this is an article search query
        if self.is_article_search_query(query):
            return self.search_for_article(query)
            
        # Regular compliance query processing
        # Override search setting if provided
        should_use_search = use_search if use_search is not None else self.use_search
        
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve_with_score(query, k=k)
        
        # Step 2: Get search results if enabled
        search_results = None
        if should_use_search:
            try:
                search_results = self.search.search(query, num_results=3)
            except Exception as e:
                print(f"Search error: {e}")
        
        # Step 3: Generate response
        response = self.llm.generate_response(
            query=query,
            retrieved_docs=retrieved_docs,
            search_results=search_results
        )
        
        # Return complete result
        return {
            "query": query,
            "response": response,
            "retrieved_docs": retrieved_docs,
            "search_results": search_results,
            "is_article_search": False
        }
