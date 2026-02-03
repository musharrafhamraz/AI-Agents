from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
import logging

from src.database import get_db
from src.models import User, ProcessedEmail, WhatsAppMessage
from src.tasks.email_tasks import process_user_emails_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/check/{user_id}")
async def trigger_email_check(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger email check for a user"""
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
    
    if not user.is_active or not user.gmail_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not active or Gmail not connected"
        )
    
    # Trigger background task
    process_user_emails_task.delay(user_id)
    
    logger.info(f"Manual email check triggered for user {user_id}")
    
    return {
        "message": "Email check started",
        "user_id": user_id,
        "status": "processing"
    }


@router.get("/history/{user_id}")
async def get_email_history(
    user_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get processed email history for a user"""
    result = await db.execute(
        select(ProcessedEmail)
        .where(ProcessedEmail.user_id == user_id)
        .order_by(desc(ProcessedEmail.processed_at))
        .limit(limit)
    )
    emails = result.scalars().all()
    
    return {
        "user_id": user_id,
        "count": len(emails),
        "emails": [
            {
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "importance_score": email.importance_score,
                "summary": email.summary,
                "sent_to_whatsapp": email.sent_to_whatsapp,
                "processed_at": email.processed_at
            }
            for email in emails
        ]
    }


@router.get("/messages/{user_id}")
async def get_whatsapp_messages(
    user_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get WhatsApp message history for a user"""
    result = await db.execute(
        select(WhatsAppMessage)
        .where(WhatsAppMessage.user_id == user_id)
        .order_by(desc(WhatsAppMessage.sent_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return {
        "user_id": user_id,
        "count": len(messages),
        "messages": [
            {
                "id": msg.id,
                "email_count": len(msg.email_ids) if msg.email_ids else 0,
                "status": msg.status,
                "sent_at": msg.sent_at,
                "message_preview": msg.message_text[:100] + "..." if len(msg.message_text) > 100 else msg.message_text
            }
            for msg in messages
        ]
    }


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a user"""
    # Total processed emails
    total_result = await db.execute(
        select(ProcessedEmail).where(ProcessedEmail.user_id == user_id)
    )
    total_emails = len(total_result.scalars().all())
    
    # Important emails (sent to WhatsApp)
    important_result = await db.execute(
        select(ProcessedEmail).where(
            ProcessedEmail.user_id == user_id,
            ProcessedEmail.sent_to_whatsapp == True
        )
    )
    important_emails = len(important_result.scalars().all())
    
    # WhatsApp messages sent
    messages_result = await db.execute(
        select(WhatsAppMessage).where(WhatsAppMessage.user_id == user_id)
    )
    total_messages = len(messages_result.scalars().all())
    
    return {
        "user_id": user_id,
        "total_emails_processed": total_emails,
        "important_emails": important_emails,
        "whatsapp_messages_sent": total_messages,
        "average_importance": 0 if total_emails == 0 else important_emails / total_emails * 100
    }
