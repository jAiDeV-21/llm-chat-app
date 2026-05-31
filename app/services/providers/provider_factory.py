# app/services/providers/provider_factory.py
from typing import Dict, Optional
from app.services.providers.base_provider import BaseAIProvider
from app.services.providers.claude_provider import ClaudeProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.ollama_provider import OllamaProvider

class ProviderFactory:
    _providers: Dict[str, BaseAIProvider] = {}
    
    @staticmethod
    def get_provider(provider_name: str) -> BaseAIProvider:
        """Get or create a provider instance"""
        if provider_name not in ProviderFactory._providers:
            if provider_name == "anthropic":
                ProviderFactory._providers[provider_name] = ClaudeProvider()
            elif provider_name == "openai":
                ProviderFactory._providers[provider_name] = OpenAIProvider()
            elif provider_name == "ollama":
                ProviderFactory._providers[provider_name] = OllamaProvider()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        
        return ProviderFactory._providers[provider_name]
    
    @staticmethod
    def list_available_providers() -> Dict[str, list]:
        """List all available providers and their models"""
        providers = {}
        
        for name in ["anthropic", "openai", "ollama"]:
            try:
                provider = ProviderFactory.get_provider(name)
                if provider.validate_api_key():
                    providers[name] = provider.list_models()
            except Exception as e:
                print(f"Provider {name} not available: {e}")
        
        return providers
    
    @staticmethod
    def clear_cache():
        """Clear cached provider instances"""
        ProviderFactory._providers.clear()