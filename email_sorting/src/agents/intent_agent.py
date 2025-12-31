"""Intent Detector Agent - Understands sender's purpose and intent"""

import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import EmailState
from ..config import INTENT_PROMPT
from ..utils import create_json_llm


class IntentAgent:
    """Agent that detects sender intent"""
    
    def __init__(self):
        self.llm = create_json_llm()
    
    def detect_intent(self, state: EmailState) -> Dict[str, Any]:
        """
        Detect the sender's primary intent.
        
        Args:
            state: Current email state
        
        Returns:
            Updated state dict with intent analysis
        """
        try:
            result = self._llm_detect(
                sender=state["sender"],
                subject=state["subject"],
                body=state["body"]
            )
            
            return {
                "intent": result["intent"],
                "intent_confidence": result["confidence"],
                "action_items": result.get("action_items", []),
                "requires_response": result["requires_response"],
                "intent_reasoning": result["reasoning"]
            }
            
        except Exception as e:
            return {
                "error": f"Intent detection failed: {str(e)}"
            }
    
    def _llm_detect(
        self,
        sender: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """Use LLM to detect intent"""
        
        prompt = INTENT_PROMPT.format(
            sender=sender,
            subject=subject,
            body=body[:1000]
        )
        
        messages = [
            SystemMessage(content="You are an expert at understanding email intent. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return json.loads(response.content)


# Node function for LangGraph
def intent_detector_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for intent detection"""
    agent = IntentAgent()
    return agent.detect_intent(state)
