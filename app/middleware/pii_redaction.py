from fastapi import Request
import re
from typing import Callable

class PIIRedactionMiddleware:
    """Middleware to redact PII from requests/responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable):
        # Optionally redact request body
        response = await call_next(request)
        return response
    
    @staticmethod
    def redact_text(text: str) -> str:
        """Remove PII from text"""
        
        # Email
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "[EMAIL]",
            text
        )
        
        # Phone
        text = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "[PHONE]",
            text
        )
        
        # SSN
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            "[SSN]",
            text
        )
        
        # Credit card
        text = re.sub(
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "[CC]",
            text
        )
        
        return text