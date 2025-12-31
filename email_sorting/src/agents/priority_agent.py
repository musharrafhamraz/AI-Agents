"""Priority Scorer Agent - Determines email urgency and importance"""

import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import EmailState
from ..config import PRIORITY_PROMPT
from ..utils import create_json_llm


class PriorityAgent:
    """Agent that scores email priority and urgency"""
    
    def __init__(self):
        self.llm = create_json_llm()
    
    def score_priority(self, state: EmailState) -> Dict[str, Any]:
        """
        Score email priority from 0-10.
        
        Args:
            state: Current email state
        
        Returns:
            Updated state dict with priority scores
        """
        try:
            sender_history = self._format_sender_history(state.get("sender_history"))
            
            result = self._llm_score(
                sender=state["sender"],
                subject=state["subject"],
                body=state["body"],
                sender_history=sender_history
            )
            
            return {
                "priority_score": result["priority_score"],
                "urgency_level": result["urgency_level"],
                "recommended_response_time": result["recommended_response_time"],
                "priority_reasoning": result["reasoning"]
            }
            
        except Exception as e:
            return {
                "error": f"Priority scoring failed: {str(e)}"
            }
    
    def _llm_score(
        self,
        sender: str,
        subject: str,
        body: str,
        sender_history: str
    ) -> Dict[str, Any]:
        """Use LLM to score priority"""
        
        prompt = PRIORITY_PROMPT.format(
            sender=sender,
            subject=subject,
            body=body[:1000],
            sender_history=sender_history
        )
        
        messages = [
            SystemMessage(content="You are an expert at determining email priority. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return json.loads(response.content)
    
    def _format_sender_history(self, sender_history: dict) -> str:
        """Format sender history for context"""
        if not sender_history:
            return "No previous history with this sender."
        
        return (
            f"Average priority: {sender_history.get('avg_priority', 5.0):.1f}/10, "
            f"VIP: {sender_history.get('is_vip', False)}, "
            f"Response rate: {sender_history.get('response_rate', 0):.0%}"
        )


# Node function for LangGraph
def priority_scorer_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for priority scoring"""
    agent = PriorityAgent()
    return agent.score_priority(state)
