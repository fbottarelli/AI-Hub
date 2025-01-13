import logging
from pathlib import Path
from typing import Any, Optional, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

logger = logging.getLogger(__name__)

def call_llm(prompt: str, temperature: float = 0.7) -> str:
    """Common function to call LLM with error handling"""
    try:
        chat = ChatOpenAI(temperature=temperature)
        messages = [HumanMessage(content=prompt)]
        response = chat.invoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        return f"Error: {str(e)}"

def sanitize_filename(title: str) -> str:
    """Sanitize a string to be used as a filename"""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)

def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS format"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def handle_error(e: Exception, context: str = "") -> Tuple[None, str]:
    """Common error handling function"""
    error_msg = f"Error{f' in {context}' if context else ''}: {str(e)}"
    logger.error(error_msg, exc_info=True)
    return None, error_msg 