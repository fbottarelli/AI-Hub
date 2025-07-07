"""
Wiki Knowledge Base Retrieval Tools

This module provides tools for retrieving information from the Wiki Knowledge Base,
which contains organizational processes, standards, guidelines, and institutional knowledge.
"""

import logging
from typing import Dict, List, Optional

from agno import tool
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.qdrant_clients import QdrantClientManager
from ..models import RetrievalResult, SourceType

logger = logging.getLogger(__name__)


class WikiRetrievalParams(BaseModel):
    """Parameters for Wiki knowledge base retrieval"""
    
    query: str = Field(..., description="Search query for Wiki knowledge base")
    topic_category: Optional[str] = Field(None, description="Topic category to filter results")
    limit: int = Field(10, description="Maximum number of results to return")
    score_threshold: float = Field(0.7, description="Minimum similarity score for results")


class WikiRetriever:
    """Tool for retrieving information from Wiki knowledge base collection"""
    
    def __init__(self):
        """Initialize the Wiki retriever"""
        self.config = get_config()
        self.collection_name = self.config.qdrant_config.wiki_collection
        self.client_manager = QdrantClientManager()
        
        logger.info(f"Initialized WikiRetriever for collection: {self.collection_name}")
    
    def retrieve_wiki_content(
        self, 
        query: str, 
        topic_category: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> RetrievalResult:
        """
        Retrieve Wiki content based on query and optional topic filter.
        
        Args:
            query: Search query for Wiki content
            topic_category: Optional topic category to filter results
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            RetrievalResult containing retrieved Wiki articles
        """
        try:
            logger.info(f"Retrieving Wiki content for query: '{query}', category: {topic_category}")
            
            # Build search filters
            filters = {}
            if topic_category:
                filters["category"] = topic_category
            
            # Get client and perform search
            client = self.client_manager.get_client()
            if not client:
                logger.error("Failed to get Qdrant client")
                return RetrievalResult(
                    source_type=SourceType.WIKI_KNOWLEDGE_BASE,
                    query=query,
                    documents=[],
                    metadata={
                        "error": "Failed to connect to Qdrant",
                        "collection": self.collection_name
                    }
                )
            
            # Perform semantic search
            search_results = client.search(
                collection_name=self.collection_name,
                query_vector=self._get_query_embedding(query),
                query_filter=filters if filters else None,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Process results
            documents = []
            for result in search_results:
                if hasattr(result, 'payload') and result.payload:
                    doc_content = {
                        "content": result.payload.get("content", ""),
                        "title": result.payload.get("title", ""),
                        "category": result.payload.get("category", ""),
                        "tags": result.payload.get("tags", []),
                        "author": result.payload.get("author", ""),
                        "last_modified": result.payload.get("last_modified", ""),
                        "version": result.payload.get("version", ""),
                        "wiki_url": result.payload.get("wiki_url", ""),
                        "score": float(result.score),
                        "section": result.payload.get("section", ""),
                        "related_topics": result.payload.get("related_topics", [])
                    }
                    documents.append(doc_content)
            
            logger.info(f"Retrieved {len(documents)} Wiki articles")
            
            return RetrievalResult(
                source_type=SourceType.WIKI_KNOWLEDGE_BASE,
                query=query,
                documents=documents,
                metadata={
                    "total_results": len(documents),
                    "collection": self.collection_name,
                    "topic_filter": topic_category,
                    "score_threshold": score_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Error retrieving Wiki content: {str(e)}")
            return RetrievalResult(
                source_type=SourceType.WIKI_KNOWLEDGE_BASE,
                query=query,
                documents=[],
                metadata={
                    "error": str(e),
                    "collection": self.collection_name
                }
            )
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for query using the configured embedding model"""
        try:
            embedding_model = self.client_manager.get_embedding_model()
            if embedding_model:
                return embedding_model.embed_query(query)
            else:
                logger.warning("No embedding model available, using dummy embedding")
                return [0.0] * 384  # Default embedding size
        except Exception as e:
            logger.error(f"Error getting query embedding: {str(e)}")
            return [0.0] * 384


@tool
def retrieve_wiki_knowledge(
    query: str,
    topic_category: Optional[str] = None,
    limit: int = 10
) -> Dict:
    """
    Retrieve information from the Wiki knowledge base (organizational processes, standards).
    
    This tool searches through Wiki articles containing organizational processes, standards,
    guidelines, and institutional knowledge to find relevant information.
    
    Args:
        query: Search query for Wiki knowledge base
        topic_category: Optional topic category to filter results
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        Dictionary containing retrieved Wiki articles and metadata
    """
    retriever = WikiRetriever()
    result = retriever.retrieve_wiki_content(
        query=query,
        topic_category=topic_category,
        limit=limit
    )
    
    return {
        "source": "Wiki Knowledge Base",
        "query": query,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


@tool
def search_organizational_processes(
    process_type: str,
    department: Optional[str] = None,
    limit: int = 8
) -> Dict:
    """
    Search for organizational processes and procedures in the Wiki.
    
    Args:
        process_type: Type of process (e.g., "approval", "change management", "security")
        department: Optional department filter
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing organizational processes
    """
    query = f"organizational process {process_type}"
    if department:
        query += f" {department}"
    
    retriever = WikiRetriever()
    result = retriever.retrieve_wiki_content(
        query=query,
        topic_category="processes",
        limit=limit
    )
    
    # Filter for process-related documents
    process_docs = [
        doc for doc in result.documents 
        if any(keyword in doc.get("content", "").lower() or 
               keyword in doc.get("title", "").lower() 
               for keyword in ["process", "procedure", "workflow", "guideline", "policy"])
    ]
    
    return {
        "source": "Wiki Knowledge Base - Organizational Processes",
        "process_type": process_type,
        "department": department,
        "documents": process_docs[:limit],
        "total_results": len(process_docs),
        "metadata": result.metadata
    }


@tool
def get_standards_and_guidelines(
    standards_type: str,
    domain: Optional[str] = None,
    limit: int = 6
) -> Dict:
    """
    Get standards and guidelines from the Wiki knowledge base.
    
    Args:
        standards_type: Type of standards (e.g., "coding", "security", "documentation")
        domain: Optional domain or area (e.g., "development", "operations", "compliance")
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing standards and guidelines
    """
    query = f"standards guidelines {standards_type}"
    if domain:
        query += f" {domain}"
    
    retriever = WikiRetriever()
    result = retriever.retrieve_wiki_content(
        query=query,
        topic_category="standards",
        limit=limit
    )
    
    return {
        "source": "Wiki Knowledge Base - Standards & Guidelines",
        "standards_type": standards_type,
        "domain": domain,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


@tool
def search_best_practices(
    practice_area: str,
    technology: Optional[str] = None,
    limit: int = 8
) -> Dict:
    """
    Search for best practices and recommendations in the Wiki.
    
    Args:
        practice_area: Area of practice (e.g., "development", "deployment", "monitoring")
        technology: Optional technology or tool name
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing best practices
    """
    query = f"best practices {practice_area}"
    if technology:
        query += f" {technology}"
    
    retriever = WikiRetriever()
    result = retriever.retrieve_wiki_content(
        query=query,
        topic_category="best-practices",
        limit=limit
    )
    
    # Filter for best practices content
    best_practices_docs = [
        doc for doc in result.documents 
        if any(keyword in doc.get("content", "").lower() or 
               keyword in doc.get("title", "").lower() 
               for keyword in ["best practice", "recommendation", "guideline", "pattern", "approach"])
    ]
    
    return {
        "source": "Wiki Knowledge Base - Best Practices",
        "practice_area": practice_area,
        "technology": technology,
        "documents": best_practices_docs[:limit],
        "total_results": len(best_practices_docs),
        "metadata": result.metadata
    }


@tool
def get_institutional_knowledge(
    knowledge_area: str,
    historical: bool = False,
    limit: int = 10
) -> Dict:
    """
    Retrieve institutional knowledge and historical information from the Wiki.
    
    Args:
        knowledge_area: Area of knowledge (e.g., "architecture", "decisions", "lessons learned")
        historical: Whether to include historical/archived content
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing institutional knowledge
    """
    query = f"institutional knowledge {knowledge_area}"
    if historical:
        query += " historical lessons learned"
    
    retriever = WikiRetriever()
    result = retriever.retrieve_wiki_content(
        query=query,
        topic_category="knowledge",
        limit=limit
    )
    
    return {
        "source": "Wiki Knowledge Base - Institutional Knowledge",
        "knowledge_area": knowledge_area,
        "historical": historical,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


# Export the main retriever class for use in other modules
__all__ = [
    "WikiRetriever", 
    "retrieve_wiki_knowledge", 
    "search_organizational_processes",
    "get_standards_and_guidelines",
    "search_best_practices",
    "get_institutional_knowledge"
] 