"""
Agno Multi-Source RAG System

An intelligent multi-source chatbot that identifies projects from questions and 
retrieves information from multiple data sources in parallel, then combines the 
information for comprehensive answers.
"""

__version__ = "0.1.0"
__author__ = "AI Hub Team"

from .agent import MultiSourceAgent
from .config import Config
from .models import (
    ProjectInfo,
    QueryContext,
    RetrievalResult,
    SynthesisResult,
)

__all__ = [
    "MultiSourceAgent",
    "Config", 
    "ProjectInfo",
    "QueryContext",
    "RetrievalResult",
    "SynthesisResult",
] 