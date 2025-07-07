"""
Verbali (Meeting Minutes) Retrieval Tools

This module provides Agno tools for retrieving information from meeting minutes,
RFC evaluations, and technical discussions stored in the verbali collection.
"""

import logging
import time
from typing import Dict, List, Optional, Union

from agno import tool
from langchain_core.documents import Document
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.project_manager import get_project_manager
from ..libs.qdrant_clients import get_qdrant_clients
from ..models import ProjectNameField, RetrievalResult, SourceType

logger = logging.getLogger(__name__)


class VerbaliRetrievalResult(BaseModel):
    """Result from verbali retrieval"""
    success: bool = Field(..., description="Whether retrieval was successful")
    documents: List[Document] = Field(default_factory=list, description="Retrieved documents")
    formatted_content: str = Field(default="", description="Formatted content for context")
    document_count: int = Field(default=0, description="Number of documents retrieved")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retrieval_time: float = Field(..., description="Time taken for retrieval")
    project_filter: Optional[Dict[str, str]] = Field(None, description="Project filter used")


@tool
def retrieve_verbali_for_project(
    project_name: str,
    user_query: Optional[str] = None,
    max_documents: int = 20
) -> VerbaliRetrievalResult:
    """
    Retrieve meeting minutes and verbali documents for a specific project.
    
    Uses scroll-based retrieval to get ALL documents for the project instead of
    similarity search, providing comprehensive context.
    
    Args:
        project_name: Name of the project to retrieve verbali for
        user_query: User's original query (for logging/context)
        max_documents: Maximum number of documents to retrieve (for safety)
        
    Returns:
        VerbaliRetrievalResult with retrieval results and formatted content
    """
    start_time = time.time()
    config = get_config()
    project_manager = get_project_manager()
    qdrant_clients = get_qdrant_clients()
    
    logger.info(f"Retrieving verbali for project: {project_name}")
    
    try:
        # Handle general context
        if project_name == "general":
            logger.info("General context - skipping verbali retrieval")
            return VerbaliRetrievalResult(
                success=True,
                documents=[],
                formatted_content="No specific project identified for verbali retrieval.",
                document_count=0,
                retrieval_time=time.time() - start_time,
                project_filter=None
            )
        
        # Validate and normalize project name
        canonical_project_name = project_manager.get_canonical_name(project_name)
        if not canonical_project_name:
            error_msg = f"Project '{project_name}' not found in project manager"
            logger.warning(error_msg)
            return VerbaliRetrievalResult(
                success=False,
                documents=[],
                formatted_content="",
                document_count=0,
                error_message=error_msg,
                retrieval_time=time.time() - start_time,
                project_filter=None
            )
        
        logger.info(f"Normalized project name: '{project_name}' -> '{canonical_project_name}'")
        
        # Create project filter
        project_filter_dict = project_manager.get_project_filter_dict(
            canonical_project_name, 
            ProjectNameField.VERBALI_PROJECT
        )
        
        if not project_filter_dict:
            error_msg = f"Could not create filter for project: {canonical_project_name}"
            logger.warning(error_msg)
            return VerbaliRetrievalResult(
                success=False,
                documents=[],
                formatted_content="",
                document_count=0,
                error_message=error_msg,
                retrieval_time=time.time() - start_time,
                project_filter=None
            )
        
        # Get collection configuration
        verbali_config = config.get_agent_config().collections.get("verbali")
        if not verbali_config or not verbali_config.enabled:
            error_msg = "Verbali collection is not configured or enabled"
            logger.error(error_msg)
            return VerbaliRetrievalResult(
                success=False,
                documents=[],
                formatted_content="",
                document_count=0,
                error_message=error_msg,
                retrieval_time=time.time() - start_time,
                project_filter=project_filter_dict
            )
        
        # Retrieve documents using scroll
        documents = qdrant_clients.scroll_all_documents_for_project(
            collection_name=verbali_config.collection_name,
            project_filter_dict=project_filter_dict
        )
        
        # Apply safety limit
        if len(documents) > max_documents:
            logger.warning(f"Retrieved {len(documents)} documents, limiting to {max_documents}")
            documents = documents[:max_documents]
        
        # Format the content
        formatted_content = _format_verbali_documents(documents, canonical_project_name)
        
        logger.info(f"Retrieved {len(documents)} verbali documents for project: {canonical_project_name}")
        
        return VerbaliRetrievalResult(
            success=True,
            documents=documents,
            formatted_content=formatted_content,
            document_count=len(documents),
            retrieval_time=time.time() - start_time,
            project_filter=project_filter_dict
        )
        
    except Exception as e:
        error_msg = f"Error retrieving verbali for project {project_name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return VerbaliRetrievalResult(
            success=False,
            documents=[],
            formatted_content="",
            document_count=0,
            error_message=error_msg,
            retrieval_time=time.time() - start_time,
            project_filter=None
        )


