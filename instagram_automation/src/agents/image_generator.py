"""Image Generator Agent - Generates images using Nano Banana."""
from typing import Dict, Any, Optional
from src.tools import image_generator, image_processor
from pathlib import Path
from loguru import logger
import asyncio
import uuid


async def image_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Image generator agent node.
    
    Generates images using Nano Banana (Gemini) API based on prompts.
    
    Args:
        state: Current state with image_prompt
        
    Returns:
        Updated state with generated image URL/path
    """
    logger.info("Image Generator Agent: Starting image generation")
    
    try:
        # Extract prompt from state
        prompt = state.get("image_prompt")
        if not prompt:
            raise ValueError("No image prompt provided")
        
        post_type = state.get("post_type", "post")
        
        # Generate image (Nano Banana handles dimensions automatically or fixed)
        logger.info(f"Generating image with Nano Banana")
        image_data_urls = await image_generator.generate_image(
            prompt=prompt,
            num_outputs=1
        )
        
        if not image_data_urls:
            raise ValueError("No images generated")
        
        # Save locally since Nano Banana returns base64 data
        # Check if we have a proper directory for images
        output_dir = Path("data/generated_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{uuid.uuid4()}.jpg"
        save_path = output_dir / filename
        
        # Download (decode) and save
        image_bytes = await image_generator.download_image(
            image_data_urls[0],
            save_path
        )
        
        # Process image for Instagram dimensions
        processed_bytes = await asyncio.to_thread(
            image_processor.resize_for_instagram,
            image_bytes,
            post_type
        )
        
        # Save processed image (overwrite)
        with open(save_path, "wb") as f:
            f.write(processed_bytes)
            
        
        # Determine strict URL for API (must be public)
        # If the source was a web URL (Pollinations), use it directly.
        # If it was base64 (data:), we only have the local file which might fail 
        # unless we implement a public upload logic.
        api_url = str(save_path.absolute())
        original_url = image_data_urls[0]
        if original_url.startswith("http"):
             api_url = original_url
             
        logger.info(f"Image Generator Agent: Successfully generated and saved image: {save_path}")
        
        # Return path as URL for local file (or upload to CDN in production)
        # For now, we'll use the absolute path for the posting agent
        return {
            "image_url": api_url,
            "local_path": str(save_path),
            "current_step": "image_generated",
            "messages": [{
                "role": "assistant",
                "content": f"Generated image from prompt with Nano Banana: {prompt[:100]}..."
            }]
        }
        
    except Exception as e:
        error_msg = f"Image Generator Agent error: {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": "error",
            "errors": [error_msg],
            "messages": [{
                "role": "assistant",
                "content": error_msg
            }]
        }


class ImageGeneratorAgent:
    """Image Generator Agent class."""
    
    def __init__(self):
        """Initialize Image Generator Agent."""
        self.name = "image_generator"
        logger.info("Initialized Image Generator Agent")
    
    async def generate_image(
        self,
        prompt: str,
        post_type: str = "post",
        save_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Generate image from prompt.
        
        Args:
            prompt: Image generation prompt
            post_type: Type of post (post, story, reel)
            save_path: Optional specific path to save the image
            
        Returns:
            Dictionary with local path and metadata
        """
        state = {
            "image_prompt": prompt,
            "post_type": post_type,
            "current_step": "init",
            "errors": [],
            "messages": []
        }
        
        result = await image_generator_node(state)
        
        # If specific save path requested and successful generation
        if save_path and result.get("image_url"):
            try:
                # Copy/Move file to requested location
                import shutil
                source = Path(result["local_path"])
                save_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, save_path)
                result["local_path"] = str(save_path)
                result["image_url"] = str(save_path.absolute())
            except Exception as e:
                logger.error(f"Error moving image: {e}")
        
        return result
