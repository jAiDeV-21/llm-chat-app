# app/services/providers/claude_provider.py
import anthropic
import os
from typing import List, Iterator
from app.services.providers.base_provider import (
    BaseAIProvider, Message, ModelConfig
)

class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.api_key = api_key
    
    def get_response(self, messages: List[Message], config: ModelConfig) -> str:
        """Get response from Claude"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.messages.create(
            model=config.name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=formatted_messages
        )
        return response.content[0].text
    
    def stream_response(self, messages: List[Message], config: ModelConfig) -> Iterator[str]:
        """Stream response from Claude"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        with self.client.messages.stream(
            model=config.name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=formatted_messages
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def list_models(self) -> List[str]:
        return [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "claude-haiku-4-5-20251001"
        ]
    
    def validate_api_key(self) -> bool:
        try:
            self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
    
    def get_cost_per_1k_tokens(self, model: str) -> dict:
        costs = {
            "claude-opus-4-6": {"input": 0.003, "output": 0.015},
            "claude-sonnet-4-6": {"input": 0.003, "output": 0.015},
            "claude-haiku-4-5-20251001": {"input": 0.0008, "output": 0.004}
        }
        return costs.get(model, {"input": 0.0, "output": 0.0})