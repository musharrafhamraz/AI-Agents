from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import logging

from src.database import get_db
from src.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


class UserPreferences(BaseModel):
    check_frequency: Optional[str] = None
    importance_threshold: Optional[int] = None
    phone_number: Optional[str] = None


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user details"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "phone_number": user.phone_number,
        "check_frequency": user.check_frequency,
        "importance_threshold": user.importance_threshold,
        "is_active": user.is_active,
        "gmail_connected": user.gmail_credentials is not None,
        "created_at": user.created_at
    }


@router.put("/{user_id}/preferences")
async def update_preferences(
    user_id: int,
    preferences: UserPreferences,
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update preferences
    if preferences.check_frequency:
        user.check_frequency = preferences.check_frequency
    if preferences.importance_threshold is not None:
        if not 1 <= preferences.importance_threshold <= 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Importance threshold must be between 1 and 10"
            )
        user.importance_threshold = preferences.importance_threshold
    if preferences.phone_number:
        user.phone_number = preferences.phone_number
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"Updated preferences for user {user_id}")
    
    return {
        "message": "Preferences updated successfully",
        "user_id": user.id,
        "check_frequency": user.check_frequency,
        "importance_threshold": user.importance_threshold,
        "phone_number": user.phone_number
    }


@router.get("/")
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    """List all users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return {
        "count": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "gmail_connected": user.gmail_credentials is not None
            }
            for user in users
        ]
    }
