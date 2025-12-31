"""LLM factory for creating language model instances"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel

from ..config import settings


def create_llm(
    provider: str = None,
    model: str = None,
    temperature: float = 0.0
) -> BaseChatModel:
    """
    Create an LLM instance based on provider configuration.
    
    Args:
        provider: LLM provider (openai, anthropic, groq). Defaults to settings.
        model: Model name. Defaults to settings.
        temperature: Temperature for generation. Default 0 for deterministic output.
    
    Returns:
        Configured LLM instance
    """
    provider = provider or settings.LLM_PROVIDER
    model = model or settings.MODEL_NAME
    
    if provider == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.ANTHROPIC_API_KEY
        )
    elif provider == "groq":
        return ChatGroq(
            model=model,
            temperature=temperature,
            api_key=settings.GROQ_API_KEY,
            max_retries=5
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_json_llm(provider: str = None, model: str = None) -> BaseChatModel:
    """
    Create an LLM instance configured for JSON output.
    
    Args:
        provider: LLM provider
        model: Model name
    
    Returns:
        LLM configured with JSON mode
    """
    llm = create_llm(provider, model, temperature=0.0)
    
    # Enable JSON mode if supported
    if hasattr(llm, 'model_kwargs'):
        llm.model_kwargs = {"response_format": {"type": "json_object"}}
    
    return llm
