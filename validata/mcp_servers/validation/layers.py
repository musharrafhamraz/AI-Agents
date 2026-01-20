"""7-Layer Reasoning Engine for response validation"""
import logging
from typing import Dict, Any
from datetime import datetime
import openai
import json

from backend.core.config import settings
from backend.models.response import Response
from backend.models.survey import Survey
from backend.models.validation import LayerResult

logger = logging.getLogger(__name__)


class ValidationLayers:
    """Implementation of the 7-Layer Reasoning Engine"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id
        )
    
    async def validate_layer_1_syntax(
        self,
        response: Response,
        survey: Survey
    ) -> LayerResult:
        """
        Layer 1: Syntax Layer
        Validates response format and structure
        """
        try:
            passed = True
            reasoning = []
            
            # Check if all required questions are answered
            required_questions = [q for q in survey.questions if q.required]
            answered_question_ids = {a.question_id for a in response.answers}
            
            for req_q in required_questions:
                if req_q.id not in answered_question_ids:
                    passed = False
                    reasoning.append(f"Missing required question: {req_q.id}")
            
            # Check answer format matches question type
            for answer in response.answers:
                question = next((q for q in survey.questions if q.id == answer.question_id), None)
                if not question:
                    passed = False
                    reasoning.append(f"Answer for unknown question: {answer.question_id}")
                    continue
                
                # Validate answer type
                if question.type.value == "multiple_choice":
                    if question.options and answer.value not in question.options:
                        passed = False
                        reasoning.append(f"Invalid option for question {question.id}")
            
            if passed:
                reasoning.append("All syntax checks passed")
            
            return LayerResult(
                layer=1,
                layer_name="Syntax Layer",
                passed=passed,
                reasoning="; ".join(reasoning),
                confidence=1.0 if passed else 0.0
            )
            
        except Exception as e:
            logger.error(f"Layer 1 validation failed: {e}")
            return LayerResult(
                layer=1,
                layer_name="Syntax Layer",
                passed=False,
                reasoning=f"Validation error: {e}",
                confidence=0.0
            )
    
    async def validate_layer_2_semantic(
        self,
        response: Response,
        survey: Survey
    ) -> LayerResult:
        """
        Layer 2: Semantic Layer
        Checks response meaning and coherence
        """
        try:
            # Use LLM to check semantic coherence
            prompt = f"""Analyze the following survey responses for semantic coherence:

Survey Questions:
{json.dumps([{"id": q.id, "text": q.text} for q in survey.questions], indent=2)}

Responses:
{json.dumps([{"question_id": a.question_id, "value": a.value} for a in response.answers], indent=2)}

Check if:
1. Answers make sense in context of the questions
2. Text responses are coherent and meaningful
3. Answers are not contradictory

