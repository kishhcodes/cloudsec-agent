# src/agents/compliance_bot/web_search.py
import os
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
import re
import time
from rich.console import Console

console = Console()

class WebSearcher:
    """
    Enhanced web search functionality to find specific information like articles, blog posts,
    authors, and content details from the web.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web searcher.
        
        Args:
            api_key: SERPAPI API key (defaults to SERPAPI_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI API key not found. Please set SERPAPI_API_KEY environment variable.")
    
    def find_article(self, query: str) -> Dict[str, Any]:
        """
        Find articles based on a user query. This is the main method used by the CLI.
        
        Args:
            query: User's search query
            
        Returns:
            Dictionary with search results and metadata
        """
        # Extract key information from query
        author_match = re.search(r'(?:by|author|written by)\s+([^.,]+)', query, re.IGNORECASE)
        topic_match = re.search(r'(?:about|on|regarding|related to|topic)\s+([^.,]+)', query, re.IGNORECASE)
        
        author = author_match.group(1).strip() if author_match else None
        topic = topic_match.group(1).strip() if topic_match else None
        
        # If no specific author or topic, use the entire query
        search_query = query
        if author and topic:
            search_query = f"{author} {topic}"
        elif author:
            search_query = f"{author} article"
        elif topic:
            search_query = f"{topic} security article"
            
        # Perform search
        try:
            results = self._general_search(search_query)
            
            if not results:
                # Try a broader search if specific search didn't yield results
                broader_query = re.sub(r'(?:by|author|written by|about|on|regarding|related to)\s+([^.,]+)', '', query).strip()
                if broader_query and broader_query != query:
                    results = self._general_search(broader_query)
            
            return {
                "found": bool(results),
                "query": search_query,
                "results": results,
                "suggestion": "Try broadening your search or using different keywords" if not results else None
            }
        
        except Exception as e:
            console.print(f"[bold red]Error searching for articles:[/bold red] {str(e)}")
            return {
                "found": False,
                "query": search_query,
                "results": [],
                "error": str(e),
                "suggestion": "Please check your internet connection or API key and try again"
            }
    
    def search_article(self, author: str, topic: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for articles by a specific author, optionally about a specific topic.
        
        Args:
            author: Name of the author
            topic: Optional topic to narrow down the search
            max_results: Maximum number of results to return
            
        Returns:
            List of article information
        """
        query = f'"{author}" article'
        if topic:
            query += f' "{topic}"'
            
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": max_results * 2,  # Request more to filter down to quality results
        }
        
        console.print(f"[dim]Searching for articles by {author}{' about ' + topic if topic else ''}...[/dim]")
        
        # Perform the search
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"SERPAPI error: {results['error']}")
            
        if "organic_results" not in results or len(results["organic_results"]) == 0:
            console.print(f"[yellow]No articles found for {author}{' about ' + topic if topic else ''}[/yellow]")
            return []
        
        # Extract and format article results
        articles = []
        for result in results["organic_results"][:max_results * 2]:  # Process more to get quality results
            if self._looks_like_article(result):
                articles.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "date": self._extract_date(result.get("snippet", "")),
                    "source": self._extract_source(result.get("link", ""))
                })
                
                if len(articles) >= max_results:
                    break
        
        return articles
    
    def search_specific_content(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a detailed search for specific content like an article, blog post, etc.
        
        Args:
            query: Detailed search query (e.g., "Maciej Pocwierz posted an article regarding S3 bucket")
            max_results: Maximum number of results to return
            
        Returns:
            Dict with search information and results
        """
        # Extract entities from query for better search
        entities = self._extract_entities(query)
        
        # Construct an optimized search query
        search_query = " ".join([
            f'"{entity}"' for entity in entities if len(entity.split()) > 1
        ] + [entity for entity in entities if len(entity.split()) == 1])
        
        # Add specific terms to help find articles/posts
        if "article" not in search_query.lower() and "post" not in search_query.lower():
            search_query += " article OR post OR blog"
            
        search_params = {
            "engine": "google",
            "q": search_query,
            "api_key": self.api_key,
            "num": max_results * 2,
        }
        
        console.print(f"[dim]Searching for: {search_query}...[/dim]")
        
        # Perform the search
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        if "error" in results:
            raise Exception(f"SERPAPI error: {results['error']}")
            
        if "organic_results" not in results:
            return {
                "query": query,
                "extracted_query": search_query,
                "found": False,
                "message": "No results found",
                "results": []
            }
            
        # Process and rank results based on relevance to entities
        processed_results = self._process_and_rank_results(results["organic_results"], entities)
        
        # Limit to requested number
        top_results = processed_results[:max_results]
        
        return {
            "query": query,
            "extracted_query": search_query,
            "found": len(top_results) > 0,
            "message": f"Found {len(top_results)} relevant results" if top_results else "No relevant results found",
            "results": top_results
        }
        
    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential named entities from the query string."""
        # Extract quoted content first
        quoted = re.findall(r'"([^"]*)"', query)
        
        # Remove quotes from the query
        clean_query = re.sub(r'"[^"]*"', '', query)
        
        # Extract capitalized terms (potential names)
        capitalized = re.findall(r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)\b', clean_query)
        
        # Extract other potentially important terms
        important_terms = [word for word in clean_query.split() if word.lower() not in 
                          {"a", "an", "the", "in", "on", "at", "by", "for", "with", "about", "regarding",
                           "to", "of", "from", "as", "posted", "wrote", "published", "shared", "created"}]
        
        # Combine all entities, prioritizing quoted and capitalized
        all_entities = quoted + capitalized
        
        # Add other important terms that aren't already included
        for term in important_terms:
            if not any(term.lower() in entity.lower() for entity in all_entities):
                all_entities.append(term)
                
        return all_entities
    
    def _looks_like_article(self, result: Dict[str, Any]) -> bool:
        """Check if a search result looks like it points to an article."""
        snippet = result.get("snippet", "").lower()
        title = result.get("title", "").lower()
        
        # Check if title or snippet contains article-like indicators
        article_indicators = ["article", "blog", "post", "wrote", "published", "author"]
        date_pattern = r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        
        # Check for indicators
        for indicator in article_indicators:
            if indicator in title or indicator in snippet:
                return True
                
        # Check for dates (often indicates an article)
        if re.search(date_pattern, snippet, re.IGNORECASE):
            return True
            
        return False
    
    def _extract_date(self, text: str) -> str:
        """Extract a publication date from text if present."""
        date_patterns = [
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
                
        return ""
    
    def _extract_source(self, url: str) -> str:
        """Extract the source (domain) from a URL."""
        if not url:
            return ""
            
        # Extract domain from URL
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            return domain_match.group(1)
            
        return ""
    
    def _process_and_rank_results(self, results: List[Dict[str, Any]], entities: List[str]) -> List[Dict[str, Any]]:
        """Process and rank search results based on relevance to extracted entities."""
        processed = []
        
        for result in results:
            # Calculate a relevance score based on how many entities appear in title and snippet
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            content = title + " " + snippet
            
            # Calculate relevance score
            score = 0
            for entity in entities:
                if entity.lower() in content:
                    # Award points based on where the entity appears
                    if entity.lower() in title:
                        score += 3  # Higher weight for title matches
                    else:
                        score += 1  # Lower weight for snippet matches
            
            # Add result with score
            processed.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "date": self._extract_date(result.get("snippet", "")),
                "source": self._extract_source(result.get("link", "")),
                "relevance_score": score
            })
        
        # Sort by relevance score (highest first)
        return sorted(processed, key=lambda x: x["relevance_score"], reverse=True)


    def _general_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a general search for articles based on a query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of article information
        """
        search_params = {
            "engine": "google",
            "q": f"{query} security article",
            "api_key": self.api_key,
            "num": max_results * 2,  # Request more to filter down
            "gl": "us",  # Set region to US for consistent results
        }
        
        try:
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            # Check if we have organic results
            if "organic_results" not in results:
                return []
                
            # Process and filter results
            article_results = []
            for result in results["organic_results"][:max_results*2]:
                if self._looks_like_article(result):
                    article_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "date": self._extract_date(result.get("snippet", "")),
                        "source": self._extract_source(result.get("link", "")),
                    })
                    
                    if len(article_results) >= max_results:
                        break
                        
            return article_results
            
        except Exception as e:
            console.print(f"[bold red]Search error:[/bold red] {str(e)}")
            return []


# Example usage function (not used directly by the CLI)
# Function to expose to the CLI
def find_article(query: str) -> Dict[str, Any]:
    """
    Find articles or specific content based on a natural language query.
    
    Args:
        query: Natural language query (e.g., "articles about AWS security best practices")
        
    Returns:
        Dict with search results and information
    """
    try:
        searcher = WebSearcher()
        
        # Extract topic and author if present
        author_match = re.search(r"by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", query, re.IGNORECASE)
        
        if author_match:
            author = author_match.group(1)
            results = searcher.search_specific_content(query)
        else:
            # Use general search
            article_results = searcher._general_search(query)
            
            if article_results:
                results = {
                    "found": True,
                    "query": query,
                    "results": article_results,
                    "count": len(article_results)
                }
            else:
                results = {"found": False, "query": query, "results": [], "count": 0}
        
        # Check if we found any results
        if not results["found"]:
            # Try extracting author name if query looks like it's asking about a specific author
            author_match = re.search(r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:wrote|posted|published|authored)', query)
            if author_match:
                author = author_match.group(1)
                
                # Extract topic if present
                topic_match = re.search(r'(?:about|on|regarding|related to)\s+(.+?)(?:\.|\?|$)', query)
                topic = topic_match.group(1) if topic_match else None
                
                # Try direct author search
                author_results = searcher.search_article(author, topic)
                if author_results:
                    return {
                        "query": query,
                        "found": True,
                        "message": f"Found {len(author_results)} articles by {author}",
                        "results": author_results
                    }
        
        return results
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return {
            "query": query,
            "found": False,
            "error": str(e),
            "results": []
        }


if __name__ == "__main__":
    # Example usage
    query = "Maciej Pocwierz posted an article regarding S3 bucket"
    results = find_article(query)
    
    console = Console()
    
    if results["found"]:
        console.print(f"\n[bold green]Found results for:[/bold green] {results['query']}\n")
        
        for i, result in enumerate(results["results"], 1):
            console.print(f"[bold cyan]{i}. {result['title']}[/bold cyan]")
            if result.get("date"):
                console.print(f"[dim]Date: {result['date']}[/dim]")
            console.print(f"[dim]Source: {result['source']}[/dim]")
            console.print(f"{result['snippet']}")
            console.print(f"[link={result['link']}]{result['link']}[/link]")
            console.print()
    else:
        console.print(f"\n[yellow]No results found for:[/yellow] {results['query']}")
        if "error" in results:
            console.print(f"[red]Error: {results['error']}[/red]")
