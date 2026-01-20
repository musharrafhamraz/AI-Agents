"""Analytics data models - Pydantic schemas"""
from datetime import datetime
from typing import List, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InsightTrace(BaseModel):
    """Traceability information for an insight"""
    source_responses: List[str] = Field(..., min_items=1)
    analysis_steps: List[str]
    memory_context: List[str]


class Insight(BaseModel):
    """Generated insight from survey data"""
    id: UUID
    survey_id: UUID
    insight_text: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    supporting_data: dict[str, Any]
    trace: InsightTrace
    generated_at: datetime
    
    class Config:
        from_attributes = True


class Pattern(BaseModel):
    """Detected pattern in survey responses"""
    pattern_type: str
    description: str
    frequency: int = Field(..., ge=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    examples: List[str]


class AggregatedData(BaseModel):
    """Aggregated response data"""
    survey_id: UUID
    total_responses: int
    response_rate: Optional[float] = None
    aggregations: dict[str, Any]
    filters_applied: dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class InsightList(BaseModel):
    """List of insights"""
    insights: List[Insight]
    total: int


class PatternList(BaseModel):
    """List of detected patterns"""
    patterns: List[Pattern]
    total: int
