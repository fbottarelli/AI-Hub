"""
Project Identification and Validation Tools

This module provides Agno tools for identifying and validating projects
from user queries using multiple methods including semantic search and LLM analysis.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Union

from agno import tool
from pydantic import BaseModel, Field

from ..config import get_config
from ..libs.project_manager import get_project_manager
from ..libs.qdrant_clients import get_qdrant_clients
from ..models import ProjectInfo, QueryContext, QueryType

logger = logging.getLogger(__name__)


class ProjectIdentificationResult(BaseModel):
    """Result from project identification"""
    identified_projects: Union[str, List[str]] = Field(..., description="Identified project(s)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    method: str = Field(..., description="Method used for identification")
    context_changed: bool = Field(default=True, description="Whether context changed from previous")
    
    
class ProjectValidationResult(BaseModel):
    """Result from project validation"""
    valid_projects: List[str] = Field(..., description="Valid canonical project names")
    invalid_projects: List[str] = Field(..., description="Invalid project names")
    normalized_projects: Dict[str, str] = Field(..., description="Mapping of input to canonical names")


@tool
def identify_project_from_query(
    user_query: str,
    conversation_history: Optional[List[Dict]] = None,
    last_project_context: Optional[str] = None
) -> ProjectIdentificationResult:
    """
    Identify relevant project(s) from a user query using multiple methods.
    
    This tool uses:
    1. Semantic search against project descriptions
    2. LLM-based extraction and validation
    3. Context change detection
    
    Args:
        user_query: The user's question or request
        conversation_history: Previous conversation turns for context
        last_project_context: Previous project context to check for changes
        
    Returns:
        ProjectIdentificationResult with identified projects and metadata
    """
    start_time = time.time()
    config = get_config()
    project_manager = get_project_manager()
    qdrant_clients = get_qdrant_clients()
    
    logger.info(f"Identifying project for query: '{user_query[:100]}...'")
    
    # Step 1: Try semantic search for project descriptions
    try:
        project_desc_config = config.get_agent_config().collections.get("project_desc")
        if project_desc_config and project_desc_config.enabled:
            logger.debug("Attempting semantic search for project descriptions")
            
            search_results = qdrant_clients.similarity_search_with_score(
                collection_config=project_desc_config,
                query=user_query,
                k=1
            )
            
            if search_results:
                doc, score = search_results[0]
                logger.info(f"Semantic search score: {score:.4f}")
                
                if score >= config.description_similarity_threshold:
                    elem_name = doc.metadata.get("elemName")
                    if elem_name:
                        canonical_name = project_manager.get_canonical_name(elem_name)
                        if canonical_name:
                            logger.info(f"Project identified via semantic search: {canonical_name}")
                            return ProjectIdentificationResult(
                                identified_projects=canonical_name,
                                confidence=score,
                                method="semantic_search",
                                context_changed=True
                            )
    except Exception as e:
        logger.warning(f"Semantic search failed: {e}")
    
    # Step 2: Check for context change if we have previous context
    if last_project_context and last_project_context != "general":
        try:
            from ..tools.llm_tools import check_project_context_change
            
            context_changed = check_project_context_change(
                user_query=user_query,
                last_project=last_project_context
            )
            
            if not context_changed:
                logger.info(f"Context unchanged, reusing: {last_project_context}")
                return ProjectIdentificationResult(
                    identified_projects=last_project_context,
                    confidence=0.8,
                    method="context_reuse",
                    context_changed=False
                )
        except Exception as e:
            logger.warning(f"Context change detection failed: {e}")
    
    # Step 3: LLM-based project extraction
    try:
        from ..tools.llm_tools import extract_projects_from_query
        
        known_projects = project_manager.get_all_canonical_names()
        
        llm_result = extract_projects_from_query(
            user_query=user_query,
            known_projects=known_projects,
            conversation_history=conversation_history
        )
        
        if llm_result.get("projects"):
            projects = llm_result["projects"]
            
            # Validate and normalize projects
            if isinstance(projects, str):
                if projects.lower() == "general":
                    return ProjectIdentificationResult(
                        identified_projects="general",
                        confidence=0.9,
                        method="llm_extraction",
                        context_changed=True
                    )
                else:
                    canonical = project_manager.get_canonical_name(projects)
                    if canonical:
                        return ProjectIdentificationResult(
                            identified_projects=canonical,
                            confidence=0.8,
                            method="llm_extraction",
                            context_changed=True
                        )
            elif isinstance(projects, list):
                valid_projects, _ = project_manager.validate_and_normalize_list(projects)
                if valid_projects:
                    return ProjectIdentificationResult(
                        identified_projects=valid_projects,
                        confidence=0.8,
                        method="llm_extraction",
                        context_changed=True
                    )
    except Exception as e:
        logger.warning(f"LLM project extraction failed: {e}")
    
    # Step 4: Fallback to general context
    logger.info("No specific project identified, defaulting to general")
    return ProjectIdentificationResult(
        identified_projects="general",
        confidence=0.5,
        method="fallback",
        context_changed=True
    )


@tool
def validate_project_names(project_names: Union[str, List[str]]) -> ProjectValidationResult:
    """
    Validate and normalize project names using the project manager.
    
    Args:
        project_names: Single project name or list of project names to validate
        
    Returns:
        ProjectValidationResult with validation results and normalized names
    """
    project_manager = get_project_manager()
    
    # Normalize input to list
    if isinstance(project_names, str):
        input_projects = [project_names]
    else:
        input_projects = project_names
    
    valid_projects = []
    invalid_projects = []
    normalized_projects = {}
    
    for project_name in input_projects:
        canonical = project_manager.get_canonical_name(project_name)
        if canonical:
            valid_projects.append(canonical)
            normalized_projects[project_name] = canonical
        else:
            invalid_projects.append(project_name)
    
    logger.info(f"Validated {len(valid_projects)} valid projects out of {len(input_projects)}")
    
    return ProjectValidationResult(
        valid_projects=valid_projects,
        invalid_projects=invalid_projects,
        normalized_projects=normalized_projects
    )


@tool
def get_project_information(project_name: str) -> Optional[ProjectInfo]:
    """
    Get detailed information about a specific project.
    
    Args:
        project_name: Name of the project to look up
        
    Returns:
        ProjectInfo object with detailed project information, or None if not found
    """
    project_manager = get_project_manager()
    
    project_info = project_manager.get_project_info(project_name)
    if project_info:
        logger.info(f"Retrieved information for project: {project_info.canonical_name}")
    else:
        logger.warning(f"No information found for project: {project_name}")
    
    return project_info


@tool
def search_projects_by_query(query: str, limit: int = 10) -> List[str]:
    """
    Search for projects using fuzzy matching on names and aliases.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of canonical project names matching the query
    """
    project_manager = get_project_manager()
    
    results = project_manager.search_projects(query, limit)
    logger.info(f"Found {len(results)} projects matching query: '{query}'")
    
    return results


@tool
def get_all_active_projects() -> List[str]:
    """
    Get a list of all active project names.
    
    Returns:
        List of canonical names for all active projects
    """
    project_manager = get_project_manager()
    
    projects = project_manager.get_active_projects()
    logger.info(f"Retrieved {len(projects)} active projects")
    
    return projects


class ProjectIdentifier:
    """
    High-level project identifier that orchestrates the identification process.
    
    This class provides a simple interface for the agent to identify projects
    from queries while handling all the complexity internally.
    """
    
    def __init__(self):
        self.config = get_config()
        self.project_manager = get_project_manager()
    
    def identify(
        self, 
        user_query: str, 
        conversation_history: Optional[List[Dict]] = None,
        last_project_context: Optional[str] = None
    ) -> ProjectIdentificationResult:
        """Main identification method"""
        return identify_project_from_query(
            user_query=user_query,
            conversation_history=conversation_history,
            last_project_context=last_project_context
        )


class ProjectValidator:
    """
    High-level project validator for normalizing and validating project names.
    """
    
    def __init__(self):
        self.project_manager = get_project_manager()
    
    def validate(self, project_names: Union[str, List[str]]) -> ProjectValidationResult:
        """Main validation method"""
        return validate_project_names(project_names)
    
    def is_valid(self, project_name: str) -> bool:
        """Check if a single project name is valid"""
        return self.project_manager.validate_project_name(project_name)
    
    def normalize(self, project_name: str) -> Optional[str]:
        """Get canonical name for a project"""
        return self.project_manager.get_canonical_name(project_name) 