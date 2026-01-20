"""FastAPI dependencies"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db_session
from backend.core.security import get_current_user


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async for session in get_db_session():
        yield session


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user"""
    # Add additional checks if needed (e.g., is_active flag)
    return current_user


async def get_account_id(
    current_user: dict = Depends(get_current_active_user)
) -> str:
    """Extract account ID from current user"""
    account_id = current_user.get("payload", {}).get("account_id")
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account ID not found in token"
        )
    return account_id
