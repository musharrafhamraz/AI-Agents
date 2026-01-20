"""Survey data models - both SQLAlchemy ORM and Pydantic schemas"""
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel, Field, field_validator

from backend.database.connection import Base


# Enums
class QuestionType(str, Enum):
    """Types of survey questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    RATING = "rating"
    CONDITIONAL = "conditional"


class SurveyStatus(str, Enum):
    """Survey lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


# SQLAlchemy ORM Models
class SurveyORM(Base):
    """Survey table in PostgreSQL"""
    __tablename__ = "surveys"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(JSON, nullable=False)  # JSONB for questions array
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(SurveyStatus), default=SurveyStatus.DRAFT, nullable=False)


# Pydantic Models
class ConditionalLogic(BaseModel):
    """Conditional logic for questions"""
    condition_question_id: str
    condition_value: Any
    show_if_match: bool = True


class Question(BaseModel):
    """Survey question schema"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: QuestionType
    text: str = Field(..., min_length=1, max_length=1000)
    options: Optional[List[str]] = None
    required: bool = True
    conditional_logic: Optional[ConditionalLogic] = None
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate that multiple choice questions have options"""
        question_type = info.data.get('type')
        if question_type == QuestionType.MULTIPLE_CHOICE:
            if not v or len(v) < 2:
                raise ValueError("Multiple choice questions must have at least 2 options")
        return v
    
    @field_validator('type')
    @classmethod
    def validate_question_type(cls, v: QuestionType) -> QuestionType:
        """Validate question type is supported"""
        if v not in QuestionType:
            raise ValueError(f"Question type must be one of: {', '.join([t.value for t in QuestionType])}")
        return v


class SurveyBase(BaseModel):
    """Base survey schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    questions: List[Question] = Field(..., min_items=1)


class SurveyCreate(SurveyBase):
    """Schema for creating a survey"""
    account_id: str = Field(..., min_length=1, max_length=255)


class SurveyUpdate(BaseModel):
    """Schema for updating a survey"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    questions: Optional[List[Question]] = Field(None, min_items=1)
    status: Optional[SurveyStatus] = None


class Survey(SurveyBase):
    """Complete survey schema with metadata"""
    id: UUID
    account_id: str
    created_at: datetime
    updated_at: datetime
    status: SurveyStatus
    
    class Config:
        from_attributes = True


class SurveyList(BaseModel):
    """Paginated list of surveys"""
    surveys: List[Survey]
    total: int
    page: int
    page_size: int


class Template(BaseModel):
    """Survey template schema"""
    id: str
    name: str
    description: str
    category: str
    questions: List[Question]
