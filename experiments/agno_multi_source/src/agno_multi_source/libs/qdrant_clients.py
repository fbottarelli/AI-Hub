"""
Qdrant Clients for Multi-Source RAG System

This module provides centralized Qdrant client management with proper configuration
and connection handling for vector database operations.
"""

import logging
from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models

from ..config import get_config
from ..models import CollectionConfig

logger = logging.getLogger(__name__)


class QdrantClients:
    """
    Centralized Qdrant client manager.
    
    Provides singleton access to Qdrant collections with proper configuration
    and error handling.
    """
    
    def __init__(self):
        self.config = get_config()
        self._client = None
        self._vectorstores: Dict[str, Qdrant] = {}
        self._embedding_models: Dict[str, any] = {}
    
    @property
    def client(self) -> QdrantClient:
        """Get or create the Qdrant client"""
        if self._client is None:
            try:
                self._client = QdrantClient(
                    url=self.config.qdrant_url,
                    api_key=self.config.qdrant_api_key
                )
                logger.info(f"Created Qdrant client for URL: {self.config.qdrant_url}")
            except Exception as e:
                logger.error(f"Failed to create Qdrant client: {e}")
                raise
        
        return self._client
    
    def get_embedding_model(self, embeddings_type: str = "Bedrock-embeddings"):
        """Get or create an embedding model"""
        if embeddings_type not in self._embedding_models:
            try:
                if embeddings_type == "Bedrock-embeddings":
                    from langchain_aws import BedrockEmbeddings
                    self._embedding_models[embeddings_type] = BedrockEmbeddings(
                        model_id="amazon.titan-embed-text-v1",
                        region_name=self.config.aws_region
                    )
                elif embeddings_type == "OpenAI-embeddings":
                    from langchain_openai import OpenAIEmbeddings
                    self._embedding_models[embeddings_type] = OpenAIEmbeddings()
                else:
                    raise ValueError(f"Unsupported embeddings type: {embeddings_type}")
                
                logger.debug(f"Created embedding model: {embeddings_type}")
            except Exception as e:
                logger.error(f"Failed to create embedding model {embeddings_type}: {e}")
                raise
        
        return self._embedding_models[embeddings_type]
    
    def create_collection(self, collection_name: str, vector_size: int = 1024):
        """Create a collection if it doesn't exist"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, 
                    distance=models.Distance.COSINE
                ),
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            # Collection might already exist
            logger.debug(f"Collection {collection_name} might already exist: {e}")
    
    def get_vectorstore(self, collection_config: CollectionConfig) -> Qdrant:
        """Get or create a vectorstore for a collection"""
        collection_name = collection_config.collection_name
        
        if collection_name not in self._vectorstores:
            try:
                # Ensure collection exists
                self.create_collection(collection_name)
                
                # Get embedding model
                embeddings = self.get_embedding_model(collection_config.embedding_provider)
                
                # Create vectorstore
                vectorstore = Qdrant(
                    client=self.client,
                    collection_name=collection_name,
                    embeddings=embeddings,
                )
                
                self._vectorstores[collection_name] = vectorstore
                logger.debug(f"Created vectorstore for collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to create vectorstore for {collection_name}: {e}")
                raise
        
        return self._vectorstores[collection_name]
    
    def scroll_all_documents_for_project(
        self, 
        collection_name: str, 
        project_filter_dict: Dict[str, str]
    ) -> List[Document]:
        """
        Retrieve ALL documents for a project using Qdrant scroll.
        This is the unified approach for MI, SA, RFC, and Verbali collections.
        """
        if not project_filter_dict:
            logger.warning(f"No project filter provided for collection {collection_name}")
            return []
        
        try:
            # Build the filter conditions from the project_filter_dict
            filter_conditions = []
            for key, value in project_filter_dict.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=f"metadata.{key}",  # Access nested metadata field
                        match=models.MatchValue(value=value)
                    )
                )
            
            scroll_filter = models.Filter(must=filter_conditions)
            
            # Scroll through all points with the filter
            all_points = []
            offset = None
            
            while True:
                result = self.client.scroll(
                    collection_name=collection_name,
                    scroll_filter=scroll_filter,
                    limit=100,  # Process in batches of 100
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                
                points, next_offset = result
                all_points.extend(points)
                
                # If no more points, break
                if next_offset is None:
                    break
                offset = next_offset
            
            # Convert Qdrant points to Langchain Documents
            documents = []
            for point in all_points:
                # Extract content and metadata from the point
                page_content = point.payload.get("page_content", "")
                metadata = point.payload.get("metadata", {})
                
                # Create Langchain Document
                doc = Document(
                    page_content=page_content,
                    metadata=metadata
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from {collection_name} for project filter: {project_filter_dict}")
            return documents
            
        except Exception as e:
            logger.error(f"Error scrolling documents from {collection_name}: {e}")
            return []
    
    def similarity_search(
        self, 
        collection_config: CollectionConfig, 
        query: str, 
        k: int = 5,
        filter_dict: Optional[Dict[str, str]] = None
    ) -> List[Document]:
        """Perform similarity search on a collection"""
        try:
            vectorstore = self.get_vectorstore(collection_config)
            
            search_kwargs = {"k": k}
            if filter_dict:
                search_kwargs["filter"] = filter_dict
            
            # Merge with collection-specific search kwargs
            search_kwargs.update(collection_config.search_kwargs)
            
            # Perform search based on search type
            if collection_config.search_type == "mmr":
                documents = vectorstore.max_marginal_relevance_search(
                    query, 
                    k=search_kwargs.get("k", k),
                    fetch_k=search_kwargs.get("fetch_k", k * 2)
                )
            elif collection_config.search_type == "similarity_score_threshold":
                documents = vectorstore.similarity_search_with_score_threshold(
                    query,
                    score_threshold=search_kwargs.get("score_threshold", 0.5),
                    k=search_kwargs.get("k", k)
                )
                # Extract just the documents (without scores)
                documents = [doc for doc, score in documents] if documents else []
            else:
                # Default similarity search
                documents = vectorstore.similarity_search(query, **search_kwargs)
            
            logger.debug(f"Found {len(documents)} documents in {collection_config.collection_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error during similarity search in {collection_config.collection_name}: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        collection_config: CollectionConfig,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, str]] = None
    ) -> List[tuple]:
        """Perform similarity search with scores"""
        try:
            vectorstore = self.get_vectorstore(collection_config)
            
            search_kwargs = {"k": k}
            if filter_dict:
                search_kwargs["filter"] = filter_dict
            
            # Merge with collection-specific search kwargs
            search_kwargs.update(collection_config.search_kwargs)
            
            results = vectorstore.similarity_search_with_score(query, **search_kwargs)
            logger.debug(f"Found {len(results)} documents with scores in {collection_config.collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error during similarity search with score in {collection_config.collection_name}: {e}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Optional[dict]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            logger.debug(f"Retrieved info for collection: {collection_name}")
            return info
        except Exception as e:
            logger.error(f"Failed to get info for collection {collection_name}: {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            logger.debug(f"Found {len(collection_names)} collections")
            return collection_names
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test Qdrant connection"""
        try:
            # Try to get cluster info
            info = self.client.get_cluster_info()
            logger.info("Qdrant connection test successful")
            return True
        except Exception as e:
            logger.error(f"Qdrant connection test failed: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validate Qdrant configuration and connectivity"""
        if not self.config.is_qdrant_configured():
            logger.error("Qdrant URL not configured")
            return False
        
        # Test connection
        if not self.test_connection():
            logger.error("Qdrant connection test failed")
            return False
        
        # Validate that required collections exist
        available_collections = self.list_collections()
        agent_config = self.config.get_agent_config()
        
        missing_collections = []
        for collection_type, collection_config in agent_config.collections.items():
            if collection_config.enabled and collection_config.collection_name not in available_collections:
                missing_collections.append(collection_config.collection_name)
        
        if missing_collections:
            logger.warning(f"Some required collections are missing: {missing_collections}")
            # Note: We don't return False here as collections might be created dynamically
        
        logger.info("Qdrant configuration validation passed")
        return True


# Global singleton instance
_qdrant_clients_instance: Optional[QdrantClients] = None


def get_qdrant_clients() -> QdrantClients:
    """Get or create the global Qdrant clients singleton"""
    global _qdrant_clients_instance
    if _qdrant_clients_instance is None:
        _qdrant_clients_instance = QdrantClients()
    return _qdrant_clients_instance 