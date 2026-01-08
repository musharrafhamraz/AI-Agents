"""Posting Agent - Publishes content to Instagram."""
from typing import Dict, Any
from src.tools import instagram_api
from src.models import Post, PostStatus
from loguru import logger
import asyncio


async def posting_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Posting agent node.
    
    Publishes content to Instagram using Graph API.
    
    Args:
        state: Current state with post data
        
    Returns:
        Updated state with publishing results
    """
    logger.info("Posting Agent: Starting post publication")
    
    try:
        # Extract post data from state
        image_url = state.get("image_url")
        caption = state.get("caption", "")
        hashtags = state.get("hashtags", [])
        
        if not image_url:
            raise ValueError("No image URL provided")
        
        # Create full caption with hashtags
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        full_caption = f"{caption}\n\n{hashtag_str}".strip()
        
        # Check if auto-publish is enabled
        auto_publish = state.get("auto_publish", False)
        
        if not auto_publish:
            logger.info("Auto-publish disabled, post queued for review")
            return {
                "current_step": "awaiting_review",
                "status": PostStatus.SCHEDULED,
                "messages": [{
                    "role": "assistant",
                    "content": "Post created and queued for human review"
                }]
            }
        
        # Publish to Instagram
        logger.info("Publishing to Instagram")
        media_id = await instagram_api.post_image(image_url, full_caption)
        
        logger.info(f"Posting Agent: Successfully published post: {media_id}")
        
        return {
            "instagram_media_id": media_id,
            "current_step": "published",
            "status": PostStatus.PUBLISHED,
            "messages": [{
                "role": "assistant",
                "content": f"Successfully published post to Instagram: {media_id}"
            }]
        }
        
    except Exception as e:
        error_msg = f"Posting Agent error: {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": "error",
            "status": PostStatus.FAILED,
            "errors": [error_msg],
            "messages": [{
                "role": "assistant",
                "content": error_msg
            }]
        }


class PostingAgent:
    """Posting Agent class."""
    
    def __init__(self):
        """Initialize Posting Agent."""
        self.name = "posting_agent"
        logger.info("Initialized Posting Agent")
    
    async def publish_post(
        self,
        image_url: str,
        caption: str,
        hashtags: list[str],
        auto_publish: bool = False
    ) -> Dict[str, Any]:
        """Publish post to Instagram.
        
        Args:
            image_url: URL of the image to post
            caption: Post caption
            hashtags: List of hashtags
            auto_publish: Whether to auto-publish or queue for review
            
        Returns:
            Dictionary with publishing results
        """
        state = {
            "image_url": image_url,
            "caption": caption,
            "hashtags": hashtags,
            "auto_publish": auto_publish,
            "current_step": "init",
            "errors": [],
            "messages": []
        }
        
        result = await posting_agent_node(state)
        return result
    
    async def get_post_insights(self, media_id: str) -> Dict[str, Any]:
        """Get insights for a published post.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Post insights data
        """
        try:
            insights = await instagram_api.get_media_insights(media_id)
            logger.info(f"Retrieved insights for post: {media_id}")
            return insights
        except Exception as e:
            logger.error(f"Error getting post insights: {e}")
            raise
