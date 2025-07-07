"""
MI Documentation Retrieval Tools

This module provides tools for retrieving information from the MI (Manuals and Instructions) 
documentation collection, which contains installation manuals, technical procedures, 
and operational guidelines.
"""

import logging
from typing import Dict, List, Optional

from agno import tool
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.qdrant_clients import QdrantClientManager
from ..models import RetrievalResult, SourceType

logger = logging.getLogger(__name__)


class MIRetrievalParams(BaseModel):
    """Parameters for MI documentation retrieval"""
    
    query: str = Field(..., description="Search query for MI documentation")
    project_name: Optional[str] = Field(None, description="Project name to filter results")
    limit: int = Field(10, description="Maximum number of results to return")
    score_threshold: float = Field(0.7, description="Minimum similarity score for results")


class MIRetriever:
    """Tool for retrieving information from MI documentation collection"""
    
    def __init__(self):
        """Initialize the MI retriever"""
        self.config = get_config()
        self.collection_name = self.config.qdrant_config.mi_collection
        self.client_manager = QdrantClientManager()
        
        logger.info(f"Initialized MIRetriever for collection: {self.collection_name}")
    
    def retrieve_mi_docs(
        self, 
        query: str, 
        project_name: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> RetrievalResult:
        """
        Retrieve MI documentation based on query and optional project filter.
        
        Args:
            query: Search query for MI documentation
            project_name: Optional project name to filter results
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            RetrievalResult containing retrieved documents
        """
        try:
            logger.info(f"Retrieving MI docs for query: '{query}', project: {project_name}")
            
            # Build search filters
            filters = {}
            if project_name:
                filters["project"] = project_name
            
            # Get client and perform search
            client = self.client_manager.get_client()
            if not client:
                logger.error("Failed to get Qdrant client")
                return RetrievalResult(
                    source_type=SourceType.MI_DOCUMENTATION,
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
                        "document_type": result.payload.get("document_type", "manual"),
                        "project": result.payload.get("project", ""),
                        "version": result.payload.get("version", ""),
                        "section": result.payload.get("section", ""),
                        "score": float(result.score),
                        "source_file": result.payload.get("source_file", ""),
                        "last_updated": result.payload.get("last_updated", "")
                    }
                    documents.append(doc_content)
            
            logger.info(f"Retrieved {len(documents)} MI documents")
            
            return RetrievalResult(
                source_type=SourceType.MI_DOCUMENTATION,
                query=query,
                documents=documents,
                metadata={
                    "total_results": len(documents),
                    "collection": self.collection_name,
                    "project_filter": project_name,
                    "score_threshold": score_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Error retrieving MI docs: {str(e)}")
            return RetrievalResult(
                source_type=SourceType.MI_DOCUMENTATION,
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
def retrieve_mi_documentation(
    query: str,
    project_name: Optional[str] = None,
    limit: int = 10
) -> Dict:
    """
    Retrieve information from MI documentation (installation manuals, technical procedures).
    
    This tool searches through installation manuals, technical procedures, and operational 
    guidelines to find relevant information for the user's query.
    
    Args:
        query: Search query for MI documentation
        project_name: Optional project name to filter results
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        Dictionary containing retrieved documents and metadata
    """
    retriever = MIRetriever()
    result = retriever.retrieve_mi_docs(
        query=query,
        project_name=project_name,
        limit=limit
    )
    
    return {
        "source": "MI Documentation",
        "query": query,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


@tool
def search_installation_procedures(
    project_name: str,
    procedure_type: Optional[str] = None,
    limit: int = 5
) -> Dict:
    """
    Search for specific installation procedures for a project.
    
    Args:
        project_name: Name of the project
        procedure_type: Optional type of procedure (e.g., "installation", "configuration", "deployment")
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing installation procedures
    """
    query = f"installation procedures {project_name}"
    if procedure_type:
        query += f" {procedure_type}"
    
    retriever = MIRetriever()
    result = retriever.retrieve_mi_docs(
        query=query,
        project_name=project_name,
        limit=limit
    )
    
    # Filter for installation-related documents
    installation_docs = [
        doc for doc in result.documents 
        if any(keyword in doc.get("content", "").lower() or 
               keyword in doc.get("title", "").lower() 
               for keyword in ["install", "setup", "deploy", "configuration", "procedure"])
    ]
    
    return {
        "source": "MI Documentation - Installation Procedures",
        "project": project_name,
        "procedure_type": procedure_type,
        "documents": installation_docs[:limit],
        "total_results": len(installation_docs),
        "metadata": result.metadata
    }


@tool
def get_technical_manual_sections(
    project_name: str,
    section_type: Optional[str] = None,
    limit: int = 8
) -> Dict:
    """
    Get specific sections from technical manuals for a project.
    
    Args:
        project_name: Name of the project
        section_type: Optional section type (e.g., "troubleshooting", "maintenance", "configuration")
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing technical manual sections
    """
    query = f"technical manual {project_name}"
    if section_type:
        query += f" {section_type}"
    
    retriever = MIRetriever()
    result = retriever.retrieve_mi_docs(
        query=query,
        project_name=project_name,
        limit=limit
    )
    
    return {
        "source": "MI Documentation - Technical Manuals",
        "project": project_name,
        "section_type": section_type,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


# Export the main retriever class for use in other modules
__all__ = ["MIRetriever", "retrieve_mi_documentation", "search_installation_procedures", "get_technical_manual_sections"] 