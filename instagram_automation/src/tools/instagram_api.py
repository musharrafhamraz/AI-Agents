"""Instagram Graph API wrapper."""
from typing import Optional, Dict, Any, List
import httpx
from pathlib import Path
from src.config import settings
from loguru import logger
import asyncio


class InstagramAPI:
    """Instagram Graph API client."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        """Initialize Instagram API client."""
        self.access_token = settings.instagram_access_token
        self.business_account_id = settings.instagram_business_account_id
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Initialized Instagram API client")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram account information.
        
        Returns:
            Account information dictionary
        """
        url = f"{self.BASE_URL}/{self.business_account_id}"
        params = {
            "fields": "id,username,name,biography,profile_picture_url,followers_count,follows_count,media_count",
            "access_token": self.access_token
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved account info for @{data.get('username')}")
            return data
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    async def create_media_container(
        self,
        image_url: str,
        caption: str,
        is_carousel: bool = False
    ) -> str:
        """Create media container for posting.
        
        Args:
            image_url: URL of the image to post
            caption: Post caption
            is_carousel: Whether this is part of a carousel
            
        Returns:
            Container ID
        """
        url = f"{self.BASE_URL}/{self.business_account_id}/media"
        
        data = {
            "image_url": image_url,
            "access_token": self.access_token
        }
        
        if not is_carousel:
            data["caption"] = caption
        
        try:
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            container_id = response.json()["id"]
            logger.info(f"Created media container: {container_id}")
            return container_id
        except Exception as e:
            logger.error(f"Error creating media container: {e}")
            raise
    
    async def publish_media(self, container_id: str) -> str:
        """Publish media container.
        
        Args:
            container_id: Media container ID
            
        Returns:
            Published media ID
        """
        url = f"{self.BASE_URL}/{self.business_account_id}/media_publish"
        data = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        try:
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            media_id = response.json()["id"]
            logger.info(f"Published media: {media_id}")
            return media_id
        except Exception as e:
            logger.error(f"Error publishing media: {e}")
            raise
    
    async def post_image(self, image_url: str, caption: str) -> str:
        """Post an image to Instagram.
        
        Args:
            image_url: URL of the image
            caption: Post caption
            
        Returns:
            Published media ID
        """
        try:
            # Create container
            container_id = await self.create_media_container(image_url, caption)
            
            # Wait a bit for processing
            await asyncio.sleep(2)
            
            # Publish
            media_id = await self.publish_media(container_id)
            logger.info(f"Successfully posted image: {media_id}")
            return media_id
        except Exception as e:
            logger.error(f"Error posting image: {e}")
            raise
    
    async def get_media_insights(
        self,
        media_id: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get insights for a media post.
        
        Args:
            media_id: Media ID
            metrics: List of metrics to retrieve
            
        Returns:
            Insights data
        """
        if metrics is None:
            metrics = [
                "engagement",
                "impressions",
                "reach",
                "saved",
                "likes",
                "comments"
            ]
        
        url = f"{self.BASE_URL}/{media_id}/insights"
        params = {
            "metric": ",".join(metrics),
            "access_token": self.access_token
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved insights for media: {media_id}")
            return data
        except Exception as e:
            logger.error(f"Error getting media insights: {e}")
            raise
    
    async def get_comments(
        self,
        media_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get comments on a media post.
        
        Args:
            media_id: Media ID
            limit: Maximum number of comments to retrieve
            
        Returns:
            List of comments
        """
        url = f"{self.BASE_URL}/{media_id}/comments"
        params = {
            "fields": "id,text,username,timestamp,like_count",
            "limit": limit,
            "access_token": self.access_token
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            comments = response.json().get("data", [])
            logger.info(f"Retrieved {len(comments)} comments for media: {media_id}")
            return comments
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            raise
    
    async def reply_to_comment(
        self,
        comment_id: str,
        reply_text: str
    ) -> str:
        """Reply to a comment.
        
        Args:
            comment_id: Comment ID
            reply_text: Reply text
            
        Returns:
            Reply comment ID
        """
        url = f"{self.BASE_URL}/{comment_id}/replies"
        data = {
            "message": reply_text,
            "access_token": self.access_token
        }
        
        try:
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            reply_id = response.json()["id"]
            logger.info(f"Posted reply to comment {comment_id}: {reply_id}")
            return reply_id
        except Exception as e:
            logger.error(f"Error replying to comment: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global instance
instagram_api = InstagramAPI()
