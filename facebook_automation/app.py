"""FastAPI application for Facebook automation with integrated scheduler."""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
import sys
import logging
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Add src to path for CrewAI imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the crew
from facebook_automation.crew import FacebookAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Facebook Automation API",
    description="Automated Facebook posting with AI-powered content generation",
    version="1.0.0"
)

# Initialize scheduler
scheduler = BackgroundScheduler(timezone=pytz.UTC)

# Content themes for variety
CONTENT_THEMES = [
    "Technology and Innovation",
    "Digital Marketing Trends",
    "Social Media Tips",
    "Business Growth Strategies",
    "Productivity Hacks",
    "Industry News and Updates",
    "Success Stories",
    "Motivational Content",
    "Educational Content",
    "Behind the Scenes",
    "Customer Success Stories",
    "Product Features",
    "Tips and Tricks",
    "Industry Insights",
    "Future Trends"
]

theme_index = 0


# Request/Response Models
class PostRequest(BaseModel):
    """Request model for creating a post."""
    topic: Optional[str] = Field(None, description="Topic for the post")
    target_audience: Optional[str] = Field(
        "Tech enthusiasts and entrepreneurs",
        description="Target audience"
    )
    brand_voice: Optional[str] = Field(
        "Informative, inspiring, and engaging",
        description="Brand voice"
    )
    auto_publish: bool = Field(True, description="Auto-publish to Facebook")


class PostResponse(BaseModel):
    """Response model for post creation."""
    status: str
    message: str
    timestamp: str
    topic: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    services: dict


class ScheduleInfo(BaseModel):
    """Schedule information."""
    total_jobs: int
    scheduler_running: bool
    schedule: List[dict]
    posts_per_day: dict


def get_next_theme() -> str:
    """Get the next content theme in rotation."""
    global theme_index
    theme = CONTENT_THEMES[theme_index % len(CONTENT_THEMES)]
    theme_index += 1
    return theme


def run_scheduled_post():
    """Run a scheduled post with rotating themes."""
    try:
        theme = get_next_theme()
        logger.info(f"Starting scheduled post with theme: {theme}")
        
        inputs = {
            'topic': theme,
            'target_audience': os.getenv('TARGET_AUDIENCE', 'Tech enthusiasts and entrepreneurs'),
            'brand_voice': os.getenv('BRAND_VOICE', 'Informative, inspiring, and engaging')
        }
        
        result = FacebookAutomation().crew().kickoff(inputs=inputs)
        logger.info(f"✅ Scheduled post completed successfully! Theme: {theme}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in scheduled post: {str(e)}")
        return None