@tool
def retrieve_verbali_for_multiple_projects(
    project_names: List[str],
    user_query: Optional[str] = None,
    max_documents_per_project: int = 15
) -> VerbaliRetrievalResult:
    """
    Retrieve verbali documents for multiple projects.
    
    Args:
        project_names: List of project names to retrieve verbali for
        user_query: User's original query (for logging/context)
        max_documents_per_project: Maximum documents per project
        
    Returns:
        VerbaliRetrievalResult with combined results from all projects
    """
    start_time = time.time()
    logger.info(f"Retrieving verbali for multiple projects: {project_names}")
    
    all_documents = []
    all_formatted_content = []
    project_filters = {}
    errors = []
    
    for project_name in project_names:
        result = retrieve_verbali_for_project(
            project_name=project_name,
            user_query=user_query,
            max_documents=max_documents_per_project
        )
        
        if result.success:
            all_documents.extend(result.documents)
            if result.formatted_content:
                all_formatted_content.append(result.formatted_content)
            if result.project_filter:
                project_filters[project_name] = result.project_filter
        else:
            errors.append(f"Project {project_name}: {result.error_message}")
    
    # Combine formatted content
    combined_content = "\n\n" + "="*50 + "\n\n".join(all_formatted_content) if all_formatted_content else ""
    
    # Determine overall success
    success = len(all_documents) > 0
    error_message = "; ".join(errors) if errors else None
    
    logger.info(f"Retrieved {len(all_documents)} total verbali documents from {len(project_names)} projects")
    
    return VerbaliRetrievalResult(
        success=success,
        documents=all_documents,
        formatted_content=combined_content,
        document_count=len(all_documents),
        error_message=error_message,
        retrieval_time=time.time() - start_time,
        project_filter=project_filters
    )


@tool
def search_verbali_by_keywords(
    keywords: str,
    project_filter: Optional[str] = None,
    max_results: int = 10
) -> VerbaliRetrievalResult:
    """
    Search verbali documents using keyword similarity search.
    
    Args:
        keywords: Keywords to search for
        project_filter: Optional project name to filter results
        max_results: Maximum number of results to return
        
    Returns:
        VerbaliRetrievalResult with search results
    """
    start_time = time.time()
    config = get_config()
    qdrant_clients = get_qdrant_clients()
    
    logger.info(f"Searching verbali with keywords: '{keywords}'")
    
    try:
        # Get collection configuration
        verbali_config = config.get_agent_config().collections.get("verbali")
        if not verbali_config or not verbali_config.enabled:
            error_msg = "Verbali collection is not configured or enabled"
            logger.error(error_msg)
            return VerbaliRetrievalResult(
                success=False,
                documents=[],
                formatted_content="",
                document_count=0,
                error_message=error_msg,
                retrieval_time=time.time() - start_time
            )
        
        # Prepare filter
        filter_dict = None
        if project_filter:
            project_manager = get_project_manager()
            canonical_project = project_manager.get_canonical_name(project_filter)
            if canonical_project:
                filter_dict = project_manager.get_project_filter_dict(
                    canonical_project,
                    ProjectNameField.VERBALI_PROJECT
                )
        
        # Perform similarity search
        documents = qdrant_clients.similarity_search(
            collection_config=verbali_config,
            query=keywords,
            k=max_results,
            filter_dict=filter_dict
        )
        
        # Format the content
        project_context = project_filter or "multiple projects"
        formatted_content = _format_verbali_documents(documents, project_context)
        
        logger.info(f"Found {len(documents)} verbali documents matching keywords")
        
        return VerbaliRetrievalResult(
            success=True,
            documents=documents,
            formatted_content=formatted_content,
            document_count=len(documents),
            retrieval_time=time.time() - start_time,
            project_filter=filter_dict
        )
        
    except Exception as e:
        error_msg = f"Error searching verbali: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return VerbaliRetrievalResult(
            success=False,
            documents=[],
            formatted_content="",
            document_count=0,
            error_message=error_msg,
            retrieval_time=time.time() - start_time
        )


