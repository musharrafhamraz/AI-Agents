"""Custom tools for LinkedIn automation."""
from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import os
import time


# LinkedIn Publishing Tool
class LinkedInPublishInput(BaseModel):
    """Input schema for LinkedInPublishTool."""
    text: str = Field(..., description="The post text content to publish")
    image_url: Optional[str] = Field(None, description="Optional URL to an image to attach to the post")


class LinkedInPublishTool(BaseTool):
    name: str = "LinkedIn Publish Tool"
    description: str = "Publishes content (text and optional image) to LinkedIn profile or organization page"
    args_schema: Type[BaseModel] = LinkedInPublishInput

    def _register_upload(self, access_token: str, author_urn: str) -> Optional[dict]:
        """Register an upload with LinkedIn to get upload URL."""
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error registering upload: {str(e)}")
            return None

    def _upload_image(self, upload_url: str, image_data: bytes, access_token: str) -> bool:
        """Upload image binary data to LinkedIn."""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.put(upload_url, headers=headers, data=image_data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return False

    def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL."""
        try:
            # Add timeout and retry logic for Pollinations.ai
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    return response.content
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    raise
            return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    def _run(self, text: str, image_url: Optional[str] = None) -> str:
        """Publish content to LinkedIn."""
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        author_urn = os.getenv("LINKEDIN_PERSON_URN") or os.getenv("LINKEDIN_ORGANIZATION_URN")
        
        if not access_token or not author_urn:
            return "Error: Missing LinkedIn credentials in environment variables"
        
        # Handle image upload if provided
        asset_urn = None
        if image_url:
            try:
                # Step 1: Download image
                print("Downloading image...")
                image_data = self._download_image(image_url)
                if not image_data:
                    return "Error: Failed to download image from URL"
                
                # Step 2: Register upload
                print("Registering upload with LinkedIn...")
                upload_response = self._register_upload(access_token, author_urn)
                if not upload_response:
                    return "Error: Failed to register upload with LinkedIn"
                
                upload_url = upload_response.get("value", {}).get("uploadMechanism", {}).get(
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
                ).get("uploadUrl")
                
                asset_urn = upload_response.get("value", {}).get("asset")
                
                if not upload_url or not asset_urn:
                    return "Error: Invalid upload response from LinkedIn"
                
                # Step 3: Upload image
                print("Uploading image to LinkedIn...")
                if not self._upload_image(upload_url, image_data, access_token):
                    return "Error: Failed to upload image to LinkedIn"
                
                print("Image uploaded successfully!")
                
            except Exception as e:
                return f"Error processing image: {str(e)}"
        
        # Build the post payload
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add image if uploaded
        if asset_urn:
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "description": {
                        "text": "Post image"
                    },
                    "media": asset_urn,
                    "title": {
                        "text": "Image"
                    }
                }
            ]
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            post_data = response.json()
            post_id = post_data.get("id", "Unknown")
            
            image_note = " with image" if asset_urn else ""
            return f"✅ Successfully published to LinkedIn{image_note}!\nPost ID: {post_id}"
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"{error_data.get('message', error_msg)} - {error_data.get('serviceErrorCode', '')}"
                except:
                    error_msg = e.response.text if e.response.text else error_msg
            return f"❌ Error publishing to LinkedIn: {error_msg}"


# LinkedIn Analytics Tool
class LinkedInAnalyticsInput(BaseModel):
    """Input schema for LinkedInAnalyticsTool."""
    pass


class LinkedInAnalyticsTool(BaseTool):
    name: str = "LinkedIn Analytics Tool"
    description: str = "Retrieves analytics and performance metrics for LinkedIn profile or organization"
    args_schema: Type[BaseModel] = LinkedInAnalyticsInput

    def _run(self) -> str:
        """Retrieve LinkedIn analytics."""
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        person_urn = os.getenv("LINKEDIN_PERSON_URN")
        org_urn = os.getenv("LINKEDIN_ORGANIZATION_URN")
        
        if not access_token:
            return "Error: Missing LinkedIn access token"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        result = "📈 LinkedIn Analytics\n\n"
        
        # Get profile info
        try:
            if person_urn:
                profile_url = "https://api.linkedin.com/v2/me"
                profile_response = requests.get(profile_url, headers=headers)
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                first_name = profile_data.get("localizedFirstName", "")
                last_name = profile_data.get("localizedLastName", "")
                result += f"Profile: {first_name} {last_name}\n"
                result += f"ID: {profile_data.get('id', 'N/A')}\n\n"
            
            elif org_urn:
                org_id = org_urn.split(":")[-1]
                org_url = f"https://api.linkedin.com/v2/organizations/{org_id}"
                org_response = requests.get(org_url, headers=headers)
                org_response.raise_for_status()
                org_data = org_response.json()
                
                org_name = org_data.get("localizedName", "Unknown")
                result += f"Organization: {org_name}\n"
                result += f"ID: {org_id}\n\n"
            
            result += "Note: Detailed analytics require additional API permissions.\n"
            result += "For full analytics, use LinkedIn's native analytics dashboard."
            
            return result
        except requests.exceptions.RequestException as e:
            return f"Error fetching analytics: {str(e)}"


# LinkedIn Engagement Tool
class LinkedInEngagementInput(BaseModel):
    """Input schema for LinkedInEngagementTool."""
    limit: Optional[int] = Field(5, description="Number of recent posts to analyze")


class LinkedInEngagementTool(BaseTool):
    name: str = "LinkedIn Engagement Tool"
    description: str = "Retrieves engagement metrics for recent LinkedIn posts"
    args_schema: Type[BaseModel] = LinkedInEngagementInput

    def _run(self, limit: int = 5) -> str:
        """Retrieve engagement metrics for recent posts."""
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        author_urn = os.getenv("LINKEDIN_PERSON_URN") or os.getenv("LINKEDIN_ORGANIZATION_URN")
        
        if not access_token or not author_urn:
            return "Error: Missing LinkedIn credentials"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Get recent posts
        url = f"https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List({author_urn})&count={limit}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("elements", [])
            if not posts:
                return "No posts found"
            
            result = f"📊 Recent Post Engagement (Last {len(posts)} posts):\n\n"
            
            for i, post in enumerate(posts, 1):
                post_id = post.get("id", "Unknown")
                text = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text", "No text")
                text_preview = text[:60] + "..." if len(text) > 60 else text
                
                # Note: Detailed engagement metrics require additional API calls
                result += f"{i}. Post ID: {post_id}\n"
                result += f"   Text: {text_preview}\n"
                result += f"   Status: {post.get('lifecycleState', 'Unknown')}\n\n"
            
            result += "Note: Detailed engagement metrics (likes, comments, shares) require additional API permissions."
            
            return result
        except requests.exceptions.RequestException as e:
            return f"Error fetching engagement: {str(e)}"


# Image Generation Tool (Professional Style)
class ImageGenerationInput(BaseModel):
    """Input schema for ImageGenerationTool."""
    prompt: str = Field(..., description="Description of the image to generate")
    style: Optional[str] = Field("professional", description="Style of the image")


class ImageGenerationTool(BaseTool):
    name: str = "Image Generation Tool"
    description: str = "Generates professional images using Pollinations.ai API based on text prompts"
    args_schema: Type[BaseModel] = ImageGenerationInput

    def _run(self, prompt: str, style: str = "professional") -> str:
        """Generate a professional image using Pollinations.ai."""
        try:
            # Add professional context to prompt
            professional_prompt = f"professional corporate business {prompt} clean modern design"
            
            # Clean and encode the prompt
            clean_prompt = professional_prompt.strip()
            encoded_prompt = clean_prompt.replace(" ", "%20")
            
            # Pollinations.ai free API endpoint with dimensions for LinkedIn
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=627"
            
            # Return URL in a clear format for the agent to extract
            return f"IMAGE_URL: {url}"
        except Exception as e:
            return f"Error generating image: {str(e)}"
