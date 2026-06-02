from app.sdk.inference_logger import InferenceLogger, LoggingDecorator
from app.services.providers.provider_factory import ProviderFactory
from typing import List, Optional, Iterator
import time

class LoggingAIService:
    """AI Service with built-in inference logging"""
    
    def __init__(
        self,
        inference_logger: InferenceLogger,
        default_provider: str = "anthropic"
    ):
        self.logger = inference_logger
        self.default_provider = default_provider
        self.token_counters = {}
    
    async def get_response(
        self,
        messages: List[tuple],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> dict:
        """Get response with automatic logging"""
        
        provider = provider or self.default_provider
        model = model or self._get_default_model(provider)
        
        # Create logging decorator
        decorator = LoggingDecorator(self.logger, provider, model)
        
        # Call provider with decorator
        result = await self._call_provider(
            messages=messages,
            provider=provider,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            conversation_id=conversation_id,
            session_id=session_id,
            user_id=user_id
        )
        
        return result
    
    async def _call_provider(self, **kwargs) -> dict:
        """Internal call to provider"""
        start = time.time()
        
        provider_instance = ProviderFactory.get_provider(kwargs["provider"])
        
        # Format messages
        message_objects = [
            {"role": role, "content": content}
            for role, content in kwargs["messages"]
        ]
        
        try:
            response = provider_instance.get_response(
                message_objects,
                kwargs["model"],
                kwargs["max_tokens"],
                kwargs["temperature"]
            )
            
            # Count tokens
            input_tokens = self._count_tokens(
                str(kwargs["messages"]),
                kwargs["provider"]
            )
            output_tokens = self._count_tokens(response, kwargs["provider"])
            
            return {
                "content": response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": kwargs["model"],
                "provider": kwargs["provider"],
                "latency_ms": (time.time() - start) * 1000
            }
        
        except Exception as e:
            raise
    
    def _count_tokens(self, text: str, provider: str) -> int:
        """Count tokens for text"""
        # Implement provider-specific token counting
        return len(text.split()) // 4  # Rough estimate