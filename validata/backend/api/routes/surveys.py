"""Survey API endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.survey import (
    Survey, SurveyCreate, SurveyUpdate, SurveyList, Template
)
from backend.api.dependencies import get_db, get_account_id
from mcp_servers.survey.resources import SurveyResources

router = APIRouter()
survey_resources = SurveyResources()


@router.post("/", response_model=Survey, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey_data: SurveyCreate,
    db: AsyncSession = Depends(get_db),
    account_id: str = Depends(get_account_id)
):
    """Create a new survey"""
    # Ensure account_id matches authenticated user
    if survey_data.account_id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create survey for different account"
        )
    
    survey = await survey_resources.create_survey(survey_data)
    return survey


@router.get("/{survey_id}", response_model=Survey)
async def get_survey(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: str = Depends(get_account_id)
):
    """Get a survey by ID"""
    survey = await survey_resources.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey {survey_id} not found"
        )
    
    # Check ownership
    if survey.account_id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return survey


@router.put("/{survey_id}", response_model=Survey)
async def update_survey(
    survey_id: UUID,
    update_data: SurveyUpdate,
    db: AsyncSession = Depends(get_db),
    account_id: str = Depends(get_account_id)
):
    """Update a survey"""
    # Check ownership first
    existing_survey = await survey_resources.get_survey(survey_id)
    if not existing_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey {survey_id} not found"
        )
    
    if existing_survey.account_id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    survey = await survey_resources.update_survey(survey_id, update_data)
    return survey


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(
    survey_id: UUID,
    db: AsyncSession = Depends(get_db),
    account_id: str = Depends(get_account_id)
):
    """Delete a survey"""
    # Check ownership first
    existing_survey = await survey_resources.get_survey(survey_id)
    if not existing_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey {survey_id} not found"
        )
    
    if existing_survey.account_id != account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    deleted = await survey_resources.delete_survey(survey_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey {survey_id} not found"
        )


@router.get("/", response_model=List[Survey])
async def list_surveys(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    account_id: str = Depends(get_account_id)
):
    """List surveys for the authenticated account"""
    from backend.models.survey import SurveyStatus
    
    status_enum = None
    if status_filter:
        try:
            status_enum = SurveyStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    surveys = await survey_resources.list_surveys(
        account_id=account_id,
        status=status_enum,
        limit=limit,
        offset=offset
    )
    
    return surveys


@router.get("/templates/", response_model=List[Template])
async def list_templates():
    """Get available survey templates"""
    from mcp_servers.survey.tools import SurveyTools
    
    tools = SurveyTools()
    templates = tools.list_templates()
    
    return templates
