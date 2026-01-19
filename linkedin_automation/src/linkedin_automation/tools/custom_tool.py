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
            # Strip "IMAGE_URL: " prefix if present
            if image_url.startswith("IMAGE_URL:"):
                image_url = image_url.replace("IMAGE_URL:", "").strip()
            
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
        person_urn = os.getenv("LINKEDIN_PERSON_URN")
        org_urn = os.getenv("LINKEDIN_ORGANIZATION_URN")
        
        # Determine author URN - person takes precedence
        if person_urn:
            author_urn = person_urn
            author_type = "person"
        elif org_urn:
            author_urn = org_urn
            author_type = "organization"
        else:
            return "Error: Missing LinkedIn URN (LINKEDIN_PERSON_URN or LINKEDIN_ORGANIZATION_URN) in environment variables"
        
        if not access_token:
            return "Error: Missing LinkedIn access token in environment variables"
        
        print(f"Publishing to {author_type}: {author_urn}")
        
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
                    error_msg = f"{error_data.get('message', error_msg)}"
                    service_error = error_data.get('serviceErrorCode', '')
                    if service_error:
                        error_msg += f" (Error Code: {service_error})"
                    
                    # Provide specific guidance for common errors
                    if e.response.status_code == 403:
                        if author_type == "organization":
                            error_msg += "\n\n⚠️ TROUBLESHOOTING FOR ORGANIZATION POSTS:"
                            error_msg += "\n1. Make sure your access token has 'w_organization_social' scope"
                            error_msg += "\n2. Verify you are an ADMIN of the organization page"
                            error_msg += "\n3. Regenerate your token using: python manual_auth.py"
                            error_msg += f"\n4. Verify organization URN is correct: {author_urn}"
                        else:
                            error_msg += "\n\n⚠️ Token may not have 'w_member_social' permission"
                    elif e.response.status_code == 400 and "author" in error_msg.lower():
                        error_msg += "\n\n⚠️ AUTHOR FIELD ERROR:"
                        error_msg += f"\n1. Check if URN format is correct: {author_urn}"
                        if author_type == "organization":
                            error_msg += "\n2. Verify you have admin access to this organization"
                            error_msg += "\n3. Token must have 'w_organization_social' scope"
                            error_msg += "\n4. Run: python manual_auth.py to get a new token"
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
    style: Optional[str] = Field("infographic", description="Style of the image (infographic, professional, corporate)")


