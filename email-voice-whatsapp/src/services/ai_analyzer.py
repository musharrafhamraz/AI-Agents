from groq import Groq
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class AIAnalyzerService:
    """Service for analyzing emails using Groq AI"""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def classify_importance(self, email: Dict) -> float:
        """Classify email importance on scale of 1-10"""
        try:
            prompt = f"""Analyze this email and rate its importance from 1-10.
Consider: urgency, sender authority, action items, deadlines, and relevance.

From: {email['sender']}
Subject: {email['subject']}
Body Preview: {email['body'][:500]}

Respond with ONLY a single number between 1-10. No explanation."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract number from response
            score = float(''.join(filter(str.isdigit, score_text)))
            score = max(1, min(10, score))  # Clamp between 1-10
            
            logger.info(f"Email importance score: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Error classifying importance: {str(e)}")
            return 5.0  # Default middle score on error
    
    def summarize_email(self, email: Dict) -> str:
        """Generate concise email summary"""
        try:
            # Limit body length for API
            body_text = email['body'][:2000] if len(email['body']) > 2000 else email['body']
            
            prompt = f"""Summarize this email in 2-3 clear, concise sentences.
Focus on: who sent it, the main topic, and any action needed.
Make it conversational and easy to understand when read aloud.

From: {email['sender']}
Subject: {email['subject']}
Body: {body_text}

Provide ONLY the summary, no additional text."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for email from {email['sender']}")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing email: {str(e)}")
            # Fallback to basic summary
            return f"Email from {email['sender']} about: {email['subject']}"
    
    def analyze_batch(self, emails: list[Dict]) -> list[Tuple[Dict, float, str]]:
        """Analyze multiple emails and return (email, importance, summary) tuples"""
        results = []
        
        for email in emails:
            try:
                importance = self.classify_importance(email)
                summary = self.summarize_email(email)
                results.append((email, importance, summary))
            except Exception as e:
                logger.error(f"Error analyzing email {email.get('id')}: {str(e)}")
                continue
        
        return results
