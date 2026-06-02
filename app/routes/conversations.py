from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("/create")
def create_conversation(db: Session = Depends(get_db)):
    conversation = models.Conversation(title="New Conversation")
    db.add(conversation)
    db.commit()
    return {"id": conversation.id, "title": conversation.title}

@router.get("/list")
def list_conversations(db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).all()
    return conversations

@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at).all()
    return messages