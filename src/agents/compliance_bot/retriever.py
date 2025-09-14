# src/agents/compliance_bot/retriever.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List

class ComplianceRetriever:
    """Retrieves relevant compliance information from the vector store."""
    
    def __init__(self, embeddings_path="data/embeddings/index"):
        """Initialize the retriever with the path to embeddings."""
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = FAISS.load_local(embeddings_path, self.embeddings, allow_dangerous_deserialization=True)
    
    def retrieve(self, query: str, k: int = 5) -> List[dict]:
        """
        Retrieve relevant documents based on the query.
        
        Args:
            query: The user's query
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents
        """
        results = self.vectorstore.similarity_search(query, k=k)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": None  # FAISS similarity_search doesn't return scores by default
            }
            for doc in results
        ]
    
    def retrieve_with_score(self, query: str, k: int = 5) -> List[dict]:
        """
        Retrieve relevant documents with similarity scores.
        
        Args:
            query: The user's query
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with scores
        """
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [
            {
                "content": doc[0].page_content,
                "metadata": doc[0].metadata,
                "score": float(doc[1])
            }
            for doc in results
        ]
