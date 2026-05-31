from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageSchema(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ConversationSchema(BaseModel):
    id: int
    title: str
    messages: List[MessageSchema]
    created_at: datetime
    
class ChatRequestSchema(BaseModel):
    conversation_id: int
    message: str