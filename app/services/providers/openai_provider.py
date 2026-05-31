# app/services/providers/openai_provider.py
import openai
import os
import tiktoken
from typing import List, Iterator
from app.services.providers.base_provider import (
    BaseAIProvider, Message, ModelConfig
)

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = openai.OpenAI(api_key=api_key)
        self.api_key = api_key
    
    def get_response(self, messages: List[Message], config: ModelConfig) -> str:
        """Get response from OpenAI"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.chat.completions.create(
            model=config.name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p or 1.0,
            messages=formatted_messages
        )
        return response.choices[0].message.content
    
    def stream_response(self, messages: List[Message], config: ModelConfig) -> Iterator[str]:
        """Stream response from OpenAI"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        stream = self.client.chat.completions.create(
            model=config.name,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            stream=True,
            messages=formatted_messages
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def list_models(self) -> List[str]:
        return [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
    
    def validate_api_key(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_cost_per_1k_tokens(self, model: str) -> dict:
        costs = {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }
        return costs.get(model, {"input": 0.0, "output": 0.0})
    
    def count_tokens(self, text: str) -> int:
        """Accurate token counting for OpenAI models"""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception:
            return len(text.split()) // 4