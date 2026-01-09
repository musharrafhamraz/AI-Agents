"""FastAPI application for Instagram Automation - Render.com deployment."""
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
from loguru import logger

# Import Instagram automation components
from src.agents import ContentCreatorAgent, ImageGeneratorAgent, PostingAgent, EngagementAgent
from src.config import settings

# Configure logging
logger.add(
    "logs/instagram_agent_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

app = FastAPI(
    title="Instagram Automation API",
    description="AI-powered Instagram content creation and automation",
    version="1.0.0"
)


# Request/Response Models
class CreatePostRequest(BaseModel):
    theme: str = Field(..., description="Content theme or topic")
    brand_voice: Optional[str] = Field(None, description="Brand voice (uses config default if not provided)")
    target_audience: Optional[str] = Field(None, description="Target audience (uses config default if not provided)")
    auto_publish: bool = Field(False, description="Auto-publish without review")


class CreatePostResponse(BaseModel):
    success: bool
    message: str
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    image_url: Optional[str] = None
    instagram_media_id: Optional[str] = None
    status: str


class ProcessCommentsRequest(BaseModel):
    media_id: str = Field(..., description="Instagram media ID")
    auto_reply: bool = Field(False, description="Auto-reply to comments")


class ProcessCommentsResponse(BaseModel):
    success: bool
    message: str
    processed_count: int
    flagged_count: int
    flagged_comments: Optional[List[dict]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict


# Health Check Endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Render.com monitoring."""
    services = {
        "api": "healthy",
        "google_gemini": "configured" if settings.google_api_key else "missing",
        "instagram_api": "configured" if settings.instagram_access_token else "missing"
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }


# Create Post Endpoint
@app.post("/api/create-post", response_model=CreatePostResponse)
async def create_post(request: CreatePostRequest, background_tasks: BackgroundTasks):
    """
    Create and optionally publish an Instagram post.
    
    This endpoint:
    1. Generates caption and hashtags using AI
    2. Generates an image based on the theme
    3. Optionally publishes to Instagram
    """
    try:
        logger.info(f"Creating post with theme: {request.theme}")
        
        # Use config defaults if not provided
        brand_voice = request.brand_voice or settings.brand_voice
        target_audience = request.target_audience or settings.target_audience
        
        # Step 1: Generate content
        content_agent = ContentCreatorAgent()
        content_result = await content_agent.create_content(
            theme=request.theme,
            brand_voice=brand_voice,
            target_audience=target_audience,
            brand_name=settings.brand_name
        )
        
        if content_result.get("errors"):
            raise HTTPException(status_code=500, detail=content_result["errors"][0])
        
        caption = content_result.get("caption", "")
        hashtags = content_result.get("hashtags", [])
        image_prompt = content_result.get("image_prompt", "")
        
        # Step 2: Generate image
        image_agent = ImageGeneratorAgent()
        image_result = await image_agent.generate_image(image_prompt)
        
        if image_result.get("errors"):
            raise HTTPException(status_code=500, detail=image_result["errors"][0])
        
        image_url = image_result.get("image_url", "")
        
        # Step 3: Publish or queue for review
        instagram_media_id = None
        status = "queued_for_review"
        
        if request.auto_publish or not settings.enable_human_review:
            posting_agent = PostingAgent()
            publish_result = await posting_agent.publish_post(
                image_url=image_url,
                caption=caption,
                hashtags=hashtags,
                auto_publish=True
            )
            
            if publish_result.get("errors"):
                raise HTTPException(status_code=500, detail=publish_result["errors"][0])
            
            instagram_media_id = publish_result.get("instagram_media_id", "")
            status = "published"
            logger.info(f"Post published successfully: {instagram_media_id}")
        else:
            logger.info("Post queued for human review")
        
        return CreatePostResponse(
            success=True,
            message="Post created successfully" if status == "published" else "Post queued for review",
            caption=caption,
            hashtags=hashtags,
            image_url=image_url,
            instagram_media_id=instagram_media_id,
            status=status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Process Comments Endpoint
@app.post("/api/process-comments", response_model=ProcessCommentsResponse)
async def process_comments(request: ProcessCommentsRequest):
    """
    Process comments on an Instagram post.
    
    This endpoint:
    1. Fetches comments from the specified post
    2. Analyzes sentiment and generates replies
    3. Optionally auto-replies to comments
    """
    try:
        logger.info(f"Processing comments for media: {request.media_id}")
        
        engagement_agent = EngagementAgent()
        result = await engagement_agent.process_comments(
            media_id=request.media_id,
            brand_voice=settings.brand_voice,
            post_caption="",  # Could fetch from API if needed
            auto_reply=request.auto_reply
        )
        
        if result.get("errors"):
            raise HTTPException(status_code=500, detail=result["errors"][0])
        
        processed = result.get("processed_comments", [])
        flagged = result.get("flagged_for_review", [])
        
        logger.info(f"Processed {len(processed)} comments, flagged {len(flagged)}")
        
        return ProcessCommentsResponse(
            success=True,
            message=f"Processed {len(processed)} comments",
            processed_count=len(processed),
            flagged_count=len(flagged),
            flagged_comments=flagged if flagged else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Test Connection Endpoint
@app.get("/api/test-connections")
async def test_connections():
    """Test all API connections."""
    results = {
        "google_gemini": {"status": "unknown", "message": ""},
        "instagram_api": {"status": "unknown", "message": ""},
        "image_generation": {"status": "unknown", "message": ""}
    }
    
    # Test Google Gemini
    try:
        from src.tools import gemini_llm
        await gemini_llm.generate_caption(
            theme="test",
            brand_voice="friendly",
            target_audience="everyone"
        )
        results["google_gemini"] = {"status": "connected", "message": "Successfully connected"}
    except Exception as e:
        results["google_gemini"] = {"status": "error", "message": str(e)}
    
    # Test Instagram API
    try:
        from src.tools import instagram_api
        account_info = await instagram_api.get_account_info()
        results["instagram_api"] = {
            "status": "connected",
            "message": f"Connected as @{account_info.get('username', 'unknown')}"
        }
    except Exception as e:
        results["instagram_api"] = {"status": "error", "message": str(e)}
    
    # Test Image Generation
    try:
        results["image_generation"] = {
            "status": "configured",
            "message": f"Provider: {settings.image_provider}, Model: {settings.image_model}"
        }
    except Exception as e:
        results["image_generation"] = {"status": "error", "message": str(e)}
    
    return results


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