def _format_verbali_documents(documents: List[Document], project_context: str) -> str:
    """
    Format verbali documents for context inclusion.
    
    Args:
        documents: List of retrieved documents
        project_context: Project context for the header
        
    Returns:
        Formatted string ready for LLM context
    """
    if not documents:
        return f"No verbali documents found for {project_context}."
    
    # Group documents by file for better organization
    docs_by_file = {}
    for doc in documents:
        file_name = doc.metadata.get('file_name', 'Unknown')
        if file_name not in docs_by_file:
            docs_by_file[file_name] = []
        docs_by_file[file_name].append(doc)
    
    formatted_sections = []
    
    # Add header
    formatted_sections.append(f"Meeting Minutes and Verbali for: {project_context}")
    formatted_sections.append(f"Retrieved {len(documents)} documents from {len(docs_by_file)} files")
    formatted_sections.append("")
    
    # Format each file's content
    for file_name, file_docs in docs_by_file.items():
        formatted_sections.append(f"=== File: {file_name} ===")
        
        # Add metadata if available
        first_doc = file_docs[0]
        if 'last_modified_time' in first_doc.metadata:
            formatted_sections.append(f"Last Modified: {first_doc.metadata['last_modified_time']}")
        if 'webViewLink' in first_doc.metadata:
            formatted_sections.append(f"Document Link: {first_doc.metadata['webViewLink']}")
        
        formatted_sections.append("")
        
        # Add content chunks
        for i, doc in enumerate(file_docs, 1):
            content = doc.page_content.strip()
            if content:
                formatted_sections.append(f"--- Content {i} ---")
                formatted_sections.append(content)
                formatted_sections.append("")
    
    return "\n".join(formatted_sections)


class VerbaliRetriever:
    """
    High-level verbali retriever that provides a clean interface for the agent.
    """
    
    def __init__(self):
        self.config = get_config()
        self.project_manager = get_project_manager()
    
    def retrieve_for_project(
        self, 
        project_name: str, 
        user_query: Optional[str] = None
    ) -> VerbaliRetrievalResult:
        """Retrieve verbali for a single project"""
        return retrieve_verbali_for_project(
            project_name=project_name,
            user_query=user_query
        )
    
    def retrieve_for_projects(
        self, 
        project_names: List[str], 
        user_query: Optional[str] = None
    ) -> VerbaliRetrievalResult:
        """Retrieve verbali for multiple projects"""
        return retrieve_verbali_for_multiple_projects(
            project_names=project_names,
            user_query=user_query
        )
    
    def search_by_keywords(
        self, 
        keywords: str, 
        project_filter: Optional[str] = None
    ) -> VerbaliRetrievalResult:
        """Search verbali by keywords"""
        return search_verbali_by_keywords(
            keywords=keywords,
            project_filter=project_filter
        ) 