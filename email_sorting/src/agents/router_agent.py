"""Action Router Agent - Decides what actions to take on emails"""

import json
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import EmailState
from ..config import ROUTER_PROMPT
from ..utils import create_json_llm


class RouterAgent:
    """Agent that decides email actions based on classification"""
    
    def __init__(self):
        self.llm = create_json_llm()
    
    def route(self, state: EmailState) -> Dict[str, Any]:
        """
        Decide what actions to take on the email.
        
        Args:
            state: Current email state with classification, priority, intent
        
        Returns:
            Updated state dict with actions to execute
        """
        try:
            # First apply rule-based routing
            rule_actions = self._apply_rules(state)
            
            # Then get LLM suggestions
            llm_result = self._llm_route(state)
            llm_actions = llm_result.get("actions", [])
            
            # Combine actions (rules take precedence)
            all_actions = rule_actions + llm_actions
            
            # Extract labels from actions
            labels = self._extract_labels(all_actions)
            
            return {
                "actions": all_actions,
                "labels": labels,
                "processing_stage": "routed",
                "error": None
            }
            
        except Exception as e:
            return {
                "processing_stage": "routing_error",
                "error": f"Routing failed: {str(e)}"
            }
    
    def _apply_rules(self, state: EmailState) -> List[str]:
        """Apply rule-based routing logic"""
        actions = []
        
        classification = state.get("classification", "")
        priority_score = state.get("priority_score", 0)
        intent = state.get("intent", "")
        
        # Spam handling
        if classification == "Spam":
            actions.append("move_to_spam")
            return actions  # Don't process further
        
        # Promotions handling
        if classification == "Promotions":
            actions.append("apply_label:promotions")
            actions.append("archive")
        
        # High priority emails
        if priority_score and priority_score >= 8:
            actions.append("mark_important")
            actions.append("apply_label:urgent")
        
        # Action required
        if intent == "REQUEST_ACTION":
            actions.append("apply_label:action_required")
        
        # Follow-up
        if intent == "FOLLOW_UP":
            actions.append("apply_label:follow_up")
        
        # Category labels
        if classification:
            actions.append(f"apply_label:{classification.lower()}")
        
        return actions
    
    def _llm_route(self, state: EmailState) -> Dict[str, Any]:
        """Use LLM for additional routing suggestions"""
        
        prompt = ROUTER_PROMPT.format(
            classification=state.get("classification", "Unknown"),
            priority_score=state.get("priority_score", 0),
            intent=state.get("intent", "Unknown"),
            confidence=state.get("overall_confidence", 0)
        )
        
        messages = [
            SystemMessage(content="You are an expert email router. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return json.loads(response.content)
    
    def _extract_labels(self, actions: List[str]) -> List[str]:
        """Extract label names from actions"""
        labels = []
        for action in actions:
            if action.startswith("apply_label:"):
                label = action.replace("apply_label:", "")
                labels.append(label)
        return labels


# Node function for LangGraph
def router_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for action routing"""
    agent = RouterAgent()
    return agent.route(state)
