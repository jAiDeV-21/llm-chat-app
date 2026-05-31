from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ChatRequestSchema
from app.services.ai_service import AIService
from app.database import get_db
from app import models

router = APIRouter(prefix="/api/chat", tags=["chat"])
ai_service = AIService()

@router.post("/send-message")
def send_message(request: ChatRequestSchema, db: Session = Depends(get_db)):
    # Get conversation
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == request.conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save user message
    user_msg = models.Message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()
    
    # Get conversation history
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == request.conversation_id
    ).order_by(models.Message.created_at).all()
    
    # Format for API
    formatted_messages = [
        {"role": msg.role, "content": msg.content} 
        for msg in messages
    ]
    
    # Get AI response
    ai_response = ai_service.get_ai_response(formatted_messages)
    
    # Save AI response
    assistant_msg = models.Message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "user_message": request.message,
        "assistant_message": ai_response
    }