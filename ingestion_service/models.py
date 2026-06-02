
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, JSON, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ingestion_logs.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InferenceLogPayload(BaseModel):
    log_id: str
    conversation_id: str
    session_id: str
    timestamp: str
    latency_ms: float
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    request_preview: str
    response_preview: str
    status: str
    error_message: Optional[str] = None
    temperature: float
    max_tokens: int
    user_id: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None

class IngestPayload(BaseModel):
    logs: List[InferenceLogPayload]


class InferenceLogModel(Base):
    __tablename__ = "inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(255), unique=True, nullable=False, index=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(String(64), nullable=False, index=True)
    latency_ms = Column(Float, nullable=False)
    model = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    request_preview = Column(Text, nullable=False)
    response_preview = Column(Text, nullable=False)
    status = Column(String(64), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    temperature = Column(Float, nullable=False)
    max_tokens = Column(Integer, nullable=False)
    user_id = Column(String(255), nullable=True, index=True)
    custom_metadata = Column(JSON, nullable=True)
    extracted_metadata = Column(JSON, nullable=False, default=dict)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
