# app/services/ai_service.py
from typing import List, Optional, Iterator
from app.services.providers.provider_factory import ProviderFactory
from app.services.providers.base_provider import Message, ModelConfig

class AIService:
    """Main service that routes to different providers"""
    
    def __init__(self, default_provider: str = "anthropic"):
        self.default_provider = default_provider
    
    def get_response(
        self,
        messages: List[tuple],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Get response from specified or default provider"""
        provider = provider or self.default_provider
        model = model or self._get_default_model(provider)
        
        # Convert tuple messages to Message objects
        message_objects = [
            Message(role=role, content=content)
            for role, content in messages
        ]
        
        config = ModelConfig(
            name=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        provider_instance = ProviderFactory.get_provider(provider)
        return provider_instance.get_response(message_objects, config)
    
    def stream_response(
        self,
        messages: List[tuple],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream response from specified or default provider"""
        provider = provider or self.default_provider
        model = model or self._get_default_model(provider)
        
        message_objects = [
            Message(role=role, content=content)
            for role, content in messages
        ]
        
        config = ModelConfig(
            name=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        provider_instance = ProviderFactory.get_provider(provider)
        yield from provider_instance.stream_response(message_objects, config)
    
    def get_available_providers(self) -> dict:
        """Get all available providers with their models"""
        return ProviderFactory.list_available_providers()
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for a provider"""
        defaults = {
            "anthropic": "claude-opus-4-6",
            "openai": "gpt-4-turbo",
            "ollama": "llama2"
        }
        return defaults.get(provider, "")