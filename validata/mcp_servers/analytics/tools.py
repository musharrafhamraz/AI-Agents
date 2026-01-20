"""Analytics MCP Server tools"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select
from datetime import datetime

from .insights import InsightGenerator
from backend.models.response import ResponseORM, Response, Answer, ValidationStatus
from backend.models.analytics import Insight, Pattern, AggregatedData
from backend.models.validation import InsightORM
from backend.database.connection import db_manager

logger = logging.getLogger(__name__)


class AnalyticsTools:
    """Tools for analytics and insights"""
    
    def __init__(self):
        self.generator = InsightGenerator()
    
    async def generate_insights(
        self,
        survey_id: UUID,
        account_context: Optional[Dict[str, Any]] = None
    ) -> List[Insight]:
        """
        Generate insights for a survey
        
        Args:
            survey_id: Survey UUID
            account_context: Historical context
        
        Returns:
            List of generated insights
        """
        try:
            # Get validated responses
            async with db_manager.session() as session:
                result = await session.execute(
                    select(ResponseORM).where(
                        ResponseORM.survey_id == survey_id,
                        ResponseORM.validation_status == ValidationStatus.VALIDATED
                    )
                )
                response_orms = result.scalars().all()
                
                # Convert to Pydantic models
                responses = [
                    Response(
                        id=r.id,
                        survey_id=r.survey_id,
                        answers=[Answer(**a) for a in r.answers],
                        channel=r.channel,
                        respondent_id=r.respondent_id,
                        submitted_at=r.submitted_at,
                        validation_status=r.validation_status
                    )
                    for r in response_orms
                ]
            
            if not responses:
                logger.warning(f"No validated responses found for survey {survey_id}")
                return []
            
            # Generate insights
            insights = await self.generator.generate_insights(
                survey_id=survey_id,
                responses=responses,
                account_context=account_context or {}
            )
            
            # Store insights in database
            async with db_manager.session() as session:
                for insight in insights:
                    insight_orm = InsightORM(
                        id=insight.id,
                        survey_id=insight.survey_id,
                        insight_text=insight.insight_text,
                        confidence_score=insight.confidence_score,
                        supporting_data=insight.supporting_data,
                        trace=insight.trace.model_dump(),
                        generated_at=insight.generated_at
                    )
                    session.add(insight_orm)
                
                await session.commit()
            
            logger.info(f"Generated and stored {len(insights)} insights for survey {survey_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            raise
    
    async def aggregate_responses(
        self,
        survey_id: UUID,
        filters: Optional[Dict[str, Any]] = None
    ) -> AggregatedData:
        """
        Aggregate response data with filters
        
        Args:
            survey_id: Survey UUID
            filters: Optional filter criteria
        
        Returns:
            Aggregated data
        """
        try:
            # Get responses
            async with db_manager.session() as session:
                query = select(ResponseORM).where(ResponseORM.survey_id == survey_id)
                
                # Apply validation status filter if specified
                if filters and filters.get("validation_status"):
                    query = query.where(ResponseORM.validation_status == filters["validation_status"])
                
                result = await session.execute(query)
                response_orms = result.scalars().all()
                
                # Convert to Pydantic models
                responses = [
                    Response(
                        id=r.id,
                        survey_id=r.survey_id,
                        answers=[Answer(**a) for a in r.answers],
                        channel=r.channel,
                        respondent_id=r.respondent_id,
                        submitted_at=r.submitted_at,
                        validation_status=r.validation_status
                    )
                    for r in response_orms
                ]
            
            # Aggregate
            aggregations = self.generator.aggregate_responses(
                responses=responses,
                filters=filters or {}
            )
            
            aggregated_data = AggregatedData(
                survey_id=survey_id,
                total_responses=aggregations["total_responses"],
                aggregations=aggregations,
                filters_applied=filters or {},
                generated_at=datetime.utcnow()
            )
            
            logger.info(f"Aggregated {aggregated_data.total_responses} responses for survey {survey_id}")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Failed to aggregate responses: {e}")
            raise
    
    async def detect_patterns(
        self,
        survey_id: UUID
    ) -> List[Pattern]:
        """
        Detect patterns in survey responses
        
        Args:
            survey_id: Survey UUID
        
        Returns:
            List of detected patterns
        """
        try:
            # Get validated responses
            async with db_manager.session() as session:
                result = await session.execute(
                    select(ResponseORM).where(
                        ResponseORM.survey_id == survey_id,
                        ResponseORM.validation_status == ValidationStatus.VALIDATED
                    )
                )
                response_orms = result.scalars().all()
                
                # Convert to Pydantic models
                responses = [
                    Response(
                        id=r.id,
                        survey_id=r.survey_id,
                        answers=[Answer(**a) for a in r.answers],
                        channel=r.channel,
                        respondent_id=r.respondent_id,
                        submitted_at=r.submitted_at,
                        validation_status=r.validation_status
                    )
                    for r in response_orms
                ]
            
            if not responses:
                logger.warning(f"No validated responses found for survey {survey_id}")
                return []
            
            # Detect patterns
            patterns = await self.generator.detect_patterns(responses)
            
            logger.info(f"Detected {len(patterns)} patterns for survey {survey_id}")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect patterns: {e}")
            raise
    
    async def get_insight_trace(
        self,
        insight_id: UUID
    ) -> Dict[str, Any]:
        """
        Get traceability information for an insight
        
        Args:
            insight_id: Insight UUID
        
        Returns:
            Trace information
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(InsightORM).where(InsightORM.id == insight_id)
                )
                insight_orm = result.scalar_one_or_none()
                
                if not insight_orm:
                    raise ValueError(f"Insight not found: {insight_id}")
                
                trace_data = {
                    "insight_id": str(insight_orm.id),
                    "survey_id": str(insight_orm.survey_id),
                    "insight_text": insight_orm.insight_text,
                    "confidence_score": insight_orm.confidence_score,
                    "trace": insight_orm.trace,
                    "supporting_data": insight_orm.supporting_data,
                    "generated_at": insight_orm.generated_at.isoformat()
                }
                
                logger.info(f"Retrieved trace for insight {insight_id}")
                return trace_data
                
        except Exception as e:
            logger.error(f"Failed to get insight trace: {e}")
            raise
    
    async def get_insights_for_survey(
        self,
        survey_id: UUID
    ) -> List[Insight]:
        """
        Get all insights for a survey
        
        Args:
            survey_id: Survey UUID
        
        Returns:
            List of insights
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(InsightORM).where(InsightORM.survey_id == survey_id)
                )
                insight_orms = result.scalars().all()
                
                insights = []
                for insight_orm in insight_orms:
                    from backend.models.analytics import InsightTrace
                    
                    trace = InsightTrace(**insight_orm.trace)
                    
                    insight = Insight(
                        id=insight_orm.id,
                        survey_id=insight_orm.survey_id,
                        insight_text=insight_orm.insight_text,
                        confidence_score=insight_orm.confidence_score,
                        supporting_data=insight_orm.supporting_data,
                        trace=trace,
                        generated_at=insight_orm.generated_at
                    )
                    insights.append(insight)
                
                logger.info(f"Retrieved {len(insights)} insights for survey {survey_id}")
                return insights
                
        except Exception as e:
            logger.error(f"Failed to get insights: {e}")
            raise
