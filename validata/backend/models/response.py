"""Response data models - both SQLAlchemy ORM and Pydantic schemas"""
from datetime import datetime
from typing import Optional, List, Union, Any
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel, Field

from backend.database.connection import Base


# Enums
class Channel(str, Enum):
    """Data collection channels"""
    FORM = "form"
    CHAT = "chat"
    API = "api"


class ValidationStatus(str, Enum):
    """Response validation status"""
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"


# SQLAlchemy ORM Models
class ResponseORM(Base):
    """Response table in PostgreSQL"""
    __tablename__ = "responses"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    survey_id = Column(PGUUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    respondent_id = Column(String(255), nullable=True, index=True)
    answers = Column(JSON, nullable=False)  # JSONB for answers array
    channel = Column(SQLEnum(Channel), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING, nullable=False)
    metadata = Column(JSON, nullable=True)  # Additional metadata like IP, user agent, etc.


# Pydantic Models
class Answer(BaseModel):
    """Individual answer to a question"""
    question_id: str
    value: Union[str, int, List[str], float, bool]


class ResponseBase(BaseModel):
    """Base response schema"""
    survey_id: UUID
    answers: List[Answer] = Field(..., min_items=1)
    channel: Channel
    respondent_id: Optional[str] = None


class ResponseCreate(ResponseBase):
    """Schema for creating a response"""
    metadata: Optional[dict[str, Any]] = None


class ResponseUpdate(BaseModel):
    """Schema for updating a response"""
    validation_status: Optional[ValidationStatus] = None
    metadata: Optional[dict[str, Any]] = None


class Response(ResponseBase):
    """Complete response schema with metadata"""
    id: UUID
    submitted_at: datetime
    validation_status: ValidationStatus
    metadata: Optional[dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ResponseList(BaseModel):
    """Paginated list of responses"""
    responses: List[Response]
    total: int
    page: int
    page_size: int