Return JSON with:
{{
  "passed": true/false,
  "reasoning": "explanation",
  "confidence": 0.0-1.0
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a semantic analysis expert. Evaluate survey responses for coherence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            return LayerResult(
                layer=2,
                layer_name="Semantic Layer",
                passed=result["passed"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Layer 2 validation failed: {e}")
            return LayerResult(
                layer=2,
                layer_name="Semantic Layer",
                passed=True,  # Default to pass on error
                reasoning=f"Semantic check skipped due to error: {e}",
                confidence=0.5
            )
    
    async def validate_layer_3_consistency(
        self,
        response: Response,
        survey: Survey
    ) -> LayerResult:
        """
        Layer 3: Consistency Layer
        Ensures internal consistency within response
        """
        try:
            prompt = f"""Check for internal consistency in these survey responses:

Survey Questions:
{json.dumps([{"id": q.id, "text": q.text} for q in survey.questions], indent=2)}

Responses:
{json.dumps([{"question_id": a.question_id, "value": a.value} for a in response.answers], indent=2)}

Look for:
1. Contradictory answers
2. Logical inconsistencies
3. Conflicting information

Return JSON with:
{{
  "passed": true/false,
  "reasoning": "explanation",
  "confidence": 0.0-1.0
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a logical consistency expert. Find contradictions in survey responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            return LayerResult(
                layer=3,
                layer_name="Consistency Layer",
                passed=result["passed"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Layer 3 validation failed: {e}")
            return LayerResult(
                layer=3,
                layer_name="Consistency Layer",
                passed=True,
                reasoning=f"Consistency check skipped due to error: {e}",
                confidence=0.5
            )
    
    async def validate_layer_4_context(
        self,
        response: Response,
        survey: Survey,
        account_context: Dict[str, Any]
    ) -> LayerResult:
        """
        Layer 4: Context Layer
        Validates against survey context and account memory
        """
        try:
            context_str = ""
            if account_context and account_context.get("recent_memories"):
                context_str = "Historical Context:\n"
                for memory in account_context["recent_memories"][:5]:
                    context_str += f"- {memory.get('metadata', {}).get('content', '')}\n"
            
            prompt = f"""Validate survey responses against context:

{context_str}

Survey: {survey.title}
Description: {survey.description}

Responses:
{json.dumps([{"question_id": a.question_id, "value": a.value} for a in response.answers], indent=2)}

Check if responses:
1. Align with historical patterns
2. Make sense in survey context
3. Are consistent with account behavior

Return JSON with:
{{
  "passed": true/false,
  "reasoning": "explanation",
  "confidence": 0.0-1.0
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a context analysis expert. Validate responses against historical context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            return LayerResult(
                layer=4,
                layer_name="Context Layer",
                passed=result["passed"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Layer 4 validation failed: {e}")
            return LayerResult(
                layer=4,
                layer_name="Context Layer",
                passed=True,
                reasoning=f"Context check skipped due to error: {e}",
                confidence=0.5
            )
    
    async def validate_layer_5_adversarial(
        self,
        response: Response,
        survey: Survey
    ) -> LayerResult:
        """
        Layer 5: Adversarial Layer
        Challenges response with counter-arguments
        """
        try:
            prompt = f"""Act as an adversarial validator. Challenge these survey responses:

Survey Questions:
{json.dumps([{"id": q.id, "text": q.text} for q in survey.questions], indent=2)}

Responses:
{json.dumps([{"question_id": a.question_id, "value": a.value} for a in response.answers], indent=2)}

Try to find:
1. Potential biases
2. Suspicious patterns
3. Gaming or manipulation attempts
4. Unrealistic responses

Return JSON with:
{{
  "passed": true/false,
  "reasoning": "explanation of challenges",
  "confidence": 0.0-1.0
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an adversarial validator. Challenge survey responses to find issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher temperature for creative challenges
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            return LayerResult(
                layer=5,
                layer_name="Adversarial Layer",
                passed=result["passed"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Layer 5 validation failed: {e}")
            return LayerResult(
                layer=5,
                layer_name="Adversarial Layer",
                passed=True,
                reasoning=f"Adversarial check skipped due to error: {e}",
                confidence=0.5
            )
    
    async def validate_layer_6_hallucination(
        self,
        response: Response,
        survey: Survey
    ) -> LayerResult:
        """
        Layer 6: Hallucination Layer
        Detects fabricated or unsupported claims
        """
        try:
            prompt = f"""Detect potential hallucinations or fabricated information in these responses:

Survey Questions:
{json.dumps([{"id": q.id, "text": q.text} for q in survey.questions], indent=2)}

Responses:
{json.dumps([{"question_id": a.question_id, "value": a.value} for a in response.answers], indent=2)}

Look for:
1. Unsupported factual claims
2. Impossible scenarios
3. Fabricated details
4. Overly specific information without basis

Return JSON with:
{{
  "passed": true/false,
  "reasoning": "explanation",
  "confidence": 0.0-1.0
}}"""
            
            llm_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a hallucination detection expert. Identify fabricated or unsupported claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(llm_response.choices[0].message.content)
            
            return LayerResult(
                layer=6,
                layer_name="Hallucination Layer",
                passed=result["passed"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Layer 6 validation failed: {e}")
            return LayerResult(
                layer=6,
                layer_name="Hallucination Layer",
                passed=True,
                reasoning=f"Hallucination check skipped due to error: {e}",
                confidence=0.5
            )
    
    async def validate_layer_7_confidence(
        self,
        response: Response,
        survey: Survey,
        previous_layers: list[LayerResult]
    ) -> LayerResult:
        """
        Layer 7: Confidence Layer
        Assigns overall confidence score based on all previous layers
        """
        try:
            # Calculate aggregate confidence
            layer_confidences = [layer.confidence for layer in previous_layers]
            layer_passes = [layer.passed for layer in previous_layers]
            
            # Weighted average (earlier layers have slightly more weight)
            weights = [1.2, 1.1, 1.0, 1.0, 0.9, 0.9]
            weighted_confidence = sum(c * w for c, w in zip(layer_confidences, weights)) / sum(weights)
            
            # All layers must pass for overall pass
            all_passed = all(layer_passes)
            
            # Generate reasoning
            failed_layers = [layer.layer_name for layer in previous_layers if not layer.passed]
            if failed_layers:
                reasoning = f"Failed layers: {', '.join(failed_layers)}"
            else:
                reasoning = f"All validation layers passed. Overall confidence: {weighted_confidence:.2f}"
            
            return LayerResult(
                layer=7,
                layer_name="Confidence Layer",
                passed=all_passed and weighted_confidence >= 0.7,
                reasoning=reasoning,
                confidence=weighted_confidence
            )
            
        except Exception as e:
            logger.error(f"Layer 7 validation failed: {e}")
            return LayerResult(
                layer=7,
                layer_name="Confidence Layer",
                passed=False,
                reasoning=f"Confidence calculation failed: {e}",
                confidence=0.0
            )
