"""Graph package - LangGraph workflow components"""

from .workflow import create_email_sorting_workflow
from .state import EmailState, AgentOutput

__all__ = [
    "create_email_sorting_workflow",
    "EmailState",
    "AgentOutput",
]
