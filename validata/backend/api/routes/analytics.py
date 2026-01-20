"""Analytics API endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.analytics import Insight, Pattern
from backend.api.dependencies import get_db
from mcp_servers.analytics.tools import AnalyticsTools

router = APIRouter()
analytics_tools = AnalyticsTools()


@router.get("/{survey_id}/insights", response_model=List[Insight])
async def get_insights(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get generated insights for a survey"""
    insights = await analytics_tools.get_insights_for_survey(survey_id)
    return insights


@router.post("/{survey_id}/insights", response_model=List[Insight])
async def generate_insights(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generate new insights for a survey"""
    try:
        insights = await analytics_tools.generate_insights(survey_id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/{survey_id}/patterns", response_model=List[Pattern])
async def get_patterns(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detected patterns for a survey"""
    patterns = await analytics_tools.detect_patterns(survey_id)
    return patterns


@router.get("/insights/{insight_id}/trace")
async def get_insight_trace(
    insight_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get traceability information for an insight"""
    try:
        trace = await analytics_tools.get_insight_trace(insight_id)
        return trace
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
