"""Custom tools for Facebook automation."""
from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import os


# Facebook Page List Tool
class FacebookPageListInput(BaseModel):
    """Input schema for FacebookPageListTool."""
    pass


class FacebookPageListTool(BaseTool):
    name: str = "Facebook Page List Tool"
    description: str = "Lists all Facebook Pages you manage with their details"
    args_schema: Type[BaseModel] = FacebookPageListInput

    def _run(self) -> str:
        """List all pages the user manages."""
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        
        if not page_access_token:
            return "Error: Missing Facebook access token"
        
        url = "https://graph.facebook.com/v18.0/me/accounts"
        
        params = {
            "access_token": page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("data", [])
            if not pages:
                return "No pages found"
            
            result = "Your Facebook Pages:\n\n"
            for page in pages:
                result += f"📄 {page.get('name', 'Unknown')}\n"
                result += f"   ID: {page.get('id')}\n"
                result += f"   Category: {page.get('category', 'N/A')}\n\n"
            
            return result
        except requests.exceptions.RequestException as e:
            return f"Error fetching pages: {str(e)}"


# Facebook Publishing Tool
class FacebookPublishInput(BaseModel):
    """Input schema for FacebookPublishTool."""
    message: str = Field(..., description="The post text content to publish")
    image_url: Optional[str] = Field(None, description="Optional URL to an image to attach to the post")


class FacebookPublishTool(BaseTool):
    name: str = "Facebook Publish Tool"
    description: str = "Publishes content (text and optional image) to a Facebook Page using the Graph API"
    args_schema: Type[BaseModel] = FacebookPublishInput

    def _run(self, message: str, image_url: Optional[str] = None) -> str:
        """Publish content to Facebook Page."""
        import time
        
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not page_access_token or not page_id:
            return "Error: Missing Facebook credentials in environment variables"
        
        # If image_url is provided, use photos endpoint
        if image_url:
            url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
            payload = {
                "url": image_url,
                "caption": message,
                "access_token": page_access_token
            }
        else:
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            payload = {
                "message": message,
                "access_token": page_access_token
            }
        
        # Retry logic with longer delays
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Use session with custom DNS resolver
                session = requests.Session()
                
                # Try with different timeout and retry settings
                response = session.post(
                    url, 
                    data=payload, 
                    timeout=60,
                    verify=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json'
                    }
                )
                response.raise_for_status()
                post_id = response.json().get("id") or response.json().get("post_id")
                post_link = f"https://facebook.com/{post_id}"
                return f"✅ Successfully published post!\nPost ID: {post_id}\nLink: {post_link}"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s, 20s, 25s
                    time.sleep(wait_time)
                    continue
                    
                error_msg = str(e)
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        error_msg = error_data.get('error', {}).get('message', error_msg)
                    except:
                        pass
                
                # Return a more helpful error message
                return f"❌ Error publishing to Facebook: {error_msg}\n\nNote: This may be a network restriction on Hugging Face Spaces. Consider using a webhook or external service to post to Facebook."


# Facebook Post Engagement Tool
class FacebookPostEngagementInput(BaseModel):
    """Input schema for FacebookPostEngagementTool."""
    limit: Optional[int] = Field(10, description="Number of recent posts to analyze")


