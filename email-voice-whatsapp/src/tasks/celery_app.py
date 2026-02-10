from celery import Celery
from celery.schedules import crontab
from src.config.settings import settings

celery_app = Celery(
    'email_voice_whatsapp',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.tasks.email_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'check-emails-hourly': {
        'task': 'src.tasks.email_tasks.check_all_users_emails',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
}

if __name__ == '__main__':
    celery_app.start()
