"""Image generation and processing tools using Google Nano Banana."""
from typing import Optional, List
import io
from pathlib import Path
from PIL import Image
from google import genai
from src.config import settings
from loguru import logger
import base64
import requests
import urllib.parse
import time


class PollinationsImageGenerator:
    """Free image generator using Pollinations.ai."""
    
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        logger.info("Initialized Pollinations.ai image generator")
        
    async def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        seed: Optional[int] = None
    ) -> List[str]:
        """Generate image using Pollinations.ai (returns URL)."""
        try:
            # Clean prompt for URL
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Construct URL with parameters
            # nologo=true to remove watermark if possible (supported by some models)
            # model=flux is default but good to specify if needed
            image_url = f"{self.base_url}/{encoded_prompt}?width={width}&height={height}&nologo=true"
            
            if seed:
                image_url += f"&seed={seed}"
            else:
                # Add random seed to avoid caching
                image_url += f"&seed={int(time.time())}"
                
            logger.info(f"Generated Pollinations URL for prompt: {prompt[:50]}...")
            return [image_url]
            
        except Exception as e:
            logger.error(f"Error generating with Pollinations: {e}")
            raise


class ImageGenerator:
    """Image generation wrapper supporting multiple providers."""
    
    def __init__(self):
        """Initialize image generator based on settings."""
        self.provider = getattr(settings, "image_provider", "google").lower()
        self.google_client = None
        self.pollinations = None
        
        if self.provider == "google":
            try:
                self.google_client = genai.Client(api_key=settings.google_api_key)
                self.model = settings.image_model
                logger.info(f"Initialized Nano Banana with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Nano Banana client: {e}")
        
        elif self.provider == "pollinations":
            self.pollinations = PollinationsImageGenerator()
            
    async def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1080,
        num_outputs: int = 1,
        output_format: str = "jpeg",
        output_quality: int = 90
    ) -> List[str]:
        """Generate image from prompt.
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            num_outputs: Number of images (only 1 supported for now)
            
        Returns:
            List of image URLs or data URLs
        """
        if self.provider == "pollinations":
            if not self.pollinations:
                self.pollinations = PollinationsImageGenerator()
            return await self.pollinations.generate_image(prompt, width, height)
            
        # Default to Google (Nano Banana)
        if not self.google_client:
             # Fallback to pollinations if Google fails or not configured
             logger.warning("Google client not ready, falling back to Pollinations")
             if not self.pollinations:
                 self.pollinations = PollinationsImageGenerator()
             return await self.pollinations.generate_image(prompt, width, height)
        
        try:
            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Call the API
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            image_urls = []
            
            # Process response parts
            for part in response.parts:
                if part.inline_data:
                    # Convert raw bytes to base64 data URL
                    image_bytes = part.inline_data.data
                    b64_data = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    data_url = f"data:{mime_type};base64,{b64_data}"
                    image_urls.append(data_url)
            
            if not image_urls:
                raise ValueError("No images returned in response")
            
            logger.info(f"Generated {len(image_urls)} image(s)")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise
    
    async def download_image(self, url: str, save_path: Optional[Path] = None) -> bytes:
        """Process image data (from data URL or download).
        
        Args:
            url: Image URL or Data URL
            save_path: Optional path to save the image
            
        Returns:
            Image bytes
        """
        try:
            # Handle Data URL
            if url.startswith("data:"):
                # defined as data:image/jpeg;base64,...
                header, encoded = url.split(",", 1)
                image_bytes = base64.b64decode(encoded)
            else:
                # Handle regular URL (Pollinations or others)
                import httpx
                # Pollinations takes time to generate, so we need a long timeout
                async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    image_bytes = response.content
            
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(image_bytes)
                logger.info(f"Saved image to {save_path}")
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error processing image data: {e}")
            raise


class ImageProcessor:
    """Image processing utilities."""
    
    @staticmethod
    def resize_for_instagram(
        image_bytes: bytes,
        post_type: str = "post"
    ) -> bytes:
        """Resize image for Instagram.
        
        Args:
            image_bytes: Original image bytes
            post_type: Type of post (post, story, reel)
            
        Returns:
            Resized image bytes
        """
        # Instagram dimensions
        dimensions = {
            "post": (1080, 1080),      # Square
            "portrait": (1080, 1350),  # Portrait
            "landscape": (1080, 566),  # Landscape
            "story": (1080, 1920),     # Story/Reel
            "reel": (1080, 1920),      # Reel
        }
        
        target_size = dimensions.get(post_type, (1080, 1080))
        
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Resize maintaining aspect ratio (crop to fill)
            # Create new image with target size
            new_image = Image.new("RGB", target_size, (255, 255, 255))
            
            # Calculate scaling to fill
            width_ratio = target_size[0] / image.width
            height_ratio = target_size[1] / image.height
            scale = max(width_ratio, height_ratio)
            
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop
            left = (new_width - target_size[0]) // 2
            top = (new_height - target_size[1]) // 2
            
            new_image.paste(resized, (-left, -top))
            
            # Save to bytes
            output = io.BytesIO()
            new_image.save(output, format="JPEG", quality=95, optimize=True)
            output.seek(0)
            
            logger.info(f"Resized image to {target_size} for {post_type}")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            raise
    
    @staticmethod
    def optimize_image(
        image_bytes: bytes,
        max_size_mb: float = 8.0,
        quality: int = 95
    ) -> bytes:
        """Optimize image size for Instagram upload.
        
        Args:
            image_bytes: Original image bytes
            max_size_mb: Maximum file size in MB
            quality: JPEG quality (0-100)
            
        Returns:
            Optimized image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Iteratively reduce quality if needed
            output = io.BytesIO()
            current_quality = quality
            
            while current_quality > 50:
                output.seek(0)
                output.truncate()
                image.save(output, format="JPEG", quality=current_quality, optimize=True)
                
                size_mb = output.tell() / (1024 * 1024)
                if size_mb <= max_size_mb:
                    break
                
                current_quality -= 5
            
            output.seek(0)
            logger.info(f"Optimized image to {size_mb:.2f}MB at quality {current_quality}")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            raise


# Global instances
image_generator = ImageGenerator()
image_processor = ImageProcessor()
