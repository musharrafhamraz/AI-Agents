"""Validation API endpoints"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_db
from mcp_servers.validation.tools import ValidationTools

router = APIRouter()
validation_tools = ValidationTools()


@router.get("/{response_id}")
async def get_validation_status(
    response_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get validation status for a response"""
    status_info = await validation_tools.get_validation_status(response_id)
    return status_info


@router.post("/{response_id}/revalidate")
async def revalidate_response(
    response_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Trigger revalidation of a response"""
    try:
        result = await validation_tools.validate_response(response_id)
        return {
            "message": "Revalidation completed",
            "validation": result.model_dump()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
