from celery import shared_task
from sqlalchemy import select
from datetime import datetime
import logging
import asyncio

from src.tasks.celery_app import celery_app
from src.database import AsyncSessionLocal
from src.models import User, ProcessedEmail, WhatsAppMessage
from src.services.email_monitor import EmailMonitorService
from src.services.ai_analyzer import AIAnalyzerService
from src.services.whatsapp_service import WhatsAppService
from src.config.settings import settings

logger = logging.getLogger(__name__)


@celery_app.task(name='src.tasks.email_tasks.check_all_users_emails')
def check_all_users_emails():
    """Periodic task to check emails for all active users"""
    logger.info("Starting periodic email check for all users")
    
    # Run async function in sync context
    asyncio.run(process_all_users())
    
    return "Email check completed"


async def process_all_users():
    """Process emails for all active users"""
    async with AsyncSessionLocal() as session:
        # Get all active users
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()
        
        logger.info(f"Processing emails for {len(users)} active users")
        
        for user in users:
            try:
                await process_user_emails(user.id)
            except Exception as e:
                logger.error(f"Error processing emails for user {user.id}: {str(e)}")
                continue


@celery_app.task(name='src.tasks.email_tasks.process_user_emails')
def process_user_emails_task(user_id: int):
    """Task to process emails for a specific user"""
    asyncio.run(process_user_emails(user_id))
    return f"Processed emails for user {user_id}"


async def process_user_emails(user_id: int):
    """Main workflow to process emails for a user"""
    async with AsyncSessionLocal() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            logger.warning(f"User {user_id} not found or inactive")
            return
        
        if not user.gmail_credentials:
            logger.warning(f"User {user_id} has no Gmail credentials")
            return
        
        logger.info(f"Processing emails for user {user_id} ({user.email})")
        
        try:
            # 1. Fetch emails from Gmail
            email_service = EmailMonitorService(user.gmail_credentials)
            emails = email_service.fetch_unread_emails(max_results=settings.MAX_EMAILS_PER_CHECK)
            
            if not emails:
                logger.info(f"No unread emails for user {user_id}")
                return
            
            # 2. Filter out already processed emails
            processed_email_ids = await get_processed_email_ids(session, user_id)
            new_emails = [e for e in emails if e['id'] not in processed_email_ids]
            
            if not new_emails:
                logger.info(f"No new emails to process for user {user_id}")
                return
            
            logger.info(f"Found {len(new_emails)} new emails for user {user_id}")
            
            # 3. Analyze emails with AI
            ai_service = AIAnalyzerService(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL
            )
            
            important_summaries = []
            
            for email in new_emails:
                try:
                    # Classify importance
                    importance = ai_service.classify_importance(email)
                    
                    # Generate summary
                    summary = ai_service.summarize_email(email)
                    
                    # Save to database
                    processed_email = ProcessedEmail(
                        user_id=user_id,
                        email_id=email['id'],
                        sender=email['sender'],
                        subject=email['subject'],
                        body_preview=email['body'][:500],
                        importance_score=importance,
                        summary=summary,
                        processed_at=datetime.utcnow(),
                        sent_to_whatsapp=False
                    )
                    session.add(processed_email)
                    
                    # If important enough, add to summaries list
                    if importance >= user.importance_threshold:
                        important_summaries.append({
                            'email_id': email['id'],
                            'sender': email['sender'],
                            'subject': email['subject'],
                            'summary': summary,
                            'importance': importance
                        })
                    
                except Exception as e:
                    logger.error(f"Error analyzing email {email['id']}: {str(e)}")
                    continue
            
            await session.commit()
            
            # 4. Send WhatsApp message if there are important emails
            if important_summaries:
                logger.info(f"Sending {len(important_summaries)} important email summaries to WhatsApp")
                
                whatsapp_service = WhatsAppService(
                    account_sid=settings.TWILIO_ACCOUNT_SID,
                    auth_token=settings.TWILIO_AUTH_TOKEN,
                    from_number=settings.TWILIO_WHATSAPP_FROM
                )
                
                result = whatsapp_service.send_email_summaries(
                    to_number=user.phone_number,
                    summaries=important_summaries
                )
                
                # Save WhatsApp message record
                whatsapp_message = WhatsAppMessage(
                    user_id=user_id,
                    email_ids=[s['email_id'] for s in important_summaries],
                    message_text=whatsapp_service.format_email_summary_message(important_summaries),
                    twilio_message_sid=result.get('message_sid'),
                    status='sent' if result['success'] else 'failed',
                    error_message=result.get('error'),
                    sent_at=result['sent_at']
                )
                session.add(whatsapp_message)
                
                # Mark emails as sent to WhatsApp
                if result['success']:
                    email_ids = [s['email_id'] for s in important_summaries]
                    await session.execute(
                        select(ProcessedEmail).where(
                            ProcessedEmail.user_id == user_id,
                            ProcessedEmail.email_id.in_(email_ids)
                        )
                    )
                    for email in (await session.execute(
                        select(ProcessedEmail).where(
                            ProcessedEmail.user_id == user_id,
                            ProcessedEmail.email_id.in_(email_ids)
                        )
                    )).scalars():
                        email.sent_to_whatsapp = True
                
                await session.commit()
                
                logger.info(f"Successfully sent WhatsApp message to user {user_id}")
            else:
                logger.info(f"No important emails to send for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error in email processing workflow for user {user_id}: {str(e)}")
            raise


async def get_processed_email_ids(session, user_id: int) -> set:
    """Get set of already processed email IDs for a user"""
    result = await session.execute(
        select(ProcessedEmail.email_id).where(ProcessedEmail.user_id == user_id)
    )
    return set(result.scalars().all())
