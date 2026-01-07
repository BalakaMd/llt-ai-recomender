import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM

from app.core.database import Base

# PostgreSQL ENUM types
llm_provider_enum = ENUM('openai', 'gemini', 'anthropic', name='llmprovider', create_type=False)
ai_run_status_enum = ENUM('pending', 'completed', 'failed', name='airunstatus', create_type=False)


class AIRun(Base):
    """Model for logging AI interactions to integration.ai_runs table."""
    
    __tablename__ = "ai_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    trip_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    provider = Column(llm_provider_enum, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(JSONB, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    status = Column(ai_run_status_enum, server_default='pending', nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIRun(id={self.id}, user_id={self.user_id}, status={self.status})>"
