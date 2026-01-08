"""Supervisor Agent - Orchestrates workflow between specialized agents."""
from typing import Dict, Any, Literal
from src.graph.state import InstagramState
from loguru import logger


def route_supervisor(state: InstagramState) -> str:
    """Route to appropriate agent based on current task.
    
    Args:
        state: Current Instagram state
        
    Returns:
        Next agent to execute
    """
    next_action = state.get("next_action", "")
    
    logger.info(f"Supervisor routing to: {next_action}")
    
    if next_action == "create_content":
        return "content_creator"
    elif next_action == "generate_image":
        return "image_generator"
    elif next_action == "publish_post":
        return "posting_agent"
    elif next_action == "handle_engagement":
        return "engagement_agent"
    elif next_action == "analyze_performance":
        return "analytics_agent"
    else:
        return "end"


async def supervisor_node(state: InstagramState) -> Dict[str, Any]:
    """Supervisor agent node.
    
    Determines the next action based on current state.
    
    Args:
        state: Current Instagram state
        
    Returns:
        Updated state with next action
    """
    logger.info("Supervisor Agent: Analyzing current state")
    
    try:
        task_description = state.get("task_description", "")
        current_post = state.get("current_post")
        
        # Determine next action based on task and current state
        if "create" in task_description.lower() or "generate" in task_description.lower():
            if not current_post or not current_post.get("caption"):
                next_action = "create_content"
            elif not current_post.get("image_url"):
                next_action = "generate_image"
            elif not current_post.get("instagram_media_id"):
                next_action = "publish_post"
            else:
                next_action = "end"
        elif "engagement" in task_description.lower() or "comment" in task_description.lower():
            next_action = "handle_engagement"
        elif "analytics" in task_description.lower() or "performance" in task_description.lower():
            next_action = "analyze_performance"
        else:
            next_action = "end"
        
        logger.info(f"Supervisor Agent: Next action determined: {next_action}")
        
        return {
            "next_action": next_action,
            "current_agent": "supervisor",
            "messages": [{
                "role": "assistant",
                "content": f"Routing to: {next_action}"
            }]
        }
        
    except Exception as e:
        error_msg = f"Supervisor Agent error: {str(e)}"
        logger.error(error_msg)
        return {
            "next_action": "end",
            "errors": [error_msg],
            "messages": [{
                "role": "assistant",
                "content": error_msg
            }]
        }


class SupervisorAgent:
    """Supervisor Agent class."""
    
    def __init__(self):
        """Initialize Supervisor Agent."""
        self.name = "supervisor"
        logger.info("Initialized Supervisor Agent")
    
    def route(self, state: InstagramState) -> str:
        """Route to next agent.
        
        Args:
            state: Current state
            
        Returns:
            Next agent name
        """
        return route_supervisor(state)
