from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas import ChatRequestSchema
from app.services.ai_service_with_logging import LoggingAIService
from app.sdk.inference_logger import InferenceLogger
from app.database import get_db
from app import models
import uuid
import os
from fastapi.responses import StreamingResponse
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize logger
logger = InferenceLogger(
    ingestion_url=os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001"),
    batch_size=10,
    flush_interval_seconds=5
)

ai_service = LoggingAIService(logger)

@router.post("/send-message")
async def send_message(
    request: ChatRequestSchema,
    provider: str = Query(None),
    model: str = Query(None),
    db: Session = Depends(get_db)
):
    """Send message with automatic logging"""
    
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == request.conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get conversation history
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == request.conversation_id
    ).order_by(models.Message.created_at).all()
    
    # Format messages
    formatted_messages = [
        (msg.role, msg.content) for msg in messages
    ] + [("user", request.message)]
    
    # Generate session ID if not exists
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Get response WITH LOGGING
        response = await ai_service.get_response(
            messages=formatted_messages,
            provider=provider or conversation.preferred_provider,
            model=model or conversation.preferred_model,
            conversation_id=str(request.conversation_id),
            session_id=session_id,
            user_id=request.user_id
        )
        
        # Save both messages
        user_msg = models.Message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        
        assistant_msg = models.Message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=response["content"],
            provider=response["provider"],
            model=response["model"]
        )
        db.add(assistant_msg)
        db.commit()
        
        return {
            "user_message": request.message,
            "assistant_message": response["content"],
            "session_id": session_id
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Flush logs
        await logger.flush_all()

@router.post("/conversations/{conversation_id}/cancel")
def cancel_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Cancel/stop active conversation"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404)
    
    # Mark as cancelled or inactive
    conversation.is_active = False
    db.commit()
    
    return {"status": "cancelled"}


@router.post("/send-message-stream")
async def send_message_stream(
    request: ChatRequestSchema,
    provider: str = Query(None),
    db: Session = Depends(get_db)
):
    """Stream response chunks"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == request.conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404)
    
    session_id = str(uuid.uuid4())
    
    async def stream_generator():
        # Get history
        messages = db.query(models.Message).filter(
            models.Message.conversation_id == request.conversation_id
        ).order_by(models.Message.created_at).all()
        
        formatted_messages = [
            (msg.role, msg.content) for msg in messages
        ] + [("user", request.message)]
        
        full_response = ""
        
        # Stream from provider
        async for chunk in ai_service.stream_response(
            messages=formatted_messages,
            provider=provider or conversation.preferred_provider,
            conversation_id=str(request.conversation_id),
            session_id=session_id
        ):
            full_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Save messages
        user_msg = models.Message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        
        assistant_msg = models.Message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=full_response
        )
        db.add(assistant_msg)
        db.commit()
    
    return StreamingResponse(stream_generator(), media_type="text/event-stream")