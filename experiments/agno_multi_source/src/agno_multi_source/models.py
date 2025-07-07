"""
Core data models for the Multi-Source RAG System

This module defines the data structures used throughout the system for:
- Project information and context
- Query processing and results
- Retrieval and synthesis results
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator


class ProjectNameField(Enum):
    """Enum defining the standard field names used across different components"""
    ATHENA_ELEMNAME = "elemname"  # Used in Athena SQL queries
    S3_ELEMNAME = "elemName"     # Used in S3 catalog JSON
    MI_PROJECT = "project"       # Used in MI collection metadata
    WIKI_PROJECT = "project"     # Used in wiki collection metadata
    VERBALI_PROJECT = "project"  # Used in verbali collection metadata
    SA_PROJECT = "project"       # Used in SA collection metadata
    RFC_PROJECT = "project"      # Used in RFC collection metadata


class SourceType(Enum):
    """Enumeration of available data sources"""
    VERBALI = "verbali"
    SA_DOCUMENTS = "sa_documents"
    RFC_DOCUMENTS = "rfc_documents"
    USER_DOCUMENTS = "user_documents"
    MI_DOCUMENTS = "mi_documents"
    WIKI_DOCUMENTS = "wiki_documents"
    ATHENA_CATALOG = "athena_catalog"


class QueryType(Enum):
    """Enumeration of query types for better routing"""
    PROJECT_SPECIFIC = "project_specific"
    MULTI_PROJECT = "multi_project"
    GENERAL = "general"
    CONTACT_SEARCH = "contact_search"
    SERVICES_LIST = "services_list"
    TECHNICAL_PROCEDURE = "technical_procedure"


class ProjectInfo(BaseModel):
    """Standardized project information"""
    canonical_name: str = Field(..., description="The official project name")
    display_name: str = Field(..., description="Human-readable display name")
    aliases: Set[str] = Field(default_factory=set, description="Alternative names/variations")
    is_active: bool = Field(default=True, description="Whether the project is currently active")
    description: Optional[str] = Field(None, description="Project description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('aliases', pre=True)
    def ensure_aliases_set(cls, v):
        if isinstance(v, list):
            return set(v)
        return v if isinstance(v, set) else set()
    
    def model_post_init(self, __context):
        """Ensure aliases includes canonical and display names"""
        self.aliases.add(self.canonical_name)
        if self.display_name:
            self.aliases.add(self.display_name)


class QueryContext(BaseModel):
    """Context information for processing queries"""
    user_query: str = Field(..., description="Original user question")
    processed_query: str = Field(..., description="Processed/cleaned query")
    query_type: QueryType = Field(..., description="Type of query")
    identified_projects: Union[str, List[str]] = Field(..., description="Identified project(s)")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Chat history")
    user_id: str = Field(..., description="User identifier")
    chat_id: str = Field(..., description="Chat session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Query timestamp")
    
    @validator('identified_projects')
    def validate_projects(cls, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return [str(p) for p in v]
        else:
            return str(v)


class RetrievalResult(BaseModel):
    """Result from a single source retrieval operation"""
    source: SourceType = Field(..., description="Source that provided the data")
    success: bool = Field(..., description="Whether retrieval was successful")
    data: Optional[str] = Field(None, description="Retrieved data content")
    raw_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Raw document objects")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    retrieval_time: float = Field(..., description="Time taken for retrieval in seconds")
    document_count: int = Field(default=0, description="Number of documents retrieved")
    
    @validator('document_count', pre=True, always=True)
    def set_document_count(cls, v, values):
        if v == 0 and 'raw_documents' in values:
            return len(values['raw_documents'])
        return v


class SynthesisResult(BaseModel):
    """Result from information synthesis across multiple sources"""
    query_context: QueryContext = Field(..., description="Original query context")
    retrieval_results: List[RetrievalResult] = Field(..., description="Results from all sources")
    synthesized_content: str = Field(..., description="Final synthesized answer")
    confidence_score: float = Field(..., description="Confidence in the synthesis", ge=0.0, le=1.0)
    sources_used: List[SourceType] = Field(..., description="Sources that contributed to the answer")
    processing_time: float = Field(..., description="Total processing time in seconds")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")
    
    @validator('sources_used', pre=True, always=True)
    def extract_sources_used(cls, v, values):
        if not v and 'retrieval_results' in values:
            return [result.source for result in values['retrieval_results'] if result.success]
        return v


class AgentState(BaseModel):
    """State maintained by the agent during processing"""
    query_context: QueryContext = Field(..., description="Query context")
    project_info: Optional[ProjectInfo] = Field(None, description="Identified project information")
    retrieval_results: List[RetrievalResult] = Field(default_factory=list, description="Retrieval results")
    synthesis_result: Optional[SynthesisResult] = Field(None, description="Final synthesis result")
    processing_stage: str = Field(default="initialized", description="Current processing stage")
    error_messages: List[str] = Field(default_factory=list, description="Any error messages")
    
    class Config:
        arbitrary_types_allowed = True


class ToolConfig(BaseModel):
    """Configuration for individual tools"""
    tool_name: str = Field(..., description="Name of the tool")
    enabled: bool = Field(default=True, description="Whether the tool is enabled")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    timeout: float = Field(default=30.0, description="Timeout in seconds")
    parallel_execution: bool = Field(default=True, description="Whether to run in parallel")
    priority: int = Field(default=1, description="Execution priority (higher = more important)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific parameters")


class CollectionConfig(BaseModel):
    """Configuration for vector database collections"""
    collection_name: str = Field(..., description="Name of the collection")
    enabled: bool = Field(default=True, description="Whether the collection is enabled")
    embedding_provider: str = Field(default="Bedrock-embeddings", description="Embedding provider")
    search_type: str = Field(default="similarity", description="Search type (similarity, mmr, etc.)")
    search_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Search parameters")
    metadata_fields: List[str] = Field(default_factory=list, description="Metadata fields to include")


class AgentConfig(BaseModel):
    """Configuration for the multi-source agent"""
    model_id: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0", description="LLM model ID")
    temperature: float = Field(default=0.2, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    max_workers: int = Field(default=5, description="Maximum parallel workers")
    enable_context_filtering: bool = Field(default=True, description="Enable context filtering")
    enable_synthesis: bool = Field(default=True, description="Enable information synthesis")
    
    # Collection configurations
    collections: Dict[str, CollectionConfig] = Field(default_factory=dict, description="Collection configurations")
    
    # Tool configurations
    tools: Dict[str, ToolConfig] = Field(default_factory=dict, description="Tool configurations")
    
    def get_collection_config(self, collection_name: str) -> Optional[CollectionConfig]:
        """Get configuration for a specific collection"""
        return self.collections.get(collection_name)
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool"""
        return self.tools.get(tool_name)


class PerformanceMetrics(BaseModel):
    """Performance metrics for monitoring and optimization"""
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    project_identification_time: float = Field(..., description="Time for project identification")
    retrieval_time: float = Field(..., description="Time for all retrievals")
    synthesis_time: float = Field(..., description="Time for synthesis")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage by model")
    api_calls: Dict[str, int] = Field(default_factory=dict, description="API calls by service")
    success_rate: float = Field(..., description="Success rate (0.0 to 1.0)")
    error_count: int = Field(default=0, description="Number of errors encountered")
    
    class Config:
        arbitrary_types_allowed = True 