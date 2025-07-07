"""
Multi-Source RAG Agent

This module implements the main agent that orchestrates project identification,
parallel retrieval from multiple sources, and information synthesis to provide
comprehensive answers to user queries.
"""

import logging
import time
from typing import Dict, List, Optional, Union

from agno import Agent
from pydantic import BaseModel, Field

from .config import get_config
from .models import (
    AgentConfig,
    AgentState,
    PerformanceMetrics,
    QueryContext,
    QueryType,
    RetrievalResult,
    SourceType,
    SynthesisResult,
)
from .tools.project_tools import (
    ProjectIdentifier,
    ProjectValidator,
    identify_project_from_query,
)
from .tools.verbali_tools import VerbaliRetriever, retrieve_verbali_for_project
from .tools.athena_tools import AthenaQueryTool, query_project_details

logger = logging.getLogger(__name__)


class MultiSourceAgent:
    """
    Main multi-source RAG agent that provides intelligent information retrieval
    and synthesis across multiple data sources.
    
    This agent:
    1. Identifies relevant projects from user queries
    2. Retrieves information from 5 parallel sources
    3. Synthesizes information into comprehensive answers
    4. Maintains conversation context
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the multi-source agent.
        
        Args:
            config: Optional agent configuration. If not provided, uses default from config.
        """
        self.config = config or get_config().get_agent_config()
        self.system_config = get_config()
        
        # Initialize tools
        self.project_identifier = ProjectIdentifier()
        self.project_validator = ProjectValidator()
        
        # Initialize retrievers
        self.verbali_retriever = VerbaliRetriever()
        self.athena_tool = AthenaQueryTool()
        
        # State management
        self.current_state: Optional[AgentState] = None
        self.conversation_context: Dict[str, any] = {}
        
        # Create the underlying Agno agent
        self._agent = self._create_agent()
        
        logger.info("MultiSourceAgent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the underlying Agno agent with tools"""
        
        # Define the system prompt
        system_prompt = """
        You are an expert AI assistant for company employees, communicating in Italian. 
        Your primary goal is to provide accurate and helpful answers based on the user's 
        question, conversation history, and information retrieved using your available tools.

        Your available tools allow you to:
        1. Identify relevant projects from user queries
        2. Retrieve information from multiple sources:
           - Meeting minutes and verbali
           - Project catalog (Athena database)
           - User documents
           - Installation manuals (MI)
           - Wiki knowledge base
        3. Synthesize information from multiple sources

        Processing Steps:
        1. ALWAYS start by identifying the project context using identify_project_from_query
        2. Based on the query and project context, decide which retrieval tools to use
        3. Call relevant retrieval tools (you can call multiple tools in parallel)
        4. Synthesize the information to provide a comprehensive answer
        5. Always respond in Italian
        6. Cite sources when providing specific information

        Guidelines:
        - If Athena/catalog data is available, prioritize it for structured information
        - Use verbali for meeting decisions and discussions
        - Provide specific, actionable information when possible
        - If information is not available, clearly state this
        - Maintain conversation context across turns
        """
        
        # Create agent with tools
        agent = Agent(
            model=self.config.model_id,
            instructions=system_prompt,
            tools=[
                identify_project_from_query,
                retrieve_verbali_for_project,
                query_project_details,
                # Add more tools as they become available
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        return agent
    
    def process_query(
        self,
        user_query: str,
        user_id: str,
        chat_id: str,
        conversation_history: Optional[List[Dict]] = None,
        last_project_context: Optional[str] = None
    ) -> SynthesisResult:
        """
        Process a user query through the complete multi-source RAG pipeline.
        
        Args:
            user_query: The user's question or request
            user_id: Unique identifier for the user
            chat_id: Unique identifier for the chat session
            conversation_history: Previous conversation turns
            last_project_context: Project context from the previous turn
            
        Returns:
            SynthesisResult with the complete response and metadata
        """
        start_time = time.time()
        
        logger.info(f"Processing query for user {user_id}: '{user_query[:100]}...'")
        
        try:
            # Step 1: Create query context
            query_context = QueryContext(
                user_query=user_query,
                processed_query=user_query,  # Could add query processing here
                query_type=QueryType.GENERAL,  # Will be determined by tools
                identified_projects="general",  # Will be determined by tools
                conversation_history=conversation_history or [],
                user_id=user_id,
                chat_id=chat_id
            )
            
            # Step 2: Initialize agent state
            self.current_state = AgentState(
                query_context=query_context,
                processing_stage="initialized"
            )
            
            # Step 3: Use the Agno agent to process the query
            # The agent will automatically use tools to identify projects and retrieve information
            response = self._agent.run(
                user_query,
                context={
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "conversation_history": conversation_history,
                    "last_project_context": last_project_context
                }
            )
            
            # Step 4: Create synthesis result
            processing_time = time.time() - start_time
            
            synthesis_result = SynthesisResult(
                query_context=query_context,
                retrieval_results=[],  # Tools will populate this
                synthesized_content=response.content,
                confidence_score=0.8,  # Could be calculated based on tool results
                sources_used=[],  # Tools will populate this
                processing_time=processing_time,
                token_usage={"total": response.usage.total_tokens} if hasattr(response, 'usage') else {}
            )
            
            # Step 5: Update state
            self.current_state.synthesis_result = synthesis_result
            self.current_state.processing_stage = "completed"
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            
            return synthesis_result
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Return error result
            processing_time = time.time() - start_time
            return SynthesisResult(
                query_context=query_context,
                retrieval_results=[],
                synthesized_content=f"Mi dispiace, si è verificato un errore durante l'elaborazione della tua richiesta: {error_msg}",
                confidence_score=0.0,
                sources_used=[],
                processing_time=processing_time,
                token_usage={}
            )
    
    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Get performance metrics for the last processed query"""
        if not self.current_state or not self.current_state.synthesis_result:
            return None
        
        synthesis_result = self.current_state.synthesis_result
        
        return PerformanceMetrics(
            total_processing_time=synthesis_result.processing_time,
            project_identification_time=0.0,  # Would need to track this
            retrieval_time=0.0,  # Would need to track this
            synthesis_time=0.0,  # Would need to track this
            token_usage=synthesis_result.token_usage,
            api_calls={},  # Would need to track this
            success_rate=1.0 if synthesis_result.confidence_score > 0.5 else 0.0,
            error_count=len(self.current_state.error_messages)
        )
    
    def validate_configuration(self) -> bool:
        """Validate that the agent is properly configured"""
        try:
            # Validate system configuration
            if not self.system_config.validate_configuration():
                logger.error("System configuration validation failed")
                return False
            
            # Validate tools
            # This would check that all required tools are available and configured
            logger.info("Agent configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def get_conversation_context(self) -> Dict[str, any]:
        """Get the current conversation context"""
        return self.conversation_context.copy()
    
    def update_conversation_context(self, key: str, value: any) -> None:
        """Update conversation context"""
        self.conversation_context[key] = value
        logger.debug(f"Updated conversation context: {key}")
    
    def clear_conversation_context(self) -> None:
        """Clear conversation context"""
        self.conversation_context.clear()
        logger.debug("Cleared conversation context")


class SimpleMultiSourceAgent:
    """
    Simplified version of the multi-source agent for direct tool usage.
    
    This version manually orchestrates the tools without using the Agno framework,
    useful for debugging and understanding the flow.
    """
    
    def __init__(self):
        self.config = get_config()
        self.project_identifier = ProjectIdentifier()
        self.verbali_retriever = VerbaliRetriever()
        self.athena_tool = AthenaQueryTool()
    
    def process_query_simple(
        self,
        user_query: str,
        last_project_context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Simple query processing that demonstrates the multi-source flow.
        
        Args:
            user_query: The user's question
            last_project_context: Previous project context
            
        Returns:
            Dictionary with results from each step
        """
        results = {
            "user_query": user_query,
            "project_identification": None,
            "verbali_results": None,
            "athena_results": None,
            "final_answer": ""
        }
        
        try:
            # Step 1: Identify project
            logger.info("Step 1: Identifying project context")
            project_result = self.project_identifier.identify(
                user_query=user_query,
                last_project_context=last_project_context
            )
            results["project_identification"] = project_result
            
            identified_project = project_result.identified_projects
            logger.info(f"Identified project: {identified_project}")
            
            # Step 2: Retrieve verbali if we have a specific project
            if identified_project != "general":
                logger.info("Step 2: Retrieving verbali documents")
                verbali_result = self.verbali_retriever.retrieve_for_project(
                    project_name=identified_project,
                    user_query=user_query
                )
                results["verbali_results"] = verbali_result
                
                # Step 3: Query Athena for project details
                logger.info("Step 3: Querying Athena for project details")
                athena_result = self.athena_tool.query_project(identified_project)
                results["athena_results"] = athena_result
            
            # Step 4: Create simple synthesis
            answer_parts = []
            
            if identified_project == "general":
                answer_parts.append("La tua domanda è di carattere generale. ")
            else:
                answer_parts.append(f"Ho trovato informazioni per il progetto: {identified_project}")
            
            if results["athena_results"] and results["athena_results"].success:
                answer_parts.append("Informazioni dal catalogo servizi disponibili.")
            
            if results["verbali_results"] and results["verbali_results"].success:
                answer_parts.append(f"Trovati {results['verbali_results'].document_count} documenti verbali.")
            
            results["final_answer"] = " ".join(answer_parts)
            
            logger.info("Simple query processing completed successfully")
            
        except Exception as e:
            error_msg = f"Errore durante l'elaborazione: {str(e)}"
            logger.error(error_msg, exc_info=True)
            results["final_answer"] = error_msg
        
        return results


def create_agent(config: Optional[AgentConfig] = None) -> MultiSourceAgent:
    """
    Factory function to create a configured multi-source agent.
    
    Args:
        config: Optional agent configuration
        
    Returns:
        Configured MultiSourceAgent instance
    """
    agent = MultiSourceAgent(config)
    
    # Validate configuration
    if not agent.validate_configuration():
        raise RuntimeError("Agent configuration validation failed")
    
    return agent 