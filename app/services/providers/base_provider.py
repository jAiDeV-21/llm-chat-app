# app/services/providers/base_provider.py
from abc import ABC, abstractmethod
from typing import List, Dict, Iterator, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str

@dataclass
class ModelConfig:
    name: str
    max_tokens: int
    temperature: float
    top_p: Optional[float] = None

class BaseAIProvider(ABC):
    """Abstract base for all AI providers"""
    
    @abstractmethod
    def get_response(self, messages: List[Message], config: ModelConfig) -> str:
        """Get a single response from the model"""
        pass
    
    @abstractmethod
    def stream_response(self, messages: List[Message], config: ModelConfig) -> Iterator[str]:
        """Stream response chunks"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """Return available models from this provider"""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate if API key is valid"""
        pass
    
    @abstractmethod
    def get_cost_per_1k_tokens(self, model: str) -> Dict[str, float]:
        """Return input and output costs per 1K tokens"""
        return {"input": 0.0, "output": 0.0}
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count (override for accuracy)"""
        return len(text.split()) // 4  # Rough estimate