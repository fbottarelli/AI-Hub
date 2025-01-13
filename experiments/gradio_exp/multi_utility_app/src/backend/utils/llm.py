import logging
from langchain_openai import ChatOpenAI
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