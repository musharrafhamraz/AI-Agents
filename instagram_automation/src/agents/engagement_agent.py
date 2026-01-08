"""Engagement Agent - Handles comments and interactions."""
from typing import Dict, Any, List
from src.tools import instagram_api, gemini_llm
from src.graph.state import EngagementState
from loguru import logger


async def engagement_agent_node(state: EngagementState) -> Dict[str, Any]:
    """Engagement agent node.
    
    Processes comments and generates replies using Google Gemini.
    
    Args:
        state: Current engagement state
        
    Returns:
        Updated state with processed comments
    """
    logger.info("Engagement Agent: Starting comment processing")
    
    try:
        comments_to_process = state.get("comments_to_process", [])
        processed_comments = []
        flagged_for_review = []
        
        brand_voice = state.get("brand_voice", "professional and friendly")
        post_caption = state.get("post_caption", "")
        
        for comment in comments_to_process:
            comment_text = comment.get("text", "")
            comment_id = comment.get("id", "")
            
            logger.info(f"Processing comment: {comment_id}")
            
            # Generate reply using Gemini
            reply_result = await gemini_llm.generate_comment_reply(
                comment_text=comment_text,
                post_caption=post_caption,
                brand_voice=brand_voice
            )
            
            reply_text = reply_result.get("reply", "")
            should_flag = reply_result.get("should_flag", False)
            
            if should_flag:
                logger.info(f"Comment flagged for review: {comment_id}")
                flagged_for_review.append({
                    **comment,
                    "suggested_reply": reply_text,
                    "flag_reason": reply_result.get("flag_reason", "Unknown")
                })
            else:
                # Post reply if auto-reply is enabled
                auto_reply = state.get("auto_reply", False)
                if auto_reply:
                    try:
                        reply_id = await instagram_api.reply_to_comment(
                            comment_id, reply_text
                        )
                        processed_comments.append({
                            **comment,
                            "reply_id": reply_id,
                            "reply_text": reply_text,
                            "status": "replied"
                        })
                        logger.info(f"Posted reply to comment: {comment_id}")
                    except Exception as e:
                        logger.error(f"Error posting reply: {e}")
                        flagged_for_review.append({
                            **comment,
                            "suggested_reply": reply_text,
                            "flag_reason": f"Error posting reply: {str(e)}"
                        })
                else:
                    processed_comments.append({
                        **comment,
                        "suggested_reply": reply_text,
                        "status": "pending_approval"
                    })
        
        logger.info(f"Engagement Agent: Processed {len(processed_comments)} comments, "
                   f"flagged {len(flagged_for_review)} for review")
        
        return {
            "processed_comments": processed_comments,
            "flagged_for_review": flagged_for_review,
            "current_step": "completed",
            "messages": [{
                "role": "assistant",
                "content": f"Processed {len(comments_to_process)} comments"
            }]
        }
        
    except Exception as e:
        error_msg = f"Engagement Agent error: {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": "error",
            "errors": [error_msg],
            "messages": [{
                "role": "assistant",
                "content": error_msg
            }]
        }


class EngagementAgent:
    """Engagement Agent class."""
    
    def __init__(self):
        """Initialize Engagement Agent."""
        self.name = "engagement_agent"
        logger.info("Initialized Engagement Agent")
    
    async def process_comments(
        self,
        media_id: str,
        brand_voice: str,
        post_caption: str,
        auto_reply: bool = False
    ) -> Dict[str, Any]:
        """Process comments on a post.
        
        Args:
            media_id: Instagram media ID
            brand_voice: Brand voice description
            post_caption: Original post caption
            auto_reply: Whether to auto-reply or queue for review
            
        Returns:
            Dictionary with processed comments and flagged items
        """
        # Fetch comments from Instagram
        comments = await instagram_api.get_comments(media_id)
        
        state: EngagementState = {
            "comments_to_process": comments,
            "dms_to_process": [],
            "current_comment": None,
            "generated_reply": None,
            "sentiment": None,
            "processed_comments": [],
            "flagged_for_review": [],
            "current_step": "init",
            "errors": [],
            "messages": [],
            "brand_voice": brand_voice,
            "post_caption": post_caption,
            "auto_reply": auto_reply
        }
        
        result = await engagement_agent_node(state)
        return result