class FacebookPostEngagementTool(BaseTool):
    name: str = "Facebook Post Engagement Tool"
    description: str = "Retrieves engagement metrics for recent posts (likes, comments, shares)"
    args_schema: Type[BaseModel] = FacebookPostEngagementInput

    def _run(self, limit: int = 10) -> str:
        """Retrieve engagement metrics for recent posts."""
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not page_access_token or not page_id:
            return "Error: Missing Facebook credentials"
        
        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        
        params = {
            "fields": "id,message,created_time,likes.summary(true),comments.summary(true),shares",
            "limit": limit,
            "access_token": page_access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("data", [])
            if not posts:
                return "No posts found"
            
            result = f"📊 Recent Post Engagement (Last {len(posts)} posts):\n\n"
            
            for i, post in enumerate(posts, 1):
                message = post.get("message", "No text")[:50] + "..."
                likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                shares = post.get("shares", {}).get("count", 0)
                created = post.get("created_time", "Unknown")
                
                result += f"{i}. Post: {message}\n"
                result += f"   👍 Likes: {likes} | 💬 Comments: {comments} | 🔄 Shares: {shares}\n"
                result += f"   📅 Posted: {created}\n\n"
            
            return result
        except requests.exceptions.RequestException as e:
            return f"Error fetching post engagement: {str(e)}"


# Facebook Page Insights Tool
class FacebookPageInsightsInput(BaseModel):
    """Input schema for FacebookPageInsightsTool."""
    period: Optional[str] = Field("day", description="Time period: day, week, or days_28")


class FacebookPageInsightsTool(BaseTool):
    name: str = "Facebook Page Insights Tool"
    description: str = "Retrieves page-level insights and performance metrics"
    args_schema: Type[BaseModel] = FacebookPageInsightsInput

    def _run(self, period: str = "day") -> str:
        """Retrieve page insights."""
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not page_access_token or not page_id:
            return "Error: Missing Facebook credentials"
        
        # Get page info first
        page_url = f"https://graph.facebook.com/v18.0/{page_id}"
        page_params = {
            "fields": "name,fan_count,followers_count,category",
            "access_token": page_access_token
        }
        
        try:
            page_response = requests.get(page_url, params=page_params)
            page_response.raise_for_status()
            page_data = page_response.json()
            
            result = f"📈 Facebook Page Insights\n\n"
            result += f"Page: {page_data.get('name', 'Unknown')}\n"
            result += f"Category: {page_data.get('category', 'N/A')}\n"
            result += f"👥 Fans: {page_data.get('fan_count', 'N/A')}\n"
            result += f"👥 Followers: {page_data.get('followers_count', 'N/A')}\n\n"
            
            # Get insights
            insights_url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
            insights_params = {
                "metric": "page_impressions,page_engaged_users,page_post_engagements,page_views_total",
                "period": period,
                "access_token": page_access_token
            }
            
            insights_response = requests.get(insights_url, params=insights_params)
            insights_response.raise_for_status()
            insights_data = insights_response.json()
            
            result += f"Metrics (Period: {period}):\n"
            for metric in insights_data.get("data", []):
                name = metric.get("name", "Unknown")
                values = metric.get("values", [])
                if values:
                    value = values[-1].get("value", "N/A")
                    result += f"  • {name}: {value}\n"
            
            return result
        except requests.exceptions.RequestException as e:
            return f"Error fetching insights: {str(e)}"


# Facebook User Content Tool
class FacebookUserContentInput(BaseModel):
    """Input schema for FacebookUserContentTool."""
    limit: Optional[int] = Field(5, description="Number of recent comments to retrieve")


class FacebookUserContentTool(BaseTool):
    name: str = "Facebook User Content Tool"
    description: str = "Retrieves user-generated content like comments on recent posts"
    args_schema: Type[BaseModel] = FacebookUserContentInput

    def _run(self, limit: int = 5) -> str:
        """Retrieve user comments on recent posts."""
        page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not page_access_token or not page_id:
            return "Error: Missing Facebook credentials"
        
        # Get recent posts first
        posts_url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        posts_params = {
            "fields": "id,message",
            "limit": 3,
            "access_token": page_access_token
        }
        
        try:
            posts_response = requests.get(posts_url, params=posts_params)
            posts_response.raise_for_status()
            posts_data = posts_response.json()
            
            posts = posts_data.get("data", [])
            if not posts:
                return "No posts found"
            
            result = "💬 Recent User Comments:\n\n"
            
            for post in posts[:2]:  # Check last 2 posts
                post_id = post.get("id")
                post_message = post.get("message", "No text")[:40] + "..."
                
                # Get comments for this post
                comments_url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
                comments_params = {
                    "fields": "from,message,created_time,like_count",
                    "limit": limit,
                    "access_token": page_access_token
                }
                
                comments_response = requests.get(comments_url, params=comments_params)
                comments_response.raise_for_status()
                comments_data = comments_response.json()
                
                comments = comments_data.get("data", [])
                if comments:
                    result += f"Post: {post_message}\n"
                    for comment in comments:
                        user = comment.get("from", {}).get("name", "Unknown")
                        message = comment.get("message", "")[:60]
                        likes = comment.get("like_count", 0)
                        result += f"  • {user}: {message}... (👍 {likes})\n"
                    result += "\n"
            
            return result if "Post:" in result else "No comments found on recent posts"
        except requests.exceptions.RequestException as e:
            return f"Error fetching user content: {str(e)}"


# Image Generation Tool
class ImageGenerationInput(BaseModel):
    """Input schema for ImageGenerationTool."""
    prompt: str = Field(..., description="Description of the image to generate")
    style: Optional[str] = Field("realistic", description="Style of the image (realistic, anime, oil_painting, etc.)")


class ImageGenerationTool(BaseTool):
    name: str = "Image Generation Tool"
    description: str = "Generates images using Pollinations.ai API based on text prompts"
    args_schema: Type[BaseModel] = ImageGenerationInput

    def _run(self, prompt: str, style: str = "realistic") -> str:
        """Generate an image using Pollinations.ai."""
        try:
            # Pollinations.ai free API endpoint
            # Clean and encode the prompt
            clean_prompt = prompt.strip()
            encoded_prompt = clean_prompt.replace(" ", "%20")
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            # Add style parameter if provided
            if style and style != "realistic":
                url += f"?style={style}"
            
            # Return URL in a clear format for the agent to extract
            return f"IMAGE_URL: {url}"
        except Exception as e:
            return f"Error generating image: {str(e)}"


# Trend Search Tool
class TrendSearchInput(BaseModel):
    """Input schema for TrendSearchTool."""
    query: str = Field(..., description="Search query for trends")
    limit: Optional[int] = Field(5, description="Number of results to return")


class TrendSearchTool(BaseTool):
    name: str = "Trend Search Tool"
    description: str = "Searches for current trends and news related to a topic"
    args_schema: Type[BaseModel] = TrendSearchInput

    def _run(self, query: str, limit: int = 5) -> str:
        """Search for trends."""
        # This is a simplified version - in production, integrate with NewsAPI or similar
        return f"""Trend Search Results for '{query}':

1. AI and Automation in {query}
   - Growing interest in AI-powered solutions
   - High engagement potential with tech-savvy audiences

2. Sustainability and {query}
   - Eco-friendly practices gaining traction
   - Appeals to environmentally conscious consumers

3. Community-driven {query}
   - User-generated content performing well
   - Authentic stories resonate with audiences

4. Educational content about {query}
   - How-to guides and tutorials trending
   - Value-driven content gets high shares

5. Behind-the-scenes {query}
   - Transparency and authenticity valued
   - Personal stories create emotional connections

Note: For production use, integrate with a real news/trends API like NewsAPI, Google Trends API, or social listening tools."""


# Web Scraping Tool
class WebScrapeInput(BaseModel):
    """Input schema for WebScrapeTool."""
    url: str = Field(..., description="Website URL to scrape")


class WebScrapeTool(BaseTool):
    name: str = "Web Scrape Tool"
    description: str = "Scrapes content from a website for research purposes"
    args_schema: Type[BaseModel] = WebScrapeInput

    def _run(self, url: str) -> str:
        """Scrape website content."""
        try:
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            return text[:2000]  # Return first 2000 chars
        except Exception as e:
            return f"Error scraping website: {str(e)}"
