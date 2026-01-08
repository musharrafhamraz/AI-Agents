"""LLM tools using Google Gemini (via google-genai)."""
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
from src.config import settings
import json
from loguru import logger


class GeminiLLM:
    """Google Gemini LLM wrapper using google-genai library."""
    
    def __init__(self):
        """Initialize Gemini API."""
        try:
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model = settings.gemini_model
            logger.info(f"Initialized Gemini model: {settings.gemini_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    async def generate_caption(
        self,
        theme: str,
        brand_voice: str,
        target_audience: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Instagram caption with hashtags."""
        if not self.client:
            raise ValueError("Gemini client not initialized")

        prompt = f"""You are an expert Instagram content creator. Generate an engaging Instagram post caption.

Theme: {theme}
Brand Voice: {brand_voice}
Target Audience: {target_audience}
{f'Additional Context: {additional_context}' if additional_context else ''}

Requirements:
- Create a compelling, engaging caption that matches the brand voice
- Keep it concise but impactful (150-200 characters ideal)
- Include a call-to-action when appropriate
- Make it relatable to the target audience
- Use emojis strategically (2-4 emojis)
- DO NOT include hashtags in the caption

Return your response in this exact JSON format:
{{
    "caption": "your engaging caption here",
    "caption_explanation": "brief explanation of your creative choices"
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            logger.info(f"Generated caption for theme: {theme}")
            return result
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            raise
    
    async def generate_hashtags(
        self,
        caption: str,
        theme: str,
        count: int = 15
    ) -> List[str]:
        """Generate relevant hashtags."""
        if not self.client:
            raise ValueError("Gemini client not initialized")

        prompt = f"""You are an Instagram hashtag expert. Generate {count} relevant, high-performing hashtags.

Caption: {caption}
Theme: {theme}

Requirements:
- Mix of popular (100k-1M posts) and niche (10k-100k posts) hashtags
- Include 2-3 trending hashtags
- All hashtags must be relevant to the content
- Avoid banned or spammy hashtags
- Use a mix of broad and specific hashtags
- Return ONLY the hashtag words, without the # symbol

Return your response in this exact JSON format:
{{
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", ...],
    "strategy_explanation": "brief explanation of your hashtag strategy"
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            hashtags = result.get("hashtags", [])[:count]
            logger.info(f"Generated {len(hashtags)} hashtags")
            return hashtags
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            raise
    
    async def generate_image_prompt(
        self,
        caption: str,
        theme: str,
        brand_name: str
    ) -> str:
        """Generate image generation prompt."""
        if not self.client:
            raise ValueError("Gemini client not initialized")

        prompt = f"""You are an expert at creating prompts for AI image generation. Create a detailed, vivid prompt for generating an Instagram post image.

Brand: {brand_name}
Theme: {theme}
Caption: {caption}

Requirements:
- Create a visually striking, Instagram-worthy image concept
- Focus on composition, lighting, and mood
- Include specific details about colors, style, and atmosphere
- Make it relevant to the caption and theme
- Ensure it's appropriate for Instagram (no controversial content)
- Keep the prompt focused and under 200 words
- Use descriptive, visual language

Return your response in this exact JSON format:
{{
    "image_prompt": "your detailed image generation prompt here",
    "style_notes": "brief notes on the visual style and mood"
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            image_prompt = result.get("image_prompt", "")
            logger.info(f"Generated image prompt for theme: {theme}")
            return image_prompt
        except Exception as e:
            logger.error(f"Error generating image prompt: {e}")
            raise
    
    async def generate_comment_reply(
        self,
        comment_text: str,
        post_caption: str,
        brand_voice: str,
        sentiment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate reply to Instagram comment."""
        if not self.client:
            raise ValueError("Gemini client not initialized")

        prompt = f"""You are a social media manager responding to Instagram comments. Generate an authentic, engaging reply.

Comment: {comment_text}
Post Caption: {post_caption}
Brand Voice: {brand_voice}
{f'Detected Sentiment: {sentiment}' if sentiment else ''}

Requirements:
- Keep it friendly and conversational
- Match the brand voice
- Be genuine and authentic (not robotic)
- Keep it concise (1-2 sentences)
- Use 1-2 emojis if appropriate
- If the comment is negative, be empathetic and helpful
- If it's a question, provide a helpful answer

Return your response in this exact JSON format:
{{
    "reply": "your reply here",
    "should_flag": false,
    "flag_reason": "reason if should_flag is true, otherwise null"
}}

Set "should_flag" to true if:
- The comment contains hate speech or harassment
- It requires human intervention (complex issue, complaint, etc.)
- You're unsure how to respond appropriately
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            logger.info("Generated comment reply")
            return result
        except Exception as e:
            logger.error(f"Error generating comment reply: {e}")
            raise
    
    async def analyze_content_performance(
        self,
        posts_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content performance and generate insights."""
        if not self.client:
            raise ValueError("Gemini client not initialized")

        prompt = f"""You are a social media analytics expert. Analyze the performance data and provide actionable insights.

Posts Data:
{json.dumps(posts_data, indent=2)}

Analyze:
- Which content themes perform best
- Optimal posting times
- Hashtag effectiveness
- Engagement patterns
- Areas for improvement

Return your response in this exact JSON format:
{{
    "top_performing_themes": ["theme1", "theme2", "theme3"],
    "best_posting_times": ["HH:MM", "HH:MM"],
    "top_hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "insights": [
        {{"title": "Insight Title", "description": "Detailed insight", "confidence": 0.85}}
    ],
    "recommendations": [
        "Actionable recommendation 1",
        "Actionable recommendation 2"
    ]
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            logger.info("Generated performance insights")
            return result
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            raise


# Global instance
gemini_llm = GeminiLLM()
