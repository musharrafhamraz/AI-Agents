"""Email Parser Agent - Extracts structured data from raw emails"""

import json
import re
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..graph.state import EmailState
from ..config import PARSING_PROMPT
from ..utils import create_json_llm


class EmailParserAgent:
    """Agent that parses raw email content into structured data"""
    
    def __init__(self):
        self.llm = create_json_llm()
    
    def parse_email(self, state: EmailState) -> Dict[str, Any]:
        """
        Parse email and extract structured information.
        
        Args:
            state: Current email state
        
        Returns:
            Updated state dict with parsed data
        """
        try:
            # Extract entities and structure using LLM
            parsed_data = self._llm_parse(state)
            
            # Clean the body text
            clean_body = self._remove_signature(state["body"])
            clean_body = self._remove_quoted_text(clean_body)
            
            return {
                "body": clean_body,
                "processing_stage": "parsed",
                "action_items": parsed_data.get("action_items", [])
            }
            
        except Exception as e:
            return {
                "processing_stage": "parse_error",
                "error": f"Parsing failed: {str(e)}"
            }
    
    def _llm_parse(self, state: EmailState) -> Dict[str, Any]:
        """Use LLM to extract structured information"""
        
        prompt = PARSING_PROMPT.format(
            raw_email=f"Subject: {state['subject']}\n\nBody: {state['body']}"
        )
        
        messages = [
            SystemMessage(content="You are an expert email parser. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return json.loads(response.content)
    
    def _remove_signature(self, text: str) -> str:
        """Remove email signature from text"""
        # Common signature patterns
        signature_patterns = [
            r'\n--\s*\n',  # Standard signature delimiter
            r'\nBest regards,.*',
            r'\nSincerely,.*',
            r'\nThanks,.*',
            r'\nSent from my .*',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return text[:match.start()]
        
        return text
    
    def _remove_quoted_text(self, text: str) -> str:
        """Remove quoted/forwarded text"""
        # Remove lines starting with > (quoted text)
        lines = text.split('\n')
        clean_lines = [line for line in lines if not line.strip().startswith('>')]
        
        # Remove "On ... wrote:" patterns
        text = '\n'.join(clean_lines)
        text = re.sub(r'\nOn .* wrote:.*', '', text, flags=re.DOTALL)
        
        return text.strip()


# Node function for LangGraph
def email_parser_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for email parsing"""
    agent = EmailParserAgent()
    return agent.parse_email(state)
