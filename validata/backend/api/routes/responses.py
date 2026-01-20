"""Response API endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.response import Response, ResponseCreate, ResponseList, ResponseORM, Answer
from backend.api.dependencies import get_db
from backend.database.connection import db_manager

router = APIRouter()


@router.post("/", response_model=Response, status_code=status.HTTP_201_CREATED)
async def submit_response(
    response_data: ResponseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a survey response"""
    # Create response in database
    response_orm = ResponseORM(
        survey_id=response_data.survey_id,
        respondent_id=response_data.respondent_id,
        answers=[a.model_dump() for a in response_data.answers],
        channel=response_data.channel,
        metadata=response_data.metadata
    )
    
    db.add(response_orm)
    await db.commit()
    await db.refresh(response_orm)
    
    # Convert to Pydantic model
    response = Response(
        id=response_orm.id,
        survey_id=response_orm.survey_id,
        answers=[Answer(**a) for a in response_orm.answers],
        channel=response_orm.channel,
        respondent_id=response_orm.respondent_id,
        submitted_at=response_orm.submitted_at,
        validation_status=response_orm.validation_status,
        metadata=response_orm.metadata
    )
    
    return response


@router.get("/{response_id}", response_model=Response)
async def get_response(
    response_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a response by ID"""
    result = await db.execute(
        select(ResponseORM).where(ResponseORM.id == response_id)
    )
    response_orm = result.scalar_one_or_none()
    
    if not response_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response {response_id} not found"
        )
    
    response = Response(
        id=response_orm.id,
        survey_id=response_orm.survey_id,
        answers=[Answer(**a) for a in response_orm.answers],
        channel=response_orm.channel,
        respondent_id=response_orm.respondent_id,
        submitted_at=response_orm.submitted_at,
        validation_status=response_orm.validation_status,
        metadata=response_orm.metadata
    )
    
    return response


@router.get("/survey/{survey_id}", response_model=List[Response])
async def list_survey_responses(
    survey_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List responses for a survey"""
    result = await db.execute(
        select(ResponseORM)
        .where(ResponseORM.survey_id == survey_id)
        .limit(limit)
        .offset(offset)
    )
    response_orms = result.scalars().all()
    
    responses = [
        Response(
            id=r.id,
            survey_id=r.survey_id,
            answers=[Answer(**a) for a in r.answers],
            channel=r.channel,
            respondent_id=r.respondent_id,
            submitted_at=r.submitted_at,
            validation_status=r.validation_status,
            metadata=r.metadata
        )
        for r in response_orms
    ]
    
    return responses
