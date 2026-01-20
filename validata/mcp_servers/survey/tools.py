"""Survey MCP Server tools for survey creation and management"""
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4
import openai

from backend.core.config import settings
from backend.models.survey import Question, QuestionType, Survey, SurveyCreate, Template

logger = logging.getLogger(__name__)


class SurveyTools:
    """Tools for survey management"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id
        )
        self.templates = self._load_templates()
    
    def _load_templates(self) -> List[Template]:
        """Load predefined survey templates"""
        return [
            Template(
                id="customer-satisfaction",
                name="Customer Satisfaction Survey",
                description="Measure customer satisfaction with products or services",
                category="Customer Feedback",
                questions=[
                    Question(
                        type=QuestionType.RATING,
                        text="How satisfied are you with our product/service?",
                        required=True
                    ),
                    Question(
                        type=QuestionType.TEXT,
                        text="What do you like most about our product/service?",
                        required=False
                    ),
                    Question(
                        type=QuestionType.TEXT,
                        text="What could we improve?",
                        required=False
                    ),
                    Question(
                        type=QuestionType.MULTIPLE_CHOICE,
                        text="Would you recommend us to others?",
                        options=["Definitely", "Probably", "Not sure", "Probably not", "Definitely not"],
                        required=True
                    )
                ]
            ),
            Template(
                id="employee-engagement",
                name="Employee Engagement Survey",
                description="Assess employee satisfaction and engagement",
                category="HR",
                questions=[
                    Question(
                        type=QuestionType.RATING,
                        text="How satisfied are you with your current role?",
                        required=True
                    ),
                    Question(
                        type=QuestionType.RATING,
                        text="How likely are you to recommend this company as a place to work?",
                        required=True
                    ),
                    Question(
                        type=QuestionType.TEXT,
                        text="What motivates you most at work?",
                        required=False
                    )
                ]
            ),
            Template(
                id="product-feedback",
                name="Product Feedback Survey",
                description="Gather feedback on product features and usability",
                category="Product",
                questions=[
                    Question(
                        type=QuestionType.RATING,
                        text="How easy is the product to use?",
                        required=True
                    ),
                    Question(
                        type=QuestionType.MULTIPLE_CHOICE,
                        text="Which features do you use most?",
                        options=["Feature A", "Feature B", "Feature C", "Feature D"],
                        required=False
                    ),
                    Question(
                        type=QuestionType.TEXT,
                        text="What new features would you like to see?",
                        required=False
                    )
                ]
            )
        ]
    
    async def generate_questions(
        self,
        topic: str,
        account_context: Optional[Dict[str, Any]] = None,
        num_questions: int = 5
    ) -> List[Question]:
        """
        Generate survey questions using LLM based on topic and context
        
        Args:
            topic: Research topic or survey purpose
            account_context: Historical context from account memory
            num_questions: Number of questions to generate
        
        Returns:
            List of generated questions
        """
        try:
            # Build prompt with context
            context_str = ""
            if account_context and account_context.get("recent_memories"):
                context_str = "\n\nAccount Context:\n"
                for memory in account_context["recent_memories"][:3]:
                    context_str += f"- {memory.get('metadata', {}).get('content', '')}\n"
            
            prompt = f"""Generate {num_questions} survey questions for the following topic: {topic}

{context_str}

Requirements:
- Questions should be clear, unbiased, and actionable
- Mix different question types (rating, multiple choice, text)
- Questions should be relevant to the topic
- Avoid leading or loaded questions

Return the questions in JSON format as an array with this structure:
[
  {{
    "type": "rating|multiple_choice|text",
    "text": "Question text",
    "options": ["option1", "option2"] (only for multiple_choice),
    "required": true|false
  }}
]"""
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert survey designer. Generate high-quality, unbiased survey questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            import json
            questions_data = json.loads(response.choices[0].message.content)
            
            # Convert to Question objects
            questions = []
            for q_data in questions_data.get("questions", []):
                question = Question(
                    type=QuestionType(q_data["type"]),
                    text=q_data["text"],
                    options=q_data.get("options"),
                    required=q_data.get("required", True)
                )
                questions.append(question)
            
            logger.info(f"Generated {len(questions)} questions for topic: {topic}")
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            raise
    
    def list_templates(self) -> List[Template]:
        """Get all available survey templates"""
        return self.templates
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
