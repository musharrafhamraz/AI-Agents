"""Classification Agent - Categorizes emails into predefined categories"""

import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import EmailState
from ..config import CLASSIFICATION_PROMPT, settings
from ..utils import create_json_llm


class ClassificationAgent:
    """Agent that classifies emails into categories"""
    
    def __init__(self):
        self.llm = create_json_llm()
        self.categories = settings.CATEGORIES
    
    def classify(self, state: EmailState) -> Dict[str, Any]:
        """
        Classify email into appropriate category.
        
        Args:
            state: Current email state with sender, subject, body
        
        Returns:
            Updated state dict with classification results
        """
        try:
            # Prepare context
            similar_emails = self._format_similar_emails(state.get("similar_emails", []))
            sender_history = self._format_sender_history(state.get("sender_history"))
            
            # Get classification from LLM
            result = self._llm_classify(
                sender=state["sender"],
                subject=state["subject"],
                body=state["body"],
                similar_emails=similar_emails,
                sender_history=sender_history
            )
            
            return {
                "classification": result["category"],
                "classification_confidence": result["confidence"],
                "classification_reasoning": result["reasoning"],
                "processing_stage": "classified"
            }
            
        except Exception as e:
            return {
                "processing_stage": "classification_error",
                "error": f"Classification failed: {str(e)}"
            }
    
    def _llm_classify(
        self,
        sender: str,
        subject: str,
        body: str,
        similar_emails: str,
        sender_history: str
    ) -> Dict[str, Any]:
        """Use LLM to classify email"""
        
        prompt = CLASSIFICATION_PROMPT.format(
            sender=sender,
            subject=subject,
            body=body[:1000],  # Limit body length
            categories=", ".join(self.categories),
            similar_emails=similar_emails,
            sender_history=sender_history
        )
        
        messages = [
            SystemMessage(content="You are an expert email classifier. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return json.loads(response.content)
    
    def _format_similar_emails(self, similar_emails: list) -> str:
        """Format similar emails for context"""
        if not similar_emails:
            return "No similar emails found."
        
        formatted = []
        for email in similar_emails[:3]:  # Top 3 similar
            formatted.append(
                f"- Category: {email.get('category', 'Unknown')}, "
                f"Similarity: {email.get('similarity', 0):.2f}"
            )
        return "\n".join(formatted)
    
    def _format_sender_history(self, sender_history: dict) -> str:
        """Format sender history for context"""
        if not sender_history:
            return "No previous history with this sender."
        
        return (
            f"Total emails: {sender_history.get('total_emails', 0)}, "
            f"Common categories: {', '.join(sender_history.get('common_categories', []))}, "
            f"VIP: {sender_history.get('is_vip', False)}"
        )


# Node function for LangGraph
def classifier_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for email classification"""
    agent = ClassificationAgent()
    return agent.classify(state)
