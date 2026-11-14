import os
from typing import Any, Dict
from abc import ABC, abstractmethod

class LLM_Wrapper(ABC):
    """
    Abstract base class for interacting with different LLM providers.
    """
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass

class Claude_Wrapper(LLM_Wrapper):
    """
    Implementation for Anthropic's Claude 3.5 Sonnet (Online).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Add initialization for Anthropic client

    def generate_response(self, prompt: str) -> str:
        # Implementation for Claude API call
        return f"Claude response to: {prompt}"

    def get_embedding(self, text: str) -> List[float]:
        # Implementation for Claude embedding
        return []

class Gemma_Wrapper(LLM_Wrapper):
    """
    Implementation for Google's Gemma 4 (Local/Provider).
    """
    def __init__(self, model_id: str = "gemma4:12b"):
        self.model_id = model_id

    def generate_response(self, prompt: str) -> str:
        # Implementation for Local model call (via Ollama/vLLM/etc)
        return f"Gemma response to: {prompt}"

    def get_embedding(self, text: str) -> List[float]:
        # Implementation for local embedding
        return []

# Factory for easy switching
def get_llm_provider(provider_type: str, **kwargs) -> LLM_Wrapper:
    if provider_type == "claude":
        return Claude_Wrapper(**kwargs)
    elif provider_type == "gemma":
        return Gemma_Wrapper(**kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")
