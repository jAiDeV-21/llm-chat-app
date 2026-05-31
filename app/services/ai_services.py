import anthropic
import os

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-6"
    
    def get_ai_response(self, messages: list) -> str:
        """
        messages: List of dicts with 'role' and 'content' keys
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=messages
        )
        return response.content[0].text
    
    def stream_ai_response(self, messages: list):
        """Stream response for real-time chat"""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1000,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text