def setup_scheduler():
    """Set up the posting schedule - 3-4 posts per day."""
    try:
        # Monday - 4 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='mon', hour=9, minute=0), id='mon_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='mon', hour=13, minute=0), id='mon_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='mon', hour=17, minute=0), id='mon_3')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='mon', hour=20, minute=0), id='mon_4')
        
        # Tuesday - 3 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='tue', hour=10, minute=0), id='tue_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='tue', hour=14, minute=0), id='tue_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='tue', hour=19, minute=0), id='tue_3')
        
        # Wednesday - 4 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='wed', hour=8, minute=0), id='wed_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='wed', hour=11, minute=0), id='wed_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='wed', hour=14, minute=0), id='wed_3')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='wed', hour=17, minute=0), id='wed_4')
        
        # Thursday - 3 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='thu', hour=9, minute=30), id='thu_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='thu', hour=13, minute=30), id='thu_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='thu', hour=16, minute=30), id='thu_3')
        
        # Friday - 4 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='fri', hour=8, minute=30), id='fri_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='fri', hour=11, minute=30), id='fri_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='fri', hour=14, minute=30), id='fri_3')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='fri', hour=18, minute=0), id='fri_4')
        
        # Saturday - 3 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sat', hour=10, minute=0), id='sat_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sat', hour=14, minute=0), id='sat_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sat', hour=18, minute=0), id='sat_3')
        
        # Sunday - 3 posts
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sun', hour=11, minute=0), id='sun_1')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sun', hour=16, minute=0), id='sun_2')
        scheduler.add_job(run_scheduled_post, CronTrigger(day_of_week='sun', hour=20, minute=0), id='sun_3')
        
        logger.info("✅ Scheduler configured with 24 posts per week (3-4 per day)")
        
    except Exception as e:
        logger.error(f"❌ Error setting up scheduler: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts."""
    logger.info("🚀 Starting Facebook Automation API...")
    
    # Check for required environment variables
    required_vars = ['GROQ_API_KEY', 'FACEBOOK_PAGE_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
    else:
        logger.info("✅ All required environment variables found")
    
    # Start scheduler
    setup_scheduler()
    scheduler.start()
    logger.info("✅ Scheduler started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the app shuts down."""
    logger.info("🛑 Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("✅ Scheduler stopped")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Facebook Automation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "create_post": "POST /api/create-post",
            "trigger_post": "POST /api/trigger-post",
            "schedule": "GET /api/schedule",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "scheduler": "running" if scheduler.running else "stopped",
            "scheduled_jobs": len(scheduler.get_jobs())
        }
    }


@app.post("/api/create-post", response_model=PostResponse)
async def create_post(request: PostRequest, background_tasks: BackgroundTasks):
    """Create and optionally publish a Facebook post."""
    try:
        topic = request.topic or get_next_theme()
        
        logger.info(f"Creating post with topic: {topic}")
        logger.info(f"Target audience: {request.target_audience}")
        logger.info(f"Brand voice: {request.brand_voice}")
        
        inputs = {
            'topic': topic,
            'target_audience': request.target_audience,
            'brand_voice': request.brand_voice
        }
        
        # Run the crew
        logger.info("Starting CrewAI execution...")
        result = FacebookAutomation().crew().kickoff(inputs=inputs)
        logger.info(f"CrewAI execution completed. Result type: {type(result)}")
        logger.info(f"CrewAI result: {str(result)[:500]}")  # Log first 500 chars
        
        return {
            "status": "success",
            "message": "Post created and published successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "topic": topic
        }
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trigger-post", response_model=PostResponse)
async def trigger_post():
    """Manually trigger a post immediately."""
    try:
        theme = get_next_theme()
        logger.info(f"Manual trigger - creating post with theme: {theme}")
        
        inputs = {
            'topic': theme,
            'target_audience': os.getenv('TARGET_AUDIENCE', 'Tech enthusiasts and entrepreneurs'),
            'brand_voice': os.getenv('BRAND_VOICE', 'Informative, inspiring, and engaging')
        }
        
        result = FacebookAutomation().crew().kickoff(inputs=inputs)
        
        return {
            "status": "success",
            "message": "Post triggered and published successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "topic": theme
        }
        
    except Exception as e:
        logger.error(f"Error triggering post: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schedule", response_model=ScheduleInfo)
async def get_schedule():
    """Get the current posting schedule."""
    jobs = scheduler.get_jobs()
    schedule_info = []
    
    for job in jobs:
        schedule_info.append({
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "total_jobs": len(jobs),
        "scheduler_running": scheduler.running,
        "schedule": schedule_info,
        "posts_per_day": {
            "Monday": 4,
            "Tuesday": 3,
            "Wednesday": 4,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 3,
            "Sunday": 3
        }
    }


@app.get("/api/test-facebook")
async def test_facebook():
    """Test Facebook API connection."""
    try:
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not page_access_token or not page_id:
            return {
                "status": "error",
                "message": "Missing Facebook credentials",
                "has_token": bool(page_access_token),
                "has_page_id": bool(page_id)
            }
        
        # Test API call to get page info
        url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            "fields": "name,fan_count,followers_count",
            "access_token": page_access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "status": "success",
            "message": "Facebook API connection working",
            "page_name": data.get("name"),
            "fans": data.get("fan_count"),
            "followers": data.get("followers_count"),
            "page_id": page_id
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
        
        return {
            "status": "error",
            "message": f"Facebook API error: {error_msg}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