class ImageGenerationTool(BaseTool):
    name: str = "Image Generation Tool"
    description: str = "Generates professional infographics and images using Gemini API (primary) or Pollinations.ai (fallback) based on text prompts"
    args_schema: Type[BaseModel] = ImageGenerationInput

    def _clean_prompt(self, prompt: str) -> str:
        """Clean prompt text for URL encoding."""
        # Remove special characters that break URLs
        cleaned = prompt.replace("#", "").replace("&", "and").replace("%", "percent")
        # Normalize whitespace
        cleaned = " ".join(cleaned.split())
        return cleaned

    def _get_infographic_type_keywords(self, prompt: str) -> str:
        """Extract infographic type-specific keywords from prompt."""
        prompt_lower = prompt.lower()
        
        # Detect infographic type from prompt content
        if any(word in prompt_lower for word in ['timeline', 'chronological', 'history', 'evolution', 'over time']):
            return "timeline chronological events milestones sequential progression"
        elif any(word in prompt_lower for word in ['comparison', 'versus', 'vs', 'compare', 'difference']):
            return "side-by-side comparison contrast two columns versus"
        elif any(word in prompt_lower for word in ['process', 'steps', 'workflow', 'how to', 'procedure']):
            return "sequential steps process workflow numbered stages"
        else:
            # Default to statistical
            return "statistics data points key metrics numbers percentages"

    def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate image using Google Gemini API."""
        try:
            import google.generativeai as genai
            
            # Get API key and model from environment
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL_NAME", "imagen-3.0-generate-001")
            
            if not api_key:
                print("⚠️ GEMINI_API_KEY not found in environment variables")
                return None
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            print(f"🎨 Attempting to generate image with Gemini ({model_name})...")
            
            # Generate image using Gemini
            model = genai.ImageGenerationModel(model_name)
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9",  # LinkedIn optimal ratio
                safety_filter_level="block_only_high",
                person_generation="allow_adult"
            )
            
            if result.images and len(result.images) > 0:
                # Save image temporarily and upload to a hosting service
                # For now, we'll use the image data URL directly
                image = result.images[0]
                
                # Convert PIL Image to bytes
                import io
                from PIL import Image
                img_byte_arr = io.BytesIO()
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                
                image.save(img_byte_arr, format='JPEG', quality=95)
                img_byte_arr.seek(0)
                
                # Upload to temporary hosting (using imgbb or similar)
                # For now, return a base64 data URL
                import base64
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
                
                # Note: LinkedIn API requires a publicly accessible URL
                # We need to upload this to a temporary hosting service
                print("✅ Image generated with Gemini successfully!")
                print("⚠️ Note: Image needs to be uploaded to public hosting for LinkedIn")
                
                # Try to upload to imgbb if API key is available
                imgbb_key = os.getenv("IMGBB_API_KEY")
                if imgbb_key:
                    upload_url = self._upload_to_imgbb(img_base64, imgbb_key)
                    if upload_url:
                        return upload_url
                
                # If imgbb upload fails, return base64 (won't work with LinkedIn but better than nothing)
                return f"data:image/jpeg;base64,{img_base64}"
            
            print("⚠️ Gemini returned no images")
            return None
            
        except ImportError:
            print("⚠️ google-generativeai package not installed. Install with: pip install google-generativeai")
            return None
        except Exception as e:
            print(f"⚠️ Gemini generation failed: {str(e)}")
            return None

    def _upload_to_imgbb(self, img_base64: str, api_key: str) -> Optional[str]:
        """Upload base64 image to imgbb for public hosting."""
        try:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": api_key,
                "image": img_base64,
                "expiration": 600  # 10 minutes expiration
            }
            
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                image_url = data.get("data", {}).get("url")
                print(f"✅ Image uploaded to imgbb: {image_url}")
                return image_url
            
            return None
        except Exception as e:
            print(f"⚠️ Failed to upload to imgbb: {str(e)}")
            return None

    def _generate_with_pollinations(self, prompt: str) -> str:
        """Generate image using Pollinations.ai as fallback."""
        try:
            print("🎨 Falling back to Pollinations.ai...")
            
            # Clean and encode the prompt
            clean_prompt = self._clean_prompt(prompt)
            
            # Use urllib.parse for proper URL encoding
            import urllib.parse
            encoded_prompt = urllib.parse.quote(clean_prompt)
            
            # Pollinations.ai free API endpoint with dimensions for LinkedIn
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=627&nologo=true"
            
            print(f"✅ Pollinations.ai URL generated: {url}")
            return url
            
        except Exception as e:
            raise Exception(f"Pollinations.ai generation failed: {str(e)}")

    def _run(self, prompt: str, style: str = "infographic") -> str:
        """Generate a professional infographic or image using Gemini (primary) or Pollinations.ai (fallback)."""
        try:
            # Construct infographic-specific prompt
            if style == "infographic" or "infographic" in prompt.lower():
                # Get type-specific keywords
                type_keywords = self._get_infographic_type_keywords(prompt)
                
                # Quality and readability specifications
                quality_specs = (
                    "high contrast clean uncluttered white space "
                    "professional blue gray colors readable text "
                    "bold headers clear visual hierarchy organized sections"
                )
                
                # Infographic-specific keywords and layout
                enhanced_prompt = (
                    f"professional infographic data visualization {prompt} "
                    f"{type_keywords} "
                    f"clean modern layout bold typography "
                    f"business style white background "
                    f"{quality_specs}"
                )
            elif style == "corporate":
                enhanced_prompt = f"professional corporate business {prompt} clean modern design"
            else:
                enhanced_prompt = (
                    f"professional {style} {prompt} "
                    f"clean modern design high contrast organized layout"
                )
            
            # Try Gemini first
            print("=" * 60)
            print("🚀 Starting image generation process...")
            print(f"📝 Prompt: {enhanced_prompt[:100]}...")
            print("=" * 60)
            
            gemini_url = self._generate_with_gemini(enhanced_prompt)
            
            if gemini_url:
                # Check if it's a valid URL (not base64)
                if gemini_url.startswith("http"):
                    return f"IMAGE_URL: {gemini_url}"
                else:
                    print("⚠️ Gemini returned base64 data, not a public URL. Falling back to Pollinations...")
            
            # Fallback to Pollinations
            print("-" * 60)
            print("🔄 Switching to Pollinations.ai fallback...")
            print("-" * 60)
            
            pollinations_url = self._generate_with_pollinations(enhanced_prompt)
            return f"IMAGE_URL: {pollinations_url}"
            
        except Exception as e:
            error_msg = f"❌ Error generating image: {str(e)}"
            fallback_msg = "Consider using a generic image or posting text-only."
            return f"{error_msg}\n{fallback_msg}"
