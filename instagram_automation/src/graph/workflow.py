"""LangGraph workflow definitions."""
from langgraph.graph import StateGraph, END
from src.graph.state import InstagramState, ContentCreationState
from src.agents import (
    supervisor_node,
    route_supervisor,
    content_creator_node,
    image_generator_node,
    posting_agent_node,
    engagement_agent_node
)
from loguru import logger


def create_content_creation_workflow() -> StateGraph:
    """Create content creation workflow.
    
    This workflow handles the complete content creation pipeline:
    1. Generate caption and hashtags
    2. Generate image
    3. Publish to Instagram (with optional review)
    
    Returns:
        Compiled StateGraph workflow
    """
    workflow = StateGraph(ContentCreationState)
    
    # Add nodes
    workflow.add_node("content_creator", content_creator_node)
    workflow.add_node("image_generator", image_generator_node)
    workflow.add_node("posting", posting_agent_node)
    
    # Define edges
    workflow.set_entry_point("content_creator")
    workflow.add_edge("content_creator", "image_generator")
    
    # Conditional edge based on review requirement
    def should_publish(state: ContentCreationState) -> str:
        if state.get("requires_review", False) and not state.get("approved", False):
            return "end"
        return "posting"
    
    workflow.add_conditional_edges(
        "image_generator",
        should_publish,
        {
            "posting": "posting",
            "end": END
        }
    )
    
    workflow.add_edge("posting", END)
    
    logger.info("Created content creation workflow")
    return workflow.compile()


def create_instagram_workflow() -> StateGraph:
    """Create main Instagram automation workflow.
    
    This workflow uses a supervisor agent to route between specialized agents.
    
    Returns:
        Compiled StateGraph workflow
    """
    workflow = StateGraph(InstagramState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("content_creator", content_creator_node)
    workflow.add_node("image_generator", image_generator_node)
    workflow.add_node("posting_agent", posting_agent_node)
    workflow.add_node("engagement_agent", engagement_agent_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "content_creator": "content_creator",
            "image_generator": "image_generator",
            "posting_agent": "posting_agent",
            "engagement_agent": "engagement_agent",
            "end": END
        }
    )
    
    # All agents return to supervisor
    workflow.add_edge("content_creator", "supervisor")
    workflow.add_edge("image_generator", "supervisor")
    workflow.add_edge("posting_agent", "supervisor")
    workflow.add_edge("engagement_agent", "supervisor")
    
    logger.info("Created Instagram automation workflow")
    return workflow.compile()


# Create workflow instances
content_workflow = create_content_creation_workflow()
instagram_workflow = create_instagram_workflow()
