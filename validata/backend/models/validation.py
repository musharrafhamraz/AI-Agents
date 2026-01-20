"""Validation data models - both SQLAlchemy ORM and Pydantic schemas"""
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel, Field

from backend.database.connection import Base
from backend.models.response import ValidationStatus as ResponseValidationStatus


# SQLAlchemy ORM Models
class ValidationORM(Base):
    """Validation table in PostgreSQL"""
    __tablename__ = "validations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    response_id = Column(PGUUID(as_uuid=True), ForeignKey("responses.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    layer_results = Column(JSON, nullable=False)  # JSONB for layer results array
    final_status = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=True)
    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    audit_log = Column(JSON, nullable=True)  # JSONB for audit trail


class InsightORM(Base):
    """Insight table in PostgreSQL"""
    __tablename__ = "insights"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    survey_id = Column(PGUUID(as_uuid=True), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_text = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    supporting_data = Column(JSON, nullable=False)  # JSONB for supporting data
    trace = Column(JSON, nullable=False)  # JSONB for traceability
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Pydantic Models
class AuditEntry(BaseModel):
    """Single audit log entry"""
    timestamp: datetime
    action: str
    details: dict[str, Any]


class LayerResult(BaseModel):
    """Result from a single validation layer"""
    layer: int = Field(..., ge=1, le=7)
    layer_name: str
    passed: bool
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationResultBase(BaseModel):
    """Base validation result schema"""
    response_id: UUID
    layer_results: List[LayerResult] = Field(..., min_items=7, max_items=7)
    final_status: ResponseValidationStatus
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class ValidationResultCreate(ValidationResultBase):
    """Schema for creating a validation result"""
    audit_log: Optional[List[AuditEntry]] = None


class ValidationResult(ValidationResultBase):
    """Complete validation result schema"""
    id: UUID
    validated_at: datetime
    audit_log: Optional[List[AuditEntry]] = None
    
    class Config:
        from_attributes = True


class ValidationStatusQuery(BaseModel):
    """Validation status query response"""
    response_id: UUID
    status: ResponseValidationStatus
    current_layer: Optional[int] = None
    completed_layers: int
    total_layers: int = 7
    last_updated: datetime


class ChallengeResult(BaseModel):
    """Result from adversarial challenge"""
    challenge_type: str
    passed: bool
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
