"""
Configuration module for the Multi-Source RAG System

This module handles all configuration loading, validation, and default settings
for the multi-source agent and its components.
"""

import os
from typing import Dict, Optional

from pydantic import BaseSettings, Field

from .models import AgentConfig, CollectionConfig, ToolConfig


class Config(BaseSettings):
    """
    Main configuration class for the Multi-Source RAG System.
    
    This class loads configuration from environment variables and provides
    default values for all system components.
    """
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("eu-central-1", env="AWS_REGION")
    
    # Vector Database Configuration
    qdrant_url: Optional[str] = Field(None, env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(None, env="QDRANT_API_KEY")
    
    # AWS Services
    athena_database: str = Field("metadata", env="ATHENA_DATABASE")
    athena_table: str = Field("catalogo_servizi", env="ATHENA_TABLE")
    athena_s3_output_location: str = Field("s3://default-bucket/query-results/", env="ATHENA_S3_OUTPUT_LOCATION")
    
    # S3 Configuration
    catalog_s3_bucket: str = Field("chatbotaistack-dataextractionstagingbucket31830e92-o4unjfsiz0o2", env="CATALOG_S3_BUCKET")
    catalog_s3_key: str = Field("Catalogo_servizi/catalogo_servizi.json", env="CATALOG_S3_KEY")
    
    # GraphQL Configuration
    graphql_url: Optional[str] = Field(None, env="GRAPHQL_URL")
    
    # DynamoDB Configuration
    table_name: Optional[str] = Field(None, env="TABLE_NAME")
    
    # Collection Names
    verbali_collection: str = Field("verbali", env="VERBALI_COLLECTION")
    sa_collection: str = Field("projects_sa", env="SA_COLLECTION")
    rfc_collection: str = Field("projects_rfc", env="RFC_COLLECTION")
    user_docs_collection: str = Field("user_docs", env="USER_DOCS_COLLECTION")
    mi_collection: str = Field("mi_installation_manuals", env="MI_COLLECTION")
    wiki_collection: str = Field("wiki_collection", env="WIKI_COLLECTION")
    project_desc_collection: str = Field("project_descriptions_v2", env="PROJECT_DESC_COLLECTION")
    
    # Agent Configuration
    model_id: str = Field("anthropic.claude-3-5-sonnet-20240620-v1:0", env="MODEL_ID")
    embedding_provider: str = Field("Bedrock-embeddings", env="EMBEDDING_PROVIDER")
    temperature: float = Field(0.2, env="TEMPERATURE")
    max_tokens: int = Field(4000, env="MAX_TOKENS")
    
    # Parallel Processing
    max_workers: int = Field(5, env="MAX_WORKERS")
    concurrent_requests: int = Field(10, env="CONCURRENT_REQUESTS")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Frontend Configuration
    frontend_type: str = Field("streamlit", env="FRONTEND_TYPE")
    
    # Semantic Search Configuration
    description_similarity_threshold: float = Field(0.85, env="DESCRIPTION_SIMILARITY_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_agent_config(self) -> AgentConfig:
        """Get the agent configuration with all necessary settings"""
        return AgentConfig(
            model_id=self.model_id,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_workers=self.max_workers,
            enable_context_filtering=True,
            enable_synthesis=True,
            collections=self._get_collection_configs(),
            tools=self._get_tool_configs()
        )
    
    def _get_collection_configs(self) -> Dict[str, CollectionConfig]:
        """Get configurations for all collections"""
        return {
            "verbali": CollectionConfig(
                collection_name=self.verbali_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="scroll",
                search_kwargs={"k": 20, "fetch_k": 50},
                metadata_fields=["webViewLink", "last_modified_time", "file_name", "project"]
            ),
            "sa": CollectionConfig(
                collection_name=self.sa_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="scroll",
                search_kwargs={"k": 20, "fetch_k": 50},
                metadata_fields=["webViewLink", "last_modified_time", "file_name", "project"]
            ),
            "rfc": CollectionConfig(
                collection_name=self.rfc_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="scroll",
                search_kwargs={"k": 20, "fetch_k": 50},
                metadata_fields=["webViewLink", "last_modified_time", "file_name", "project"]
            ),
            "user_docs": CollectionConfig(
                collection_name=self.user_docs_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 10},
                metadata_fields=["webViewLink", "last_modified_time", "file_name"]
            ),
            "mi": CollectionConfig(
                collection_name=self.mi_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="hybrid",
                search_kwargs={"k": 4, "fetch_k": 10},
                metadata_fields=["webViewLink", "last_modified_time", "file_name", "sheet_name", "all_sheets", "project"]
            ),
            "wiki": CollectionConfig(
                collection_name=self.wiki_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="scroll",
                search_kwargs={"k": 15, "fetch_k": 30},
                metadata_fields=["source_filename", "page_title", "chunk_number", "total_chunks", "project"]
            ),
            "project_desc": CollectionConfig(
                collection_name=self.project_desc_collection,
                enabled=True,
                embedding_provider=self.embedding_provider,
                search_type="similarity",
                search_kwargs={"k": 1},
                metadata_fields=["elemName", "description"]
            ),
        }
    
    def _get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get configurations for all tools"""
        return {
            "project_identifier": ToolConfig(
                tool_name="project_identifier",
                enabled=True,
                max_retries=3,
                timeout=30.0,
                parallel_execution=False,
                priority=10,
                parameters={
                    "similarity_threshold": self.description_similarity_threshold,
                    "use_llm_fallback": True,
                    "cache_results": True
                }
            ),
            "verbali_retriever": ToolConfig(
                tool_name="verbali_retriever",
                enabled=True,
                max_retries=2,
                timeout=45.0,
                parallel_execution=True,
                priority=8,
                parameters={
                    "use_scroll": True,
                    "include_metadata": True
                }
            ),
            "sa_retriever": ToolConfig(
                tool_name="sa_retriever",
                enabled=True,
                max_retries=2,
                timeout=45.0,
                parallel_execution=True,
                priority=7,
                parameters={
                    "use_scroll": True,
                    "include_metadata": True
                }
            ),
            "rfc_retriever": ToolConfig(
                tool_name="rfc_retriever",
                enabled=True,
                max_retries=2,
                timeout=45.0,
                parallel_execution=True,
                priority=7,
                parameters={
                    "use_scroll": True,
                    "include_metadata": True
                }
            ),
            "user_docs_retriever": ToolConfig(
                tool_name="user_docs_retriever",
                enabled=True,
                max_retries=2,
                timeout=30.0,
                parallel_execution=True,
                priority=6,
                parameters={
                    "use_mmr": True,
                    "include_metadata": True
                }
            ),
            "mi_retriever": ToolConfig(
                tool_name="mi_retriever",
                enabled=True,
                max_retries=2,
                timeout=60.0,
                parallel_execution=True,
                priority=8,
                parameters={
                    "use_llm_sheet_selection": True,
                    "include_metadata": True
                }
            ),
            "wiki_retriever": ToolConfig(
                tool_name="wiki_retriever",
                enabled=True,
                max_retries=2,
                timeout=45.0,
                parallel_execution=True,
                priority=7,
                parameters={
                    "use_scroll": True,
                    "include_metadata": True
                }
            ),
            "athena_query": ToolConfig(
                tool_name="athena_query",
                enabled=True,
                max_retries=2,
                timeout=120.0,
                parallel_execution=True,
                priority=9,
                parameters={
                    "max_poll_attempts": 10,
                    "poll_interval": 3,
                    "validate_sql": True
                }
            ),
            "information_synthesizer": ToolConfig(
                tool_name="information_synthesizer",
                enabled=True,
                max_retries=1,
                timeout=60.0,
                parallel_execution=False,
                priority=10,
                parameters={
                    "use_context_filtering": True,
                    "max_context_length": 8000,
                    "include_source_attribution": True
                }
            )
        }
    
    def get_collection_name(self, collection_type: str) -> str:
        """Get the collection name for a specific type"""
        collection_map = {
            "verbali": self.verbali_collection,
            "sa": self.sa_collection,
            "rfc": self.rfc_collection,
            "user_docs": self.user_docs_collection,
            "mi": self.mi_collection,
            "wiki": self.wiki_collection,
            "project_desc": self.project_desc_collection
        }
        return collection_map.get(collection_type, collection_type)
    
    def is_aws_configured(self) -> bool:
        """Check if AWS credentials are configured"""
        return bool(self.aws_access_key_id and self.aws_secret_access_key)
    
    def is_qdrant_configured(self) -> bool:
        """Check if Qdrant is configured"""
        return bool(self.qdrant_url)
    
    def is_anthropic_configured(self) -> bool:
        """Check if Anthropic is configured"""
        return bool(self.anthropic_api_key)
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.openai_api_key)
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present"""
        required_checks = [
            (self.is_qdrant_configured(), "Qdrant URL not configured"),
            (self.is_aws_configured(), "AWS credentials not configured"),
            (self.is_anthropic_configured() or self.is_openai_configured(), "No LLM provider configured")
        ]
        
        for check, message in required_checks:
            if not check:
                print(f"Configuration error: {message}")
                return False
        
        return True


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def reload_config() -> Config:
    """Reload configuration from environment"""
    global config
    config = Config()
    return config 