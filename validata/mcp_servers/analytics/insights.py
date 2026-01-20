"""Analytics insight generation logic"""
import logging
from typing import List, Dict, Any
from uuid import UUID
import openai
import json

from backend.core.config import settings
from backend.models.analytics import Insight, Pattern, InsightTrace
from backend.models.response import Response

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Generate insights from survey responses"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id
        )
    
    async def generate_insights(
        self,
        survey_id: UUID,
        responses: List[Response],
        account_context: Dict[str, Any]
    ) -> List[Insight]:
        """
        Generate insights from validated responses
        
        Args:
            survey_id: Survey UUID
            responses: List of validated responses
            account_context: Historical context from memory
        
        Returns:
            List of generated insights
        """
        try:
            if not responses:
                return []
            
            # Prepare response data for analysis
            response_data = []
            for resp in responses:
                response_data.append({
                    "id": str(resp.id),
                    "answers": [{"question_id": a.question_id, "value": a.value} for a in resp.answers],
                    "channel": resp.channel.value
                })
            
            # Build context string
            context_str = ""
            if account_context and account_context.get("recent_memories"):
                context_str = "\n\nHistorical Context:\n"
                for memory in account_context["recent_memories"][:5]:
                    context_str += f"- {memory.get('metadata', {}).get('content', '')}\n"
            
            # Generate insights using LLM
            prompt = f"""Analyze the following survey responses and generate actionable insights:

{context_str}

Survey Responses ({len(responses)} total):
{json.dumps(response_data, indent=2)}

Generate 3-5 key insights that:
1. Identify patterns and trends
2. Provide actionable recommendations
3. Highlight important findings
4. Consider historical context

For each insight, provide:
- Clear insight text
- Confidence score (0.0-1.0)
- Supporting data (response IDs and relevant answers)
- Analysis steps taken

Return JSON format:
{{
  "insights": [
    {{
      "insight_text": "Clear, actionable insight",
      "confidence_score": 0.85,
      "supporting_response_ids": ["id1", "id2"],
      "analysis_steps": ["step1", "step2"],
      "supporting_data": {{"key": "value"}}
    }}
  ]
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst. Generate actionable insights from survey data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            # Convert to Insight objects
            insights = []
            from datetime import datetime
            from uuid import uuid4
            
            for insight_data in result.get("insights", []):
                trace = InsightTrace(
                    source_responses=insight_data.get("supporting_response_ids", []),
                    analysis_steps=insight_data.get("analysis_steps", []),
                    memory_context=[m.get("id", "") for m in account_context.get("recent_memories", [])[:3]]
                )
                
                insight = Insight(
                    id=uuid4(),
                    survey_id=survey_id,
                    insight_text=insight_data["insight_text"],
                    confidence_score=insight_data["confidence_score"],
                    supporting_data=insight_data.get("supporting_data", {}),
                    trace=trace,
                    generated_at=datetime.utcnow()
                )
                insights.append(insight)
            
            logger.info(f"Generated {len(insights)} insights for survey {survey_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            raise
    
    async def detect_patterns(
        self,
        responses: List[Response]
    ) -> List[Pattern]:
        """
        Detect patterns in survey responses
        
        Args:
            responses: List of responses
        
        Returns:
            List of detected patterns
        """
        try:
            if not responses:
                return []
            
            # Prepare response data
            response_data = []
            for resp in responses:
                response_data.append({
                    "answers": [{"question_id": a.question_id, "value": a.value} for a in resp.answers]
                })
            
            # Detect patterns using LLM
            prompt = f"""Analyze these survey responses and identify patterns:

Responses ({len(responses)} total):
{json.dumps(response_data, indent=2)}

Identify:
1. Common themes or topics
2. Recurring sentiments
3. Frequency patterns
4. Correlations between answers

Return JSON format:
{{
  "patterns": [
    {{
      "pattern_type": "theme|sentiment|frequency|correlation",
      "description": "Clear description of the pattern",
      "frequency": 10,
      "confidence": 0.85,
      "examples": ["example1", "example2"]
    }}
  ]
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a pattern recognition expert. Identify trends in survey data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            # Convert to Pattern objects
            patterns = []
            for pattern_data in result.get("patterns", []):
                pattern = Pattern(
                    pattern_type=pattern_data["pattern_type"],
                    description=pattern_data["description"],
                    frequency=pattern_data["frequency"],
                    confidence=pattern_data["confidence"],
                    examples=pattern_data.get("examples", [])
                )
                patterns.append(pattern)
            
            logger.info(f"Detected {len(patterns)} patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect patterns: {e}")
            raise
    
    def aggregate_responses(
        self,
        responses: List[Response],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate response data with optional filters
        
        Args:
            responses: List of responses
            filters: Filter criteria
        
        Returns:
            Aggregated data
        """
        try:
            # Apply filters
            filtered_responses = responses
            
            if filters.get("channel"):
                filtered_responses = [r for r in filtered_responses if r.channel.value == filters["channel"]]
            
            if filters.get("date_from"):
                from datetime import datetime
                date_from = datetime.fromisoformat(filters["date_from"])
                filtered_responses = [r for r in filtered_responses if r.submitted_at >= date_from]
            
            if filters.get("date_to"):
                from datetime import datetime
                date_to = datetime.fromisoformat(filters["date_to"])
                filtered_responses = [r for r in filtered_responses if r.submitted_at <= date_to]
            
            # Aggregate data
            aggregations = {
                "total_responses": len(filtered_responses),
                "by_channel": {},
                "by_validation_status": {},
                "answer_distributions": {}
            }
            
            # Count by channel
            for resp in filtered_responses:
                channel = resp.channel.value
                aggregations["by_channel"][channel] = aggregations["by_channel"].get(channel, 0) + 1
            
            # Count by validation status
            for resp in filtered_responses:
                status = resp.validation_status.value
                aggregations["by_validation_status"][status] = aggregations["by_validation_status"].get(status, 0) + 1
            
            # Analyze answer distributions
            answer_counts = {}
            for resp in filtered_responses:
                for answer in resp.answers:
                    q_id = answer.question_id
                    if q_id not in answer_counts:
                        answer_counts[q_id] = {}
                    
                    value_str = str(answer.value)
                    answer_counts[q_id][value_str] = answer_counts[q_id].get(value_str, 0) + 1
            
            aggregations["answer_distributions"] = answer_counts
            
            logger.info(f"Aggregated {len(filtered_responses)} responses")
            return aggregations
            
        except Exception as e:
            logger.error(f"Failed to aggregate responses: {e}")
            raise
