"""Survey MCP Server resources for database operations"""
import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.survey import (
    SurveyORM, Survey, SurveyCreate, SurveyUpdate,
    Question, SurveyStatus
)
from backend.database.connection import db_manager

logger = logging.getLogger(__name__)


class SurveyResources:
    """Database operations for surveys"""
    
    @staticmethod
    async def create_survey(survey_data: SurveyCreate) -> Survey:
        """
        Create a new survey in the database
        
        Args:
            survey_data: Survey creation data
        
        Returns:
            Created survey
        """
        try:
            async with db_manager.session() as session:
                # Convert questions to dict format for JSONB
                questions_dict = [q.model_dump() for q in survey_data.questions]
                
                # Create ORM object
                survey_orm = SurveyORM(
                    account_id=survey_data.account_id,
                    title=survey_data.title,
                    description=survey_data.description,
                    questions=questions_dict,
                    status=SurveyStatus.DRAFT
                )
                
                session.add(survey_orm)
                await session.commit()
                await session.refresh(survey_orm)
                
                # Convert to Pydantic model
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
                
                logger.info(f"Survey created: {survey.id}")
                return survey
                
        except Exception as e:
            logger.error(f"Failed to create survey: {e}")
            raise
    
    @staticmethod
    async def get_survey(survey_id: UUID) -> Optional[Survey]:
        """
        Get a survey by ID
        
        Args:
            survey_id: Survey UUID
        
        Returns:
            Survey or None if not found
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == survey_id)
                )
                survey_orm = result.scalar_one_or_none()
                
                if not survey_orm:
                    return None
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
                
                return survey
                
        except Exception as e:
            logger.error(f"Failed to get survey: {e}")
            raise
    
    @staticmethod
    async def update_survey(survey_id: UUID, update_data: SurveyUpdate) -> Optional[Survey]:
        """
        Update a survey
        
        Args:
            survey_id: Survey UUID
            update_data: Update data
        
        Returns:
            Updated survey or None if not found
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == survey_id)
                )
                survey_orm = result.scalar_one_or_none()
                
                if not survey_orm:
                    return None
                
                # Update fields
                if update_data.title is not None:
                    survey_orm.title = update_data.title
                if update_data.description is not None:
                    survey_orm.description = update_data.description
                if update_data.questions is not None:
                    survey_orm.questions = [q.model_dump() for q in update_data.questions]
                if update_data.status is not None:
                    survey_orm.status = update_data.status
                
                await session.commit()
                await session.refresh(survey_orm)
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
                
                logger.info(f"Survey updated: {survey_id}")
                return survey
                
        except Exception as e:
            logger.error(f"Failed to update survey: {e}")
            raise
    
    @staticmethod
    async def delete_survey(survey_id: UUID) -> bool:
        """
        Delete a survey
        
        Args:
            survey_id: Survey UUID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == survey_id)
                )
                survey_orm = result.scalar_one_or_none()
                
                if not survey_orm:
                    return False
                
                await session.delete(survey_orm)
                await session.commit()
                
                logger.info(f"Survey deleted: {survey_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete survey: {e}")
            raise
    
    @staticmethod
    async def list_surveys(
        account_id: Optional[str] = None,
        status: Optional[SurveyStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Survey]:
        """
        List surveys with optional filters
        
        Args:
            account_id: Filter by account
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of surveys
        """
        try:
            async with db_manager.session() as session:
                query = select(SurveyORM)
                
                if account_id:
                    query = query.where(SurveyORM.account_id == account_id)
                if status:
                    query = query.where(SurveyORM.status == status)
                
                query = query.limit(limit).offset(offset)
                
                result = await session.execute(query)
                survey_orms = result.scalars().all()
                
                surveys = [
                    Survey(
                        id=s.id,
                        account_id=s.account_id,
                        title=s.title,
                        description=s.description,
                        questions=[Question(**q) for q in s.questions],
                        created_at=s.created_at,
                        updated_at=s.updated_at,
                        status=s.status
                    )
                    for s in survey_orms
                ]
                
                return surveys
                
        except Exception as e:
            logger.error(f"Failed to list surveys: {e}")
            raise
    
    @staticmethod
    async def add_question(survey_id: UUID, question: Question) -> Optional[Survey]:
        """
        Add a question to a survey
        
        Args:
            survey_id: Survey UUID
            question: Question to add
        
        Returns:
            Updated survey or None if not found
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == survey_id)
                )
                survey_orm = result.scalar_one_or_none()
                
                if not survey_orm:
                    return None
                
                # Add question
                questions = survey_orm.questions.copy()
                questions.append(question.model_dump())
                survey_orm.questions = questions
                
                await session.commit()
                await session.refresh(survey_orm)
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
                
                logger.info(f"Question added to survey: {survey_id}")
                return survey
                
        except Exception as e:
            logger.error(f"Failed to add question: {e}")
            raise
    
    @staticmethod
    async def update_question(
        survey_id: UUID,
        question_id: str,
        question: Question
    ) -> Optional[Survey]:
        """
        Update a question in a survey
        
        Args:
            survey_id: Survey UUID
            question_id: Question ID to update
            question: Updated question data
        
        Returns:
            Updated survey or None if not found
        """
        try:
            async with db_manager.session() as session:
                result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == survey_id)
                )
                survey_orm = result.scalar_one_or_none()
                
                if not survey_orm:
                    return None
                
                # Update question
                questions = survey_orm.questions.copy()
                for i, q in enumerate(questions):
                    if q.get("id") == question_id:
                        questions[i] = question.model_dump()
                        break
                
                survey_orm.questions = questions
                
                await session.commit()
                await session.refresh(survey_orm)
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
                
                logger.info(f"Question updated in survey: {survey_id}")
                return survey
                
        except Exception as e:
            logger.error(f"Failed to update question: {e}")
            raise
