from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from pydantic import BaseModel
import logging

from src.database import get_db
from src.models import User
from src.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Gmail OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class UserCreate(BaseModel):
    email: str
    phone_number: str


@router.post("/register")
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        is_active=False  # Will be activated after Gmail connection
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user registered: {user_data.email}")
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email,
        "next_step": "Connect Gmail account using /api/auth/gmail/connect"
    }


@router.get("/gmail/connect/{user_id}")
async def connect_gmail(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Initiate Gmail OAuth flow"""
    # Verify user exists
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GMAIL_REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GMAIL_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=str(user_id)  # Pass user_id in state
    )
    
    logger.info(f"Gmail OAuth initiated for user {user_id}")
    
    return {
        "authorization_url": authorization_url,
        "message": "Visit the authorization_url to connect your Gmail account"
    }


@router.get("/gmail/callback")
async def gmail_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle Gmail OAuth callback"""
    try:
        user_id = int(state)
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Exchange code for credentials
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Store credentials
        user.gmail_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        user.is_active = True
        
        await db.commit()
        
        logger.info(f"Gmail connected successfully for user {user_id}")
        
        return {
            "message": "Gmail account connected successfully!",
            "user_id": user_id,
            "email": user.email,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error in Gmail callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect Gmail: {str(e)}"
        )
