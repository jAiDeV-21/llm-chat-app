# app/services/providers/ollama_provider.py
import requests
from typing import List, Iterator
from app.services.providers.base_provider import (
    BaseAIProvider, Message, ModelConfig
)

class OllamaProvider(BaseAIProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def get_response(self, messages: List[Message], config: ModelConfig) -> str:
        """Get response from local Ollama model"""
        response = requests.post(
            f"{self.api_url}/chat",
            json={
                "model": config.name,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                "stream": False,
                "options": {
                    "temperature": config.temperature,
                    "num_predict": config.max_tokens
                }
            }
        )
        return response.json()["message"]["content"]
    
    def stream_response(self, messages: List[Message], config: ModelConfig) -> Iterator[str]:
        """Stream response from Ollama"""
        response = requests.post(
            f"{self.api_url}/chat",
            json={
                "model": config.name,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                "stream": True,
                "options": {"temperature": config.temperature}
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                import json
                chunk = json.loads(line)
                if "message" in chunk:
                    yield chunk["message"].get("content", "")
    
    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.api_url}/tags")
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception:
            return ["llama2", "mistral"]  # Defaults
    
    def validate_api_key(self) -> bool:
        try:
            requests.get(f"{self.api_url}/tags", timeout=5)
            return True
        except Exception:
            return False
    
    def get_cost_per_1k_tokens(self, model: str) -> dict:
        # Local models are free
        return {"input": 0.0, "output": 0.0}