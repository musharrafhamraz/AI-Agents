"""Main LangGraph workflow for email sorting"""

from typing import Literal
from langgraph.graph import StateGraph, END

from .state import EmailState
from ..agents.email_parser import email_parser_node
from ..agents.classifier_agent import classifier_node
from ..agents.priority_agent import priority_scorer_node
from ..agents.intent_agent import intent_detector_node
from ..agents.router_agent import router_node
from ..agents.executor_agent import executor_node
from ..config import settings


def create_email_sorting_workflow(checkpointer=None):
    """
    Create the main LangGraph workflow for email sorting.
    
    Args:
        checkpointer: Optional checkpointer for persistence
        
    Returns:
        Compiled LangGraph workflow
    """
    
    # Initialize graph with state schema
    workflow = StateGraph(EmailState)
    
    # Add nodes for each agent
    workflow.add_node("parse", email_parser_node)
    workflow.add_node("classify", classifier_node)
    workflow.add_node("score_priority", priority_scorer_node)
    workflow.add_node("detect_intent", intent_detector_node)
    workflow.add_node("aggregate", aggregate_results_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("route", router_node)
    workflow.add_node("execute", executor_node)
    workflow.add_node("finalize", finalize_node)
    
    # Define workflow edges
    workflow.set_entry_point("parse")
    
    # After parsing, run classification, priority, and intent in parallel
    workflow.add_edge("parse", "classify")
    workflow.add_edge("parse", "score_priority")
    workflow.add_edge("parse", "detect_intent")
    
    # All three converge to aggregator
    workflow.add_edge("classify", "aggregate")
    workflow.add_edge("score_priority", "aggregate")
    workflow.add_edge("detect_intent", "aggregate")
    
    # Conditional routing based on confidence
    workflow.add_conditional_edges(
        "aggregate",
        should_review_human,
        {
            "review": "human_review",
            "proceed": "route"
        }
    )
    
    # Both paths lead to router
    workflow.add_edge("human_review", "route")
    workflow.add_edge("route", "execute")
    workflow.add_edge("execute", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile(checkpointer=checkpointer)


def aggregate_results_node(state: EmailState) -> dict:
    """
    Aggregate results from parallel agents and calculate overall confidence.
    
    Args:
        state: Current state with results from classifier, priority, intent agents
    
    Returns:
        Updated state with aggregated confidence
    """
    # Calculate overall confidence as average of available confidences
    confidences = []
    
    if state.get("classification_confidence"):
        confidences.append(state["classification_confidence"])
    if state.get("intent_confidence"):
        confidences.append(state["intent_confidence"])
    
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    
    # Determine if human review is needed
    requires_review = overall_confidence < settings.CONFIDENCE_THRESHOLD
    
    return {
        "overall_confidence": overall_confidence,
        "requires_human_review": requires_review,
        "processing_stage": "aggregated"
    }


def should_review_human(state: EmailState) -> Literal["review", "proceed"]:
    """
    Conditional edge function to determine if human review is needed.
    
    Args:
        state: Current state
    
    Returns:
        "review" if human review needed, "proceed" otherwise
    """
    if not settings.ENABLE_HUMAN_REVIEW:
        return "proceed"
    
    if state.get("requires_human_review", False):
        return "review"
    
    return "proceed"


def human_review_node(state: EmailState) -> dict:
    """
    Pause workflow for human review on uncertain classifications.
    
    Args:
        state: Current state
    
    Returns:
        Updated state with human feedback
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    
    console = Console()
    
    # Display email summary
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold yellow]Low Confidence Classification - Please Review[/bold yellow]\n\n"
        f"[cyan]From:[/cyan] {state['sender']}\n"
        f"[cyan]Subject:[/cyan] {state['subject']}\n"
        f"[cyan]Body Preview:[/cyan] {state['body'][:200]}...\n\n"
        f"[green]AI Suggestion:[/green]\n"
        f"  Category: {state.get('classification', 'Unknown')}\n"
        f"  Priority: {(state.get('priority_score') or 0):.1f}/10\n"
        f"  Intent: {state.get('intent', 'Unknown')}\n"
        f"  Confidence: {(state.get('overall_confidence') or 0):.0%}",
        title="Email Review Required"
    ))
    
    # Ask user
    accept = Confirm.ask("Accept AI classification?", default=True)
    
    if not accept:
        # Get correct classification
        console.print(f"\nAvailable categories: {', '.join(settings.CATEGORIES)}")
        correct_category = Prompt.ask("Enter correct category")
        
        return {
            "classification": correct_category,
            "classification_confidence": 1.0,
            "overall_confidence": 1.0,
            "requires_human_review": False,
            "processing_stage": "human_corrected"
        }
    
    return {
        "requires_human_review": False,
        "processing_stage": "human_approved"
    }


def finalize_node(state: EmailState) -> dict:
    """
    Finalize processing and prepare for execution.
    
    Args:
        state: Current state
    
    Returns:
        Updated state with final status
    """
    from datetime import datetime
    
    return {
        "processing_stage": "ready_for_execution",
        "processed_at": datetime.now().isoformat()
    }
