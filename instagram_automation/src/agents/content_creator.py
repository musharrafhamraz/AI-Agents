"""Content Creator Agent - Generates captions and hashtags using Google Gemini."""
from typing import Dict, Any
from src.tools import gemini_llm
from src.graph.state import ContentCreationState
from loguru import logger


async def content_creator_node(state: ContentCreationState) -> Dict[str, Any]:
    """Content creator agent node.
    
    Generates engaging captions and hashtags using Google Gemini.
    
    Args:
        state: Current content creation state
        
    Returns:
        Updated state with generated content
    """
    logger.info("Content Creator Agent: Starting content generation")
    
    try:
        # Extract input from state
        theme = state.get("content_theme", "lifestyle")
        brand_voice = state.get("brand_voice", "professional and friendly")
        target_audience = state.get("target_audience", "young professionals")
        
        # Generate caption
        logger.info(f"Generating caption for theme: {theme}")
        caption_result = await gemini_llm.generate_caption(
            theme=theme,
            brand_voice=brand_voice,
            target_audience=target_audience
        )
        
        caption = caption_result.get("caption", "")
        
        # Generate hashtags
        logger.info("Generating hashtags")
        hashtags = await gemini_llm.generate_hashtags(
            caption=caption,
            theme=theme,
            count=15
        )
        
        # Generate image prompt
        logger.info("Generating image prompt")
        image_prompt = await gemini_llm.generate_image_prompt(
            caption=caption,
            theme=theme,
            brand_name=state.get("brand_name", "Brand")
        )
        
        logger.info("Content Creator Agent: Successfully generated content")
        
        return {
            "caption": caption,
            "hashtags": hashtags,
            "image_prompt": image_prompt,
            "current_step": "content_created",
            "messages": [{
                "role": "assistant",
                "content": f"Generated caption and {len(hashtags)} hashtags for theme: {theme}"
            }]
        }
        
    except Exception as e:
        error_msg = f"Content Creator Agent error: {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": "error",
            "errors": [error_msg],
            "messages": [{
                "role": "assistant",
                "content": error_msg
            }]
        }


class ContentCreatorAgent:
    """Content Creator Agent class."""
    
    def __init__(self):
        """Initialize Content Creator Agent."""
        self.name = "content_creator"
        logger.info("Initialized Content Creator Agent")
    
    async def create_content(
        self,
        theme: str,
        brand_voice: str,
        target_audience: str,
        brand_name: str = "Brand"
    ) -> Dict[str, Any]:
        """Create content for Instagram post.
        
        Args:
            theme: Content theme
            brand_voice: Brand voice description
            target_audience: Target audience description
            brand_name: Brand name
            
        Returns:
            Dictionary with caption, hashtags, and image prompt
        """
        state: ContentCreationState = {
            "content_theme": theme,
            "brand_voice": brand_voice,
            "target_audience": target_audience,
            "brand_name": brand_name,
            "hashtags": [],
            "current_step": "init",
            "requires_review": False,
            "approved": False,
            "errors": [],
            "messages": [],
            "caption": None,
            "image_prompt": None,
            "image_url": None
        }
        
        result = await content_creator_node(state)
        return result
