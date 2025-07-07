"""
User Documents Retrieval Tools

This module provides tools for retrieving information from user-uploaded documents
and project-specific documents, including personal files, project attachments,
and custom documentation.
"""

import logging
from typing import Dict, List, Optional

from agno import tool
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.qdrant_clients import QdrantClientManager
from ..models import RetrievalResult, SourceType

logger = logging.getLogger(__name__)


class UserDocsRetrievalParams(BaseModel):
    """Parameters for user documents retrieval"""
    
    query: str = Field(..., description="Search query for user documents")
    user_id: Optional[str] = Field(None, description="User ID to filter results")
    document_type: Optional[str] = Field(None, description="Document type to filter results")
    limit: int = Field(10, description="Maximum number of results to return")
    score_threshold: float = Field(0.7, description="Minimum similarity score for results")


class UserDocsRetriever:
    """Tool for retrieving information from user documents collection"""
    
    def __init__(self):
        """Initialize the User Documents retriever"""
        self.config = get_config()
        self.collection_name = self.config.qdrant_config.user_docs_collection
        self.client_manager = QdrantClientManager()
        
        logger.info(f"Initialized UserDocsRetriever for collection: {self.collection_name}")
    
    def retrieve_user_documents(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        document_type: Optional[str] = None,
        project_name: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> RetrievalResult:
        """
        Retrieve user documents based on query and optional filters.
        
        Args:
            query: Search query for user documents
            user_id: Optional user ID to filter results
            document_type: Optional document type to filter results
            project_name: Optional project name to filter results
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score for results
            
        Returns:
            RetrievalResult containing retrieved documents
        """
        try:
            logger.info(f"Retrieving user docs for query: '{query}', user: {user_id}, type: {document_type}")
            
            # Build search filters
            filters = {}
            if user_id:
                filters["user_id"] = user_id
            if document_type:
                filters["document_type"] = document_type
            if project_name:
                filters["project"] = project_name
            
            # Get client and perform search
            client = self.client_manager.get_client()
            if not client:
                logger.error("Failed to get Qdrant client")
                return RetrievalResult(
                    source_type=SourceType.USER_DOCUMENTS,
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
                        "filename": result.payload.get("filename", ""),
                        "document_type": result.payload.get("document_type", ""),
                        "user_id": result.payload.get("user_id", ""),
                        "project": result.payload.get("project", ""),
                        "upload_date": result.payload.get("upload_date", ""),
                        "file_size": result.payload.get("file_size", 0),
                        "file_path": result.payload.get("file_path", ""),
                        "score": float(result.score),
                        "tags": result.payload.get("tags", []),
                        "description": result.payload.get("description", ""),
                        "access_level": result.payload.get("access_level", "private")
                    }
                    documents.append(doc_content)
            
            logger.info(f"Retrieved {len(documents)} user documents")
            
            return RetrievalResult(
                source_type=SourceType.USER_DOCUMENTS,
                query=query,
                documents=documents,
                metadata={
                    "total_results": len(documents),
                    "collection": self.collection_name,
                    "user_filter": user_id,
                    "document_type_filter": document_type,
                    "project_filter": project_name,
                    "score_threshold": score_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Error retrieving user documents: {str(e)}")
            return RetrievalResult(
                source_type=SourceType.USER_DOCUMENTS,
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
def retrieve_user_documents(
    query: str,
    user_id: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 10
) -> Dict:
    """
    Retrieve information from user-uploaded documents and project-specific files.
    
    This tool searches through user-uploaded documents, project attachments,
    and custom documentation to find relevant information.
    
    Args:
        query: Search query for user documents
        user_id: Optional user ID to filter results to specific user's documents
        document_type: Optional document type filter (e.g., "pdf", "word", "presentation")
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        Dictionary containing retrieved documents and metadata
    """
    retriever = UserDocsRetriever()
    result = retriever.retrieve_user_documents(
        query=query,
        user_id=user_id,
        document_type=document_type,
        limit=limit
    )
    
    return {
        "source": "User Documents",
        "query": query,
        "documents": result.documents,
        "total_results": len(result.documents),
        "metadata": result.metadata
    }


@tool
def search_project_attachments(
    project_name: str,
    attachment_type: Optional[str] = None,
    limit: int = 8
) -> Dict:
    """
    Search for project-specific attachments and documents.
    
    Args:
        project_name: Name of the project
        attachment_type: Optional attachment type (e.g., "specification", "design", "report")
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing project attachments
    """
    query = f"project attachments {project_name}"
    if attachment_type:
        query += f" {attachment_type}"
    
    retriever = UserDocsRetriever()
    result = retriever.retrieve_user_documents(
        query=query,
        project_name=project_name,
        limit=limit
    )
    
    # Filter for project-specific documents
    project_docs = [
        doc for doc in result.documents 
        if doc.get("project", "").lower() == project_name.lower() or
           project_name.lower() in doc.get("content", "").lower() or
           project_name.lower() in doc.get("title", "").lower()
    ]
    
    return {
        "source": "User Documents - Project Attachments",
        "project": project_name,
        "attachment_type": attachment_type,
        "documents": project_docs[:limit],
        "total_results": len(project_docs),
        "metadata": result.metadata
    }


@tool
def get_user_uploaded_files(
    user_id: str,
    file_type: Optional[str] = None,
    recent_days: Optional[int] = None,
    limit: int = 10
) -> Dict:
    """
    Get files uploaded by a specific user.
    
    Args:
        user_id: User ID to search for
        file_type: Optional file type filter (e.g., "pdf", "docx", "pptx")
        recent_days: Optional filter for files uploaded in the last N days
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing user's uploaded files
    """
    query = f"user files {user_id}"
    if file_type:
        query += f" {file_type}"
    
    retriever = UserDocsRetriever()
    result = retriever.retrieve_user_documents(
        query=query,
        user_id=user_id,
        document_type=file_type,
        limit=limit
    )
    
    documents = result.documents
    
    # Filter by recent days if specified
    if recent_days:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=recent_days)
        
        recent_docs = []
        for doc in documents:
            upload_date_str = doc.get("upload_date", "")
            if upload_date_str:
                try:
                    upload_date = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
                    if upload_date >= cutoff_date:
                        recent_docs.append(doc)
                except ValueError:
                    # Include documents with unparseable dates
                    recent_docs.append(doc)
        
        documents = recent_docs
    
    return {
        "source": "User Documents - User Uploads",
        "user_id": user_id,
        "file_type": file_type,
        "recent_days": recent_days,
        "documents": documents[:limit],
        "total_results": len(documents),
        "metadata": result.metadata
    }


@tool
def search_document_by_filename(
    filename: str,
    user_id: Optional[str] = None,
    exact_match: bool = False,
    limit: int = 5
) -> Dict:
    """
    Search for documents by filename or partial filename.
    
    Args:
        filename: Filename or partial filename to search for
        user_id: Optional user ID to filter results
        exact_match: Whether to search for exact filename match
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing matching documents
    """
    if exact_match:
        query = f"filename:{filename}"
    else:
        query = f"filename contains {filename}"
    
    retriever = UserDocsRetriever()
    result = retriever.retrieve_user_documents(
        query=query,
        user_id=user_id,
        limit=limit
    )
    
    # Filter by filename matching
    matching_docs = []
    for doc in result.documents:
        doc_filename = doc.get("filename", "")
        if exact_match:
            if doc_filename == filename:
                matching_docs.append(doc)
        else:
            if filename.lower() in doc_filename.lower():
                matching_docs.append(doc)
    
    return {
        "source": "User Documents - Filename Search",
        "filename": filename,
        "user_id": user_id,
        "exact_match": exact_match,
        "documents": matching_docs[:limit],
        "total_results": len(matching_docs),
        "metadata": result.metadata
    }


@tool
def get_shared_documents(
    project_name: Optional[str] = None,
    access_level: str = "shared",
    limit: int = 10
) -> Dict:
    """
    Get documents that are shared or have public access.
    
    Args:
        project_name: Optional project name to filter results
        access_level: Access level filter ("shared", "public", "team")
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing shared documents
    """
    query = f"shared documents {access_level}"
    if project_name:
        query += f" {project_name}"
    
    retriever = UserDocsRetriever()
    result = retriever.retrieve_user_documents(
        query=query,
        project_name=project_name,
        limit=limit
    )
    
    # Filter by access level
    shared_docs = [
        doc for doc in result.documents 
        if doc.get("access_level", "private") in ["shared", "public", "team"]
    ]
    
    return {
        "source": "User Documents - Shared Documents",
        "project": project_name,
        "access_level": access_level,
        "documents": shared_docs[:limit],
        "total_results": len(shared_docs),
        "metadata": result.metadata
    }


# Export the main retriever class for use in other modules
__all__ = [
    "UserDocsRetriever",
    "retrieve_user_documents",
    "search_project_attachments",
    "get_user_uploaded_files",
    "search_document_by_filename",
    "get_shared_documents"
] 