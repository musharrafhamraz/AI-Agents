"""Validation MCP Server tools"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select

from .layers import ValidationLayers
from backend.models.response import Response, ResponseORM, ValidationStatus as ResponseValidationStatus
from backend.models.survey import Survey, SurveyORM, Question
from backend.models.validation import ValidationResult, ValidationResultCreate, ValidationORM, LayerResult
from backend.database.connection import db_manager

logger = logging.getLogger(__name__)


class ValidationTools:
    """Tools for response validation"""
    
    def __init__(self):
        self.layers = ValidationLayers()
    
    async def validate_response(
        self,
        response_id: UUID,
        account_context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Run full 7-layer validation on a response
        
        Args:
            response_id: Response UUID
            account_context: Account memory context
        
        Returns:
            Complete validation result
        """
        try:
            # Get response and survey from database
            async with db_manager.session() as session:
                # Get response
                response_result = await session.execute(
                    select(ResponseORM).where(ResponseORM.id == response_id)
                )
                response_orm = response_result.scalar_one_or_none()
                
                if not response_orm:
                    raise ValueError(f"Response not found: {response_id}")
                
                # Get survey
                survey_result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == response_orm.survey_id)
                )
                survey_orm = survey_result.scalar_one_or_none()
                
                if not survey_orm:
                    raise ValueError(f"Survey not found: {response_orm.survey_id}")
                
                # Convert to Pydantic models
                from backend.models.response import Answer
                response = Response(
                    id=response_orm.id,
                    survey_id=response_orm.survey_id,
                    answers=[Answer(**a) for a in response_orm.answers],
                    channel=response_orm.channel,
                    respondent_id=response_orm.respondent_id,
                    submitted_at=response_orm.submitted_at,
                    validation_status=response_orm.validation_status
                )
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
            
            # Run all 7 layers sequentially
            layer_results = []
            
            # Layer 1: Syntax
            layer_1 = await self.layers.validate_layer_1_syntax(response, survey)
            layer_results.append(layer_1)
            
            # Layer 2: Semantic
            layer_2 = await self.layers.validate_layer_2_semantic(response, survey)
            layer_results.append(layer_2)
            
            # Layer 3: Consistency
            layer_3 = await self.layers.validate_layer_3_consistency(response, survey)
            layer_results.append(layer_3)
            
            # Layer 4: Context
            layer_4 = await self.layers.validate_layer_4_context(
                response, survey, account_context or {}
            )
            layer_results.append(layer_4)
            
            # Layer 5: Adversarial
            layer_5 = await self.layers.validate_layer_5_adversarial(response, survey)
            layer_results.append(layer_5)
            
            # Layer 6: Hallucination
            layer_6 = await self.layers.validate_layer_6_hallucination(response, survey)
            layer_results.append(layer_6)
            
            # Layer 7: Confidence
            layer_7 = await self.layers.validate_layer_7_confidence(
                response, survey, layer_results
            )
            layer_results.append(layer_7)
            
            # Determine final status
            all_passed = all(layer.passed for layer in layer_results)
            final_status = ResponseValidationStatus.VALIDATED if all_passed else ResponseValidationStatus.FAILED
            
            # Calculate overall confidence
            confidence_score = layer_results[-1].confidence
            
            # Create validation result
            validation_result = ValidationResultCreate(
                response_id=response_id,
                layer_results=layer_results,
                final_status=final_status,
                confidence_score=confidence_score
            )
            
            # Store in database
            async with db_manager.session() as session:
                validation_orm = ValidationORM(
                    response_id=response_id,
                    layer_results=[lr.model_dump() for lr in layer_results],
                    final_status=final_status.value,
                    confidence_score=confidence_score
                )
                
                session.add(validation_orm)
                
                # Update response validation status
                response_orm = await session.get(ResponseORM, response_id)
                if response_orm:
                    response_orm.validation_status = final_status
                
                await session.commit()
                await session.refresh(validation_orm)
                
                result = ValidationResult(
                    id=validation_orm.id,
                    response_id=validation_orm.response_id,
                    layer_results=layer_results,
                    final_status=final_status,
                    confidence_score=validation_orm.confidence_score,
                    validated_at=validation_orm.validated_at
                )
            
            logger.info(f"Validation completed for response {response_id}: {final_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to validate response: {e}")
            raise
    
    async def validate_layer(
        self,
        response_id: UUID,
        layer: int,
        account_context: Optional[Dict[str, Any]] = None
    ) -> LayerResult:
        """
        Validate a specific layer only
        
        Args:
            response_id: Response UUID
            layer: Layer number (1-7)
            account_context: Account memory context
        
        Returns:
            Layer result
        """
        try:
            # Get response and survey
            async with db_manager.session() as session:
                response_result = await session.execute(
                    select(ResponseORM).where(ResponseORM.id == response_id)
                )
                response_orm = response_result.scalar_one_or_none()
                
                if not response_orm:
                    raise ValueError(f"Response not found: {response_id}")
                
                survey_result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == response_orm.survey_id)
                )
                survey_orm = survey_result.scalar_one_or_none()
                
                if not survey_orm:
                    raise ValueError(f"Survey not found: {response_orm.survey_id}")
                
                # Convert to Pydantic models
                from backend.models.response import Answer
                response = Response(
                    id=response_orm.id,
                    survey_id=response_orm.survey_id,
                    answers=[Answer(**a) for a in response_orm.answers],
                    channel=response_orm.channel,
                    respondent_id=response_orm.respondent_id,
                    submitted_at=response_orm.submitted_at,
                    validation_status=response_orm.validation_status
                )
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
            
            # Run specific layer
            if layer == 1:
                result = await self.layers.validate_layer_1_syntax(response, survey)
            elif layer == 2:
                result = await self.layers.validate_layer_2_semantic(response, survey)
            elif layer == 3:
                result = await self.layers.validate_layer_3_consistency(response, survey)
            elif layer == 4:
                result = await self.layers.validate_layer_4_context(
                    response, survey, account_context or {}
                )
            elif layer == 5:
                result = await self.layers.validate_layer_5_adversarial(response, survey)
            elif layer == 6:
                result = await self.layers.validate_layer_6_hallucination(response, survey)
            elif layer == 7:
                # For layer 7, we need previous layers
                raise ValueError("Layer 7 requires all previous layers to be completed")
            else:
                raise ValueError(f"Invalid layer number: {layer}")
            
            logger.info(f"Layer {layer} validation completed for response {response_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to validate layer {layer}: {e}")
            raise
    
    async def get_validation_status(self, response_id: UUID) -> Dict[str, Any]:
        """
        Get validation status for a response
        
        Args:
            response_id: Response UUID
        
        Returns:
            Validation status information
        """
        try:
            async with db_manager.session() as session:
                # Get validation
                validation_result = await session.execute(
                    select(ValidationORM).where(ValidationORM.response_id == response_id)
                )
                validation_orm = validation_result.scalar_one_or_none()
                
                if not validation_orm:
                    return {
                        "response_id": str(response_id),
                        "status": "pending",
                        "completed_layers": 0,
                        "total_layers": 7
                    }
                
                layer_results = validation_orm.layer_results
                
                return {
                    "response_id": str(response_id),
                    "status": validation_orm.final_status,
                    "completed_layers": len(layer_results),
                    "total_layers": 7,
                    "confidence_score": validation_orm.confidence_score,
                    "validated_at": validation_orm.validated_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get validation status: {e}")
            raise
    
    async def challenge_response(
        self,
        response_id: UUID,
        challenge_type: str
    ) -> Dict[str, Any]:
        """
        Run adversarial challenge on a response
        
        Args:
            response_id: Response UUID
            challenge_type: Type of challenge to run
        
        Returns:
            Challenge result
        """
        try:
            # Get response and survey
            async with db_manager.session() as session:
                response_result = await session.execute(
                    select(ResponseORM).where(ResponseORM.id == response_id)
                )
                response_orm = response_result.scalar_one_or_none()
                
                if not response_orm:
                    raise ValueError(f"Response not found: {response_id}")
                
                survey_result = await session.execute(
                    select(SurveyORM).where(SurveyORM.id == response_orm.survey_id)
                )
                survey_orm = survey_result.scalar_one_or_none()
                
                # Convert to Pydantic models
                from backend.models.response import Answer
                response = Response(
                    id=response_orm.id,
                    survey_id=response_orm.survey_id,
                    answers=[Answer(**a) for a in response_orm.answers],
                    channel=response_orm.channel,
                    respondent_id=response_orm.respondent_id,
                    submitted_at=response_orm.submitted_at,
                    validation_status=response_orm.validation_status
                )
                
                survey = Survey(
                    id=survey_orm.id,
                    account_id=survey_orm.account_id,
                    title=survey_orm.title,
                    description=survey_orm.description,
                    questions=[Question(**q) for q in survey_orm.questions],
                    created_at=survey_orm.created_at,
                    updated_at=survey_orm.updated_at,
                    status=survey_orm.status
                )
            
            # Run adversarial layer
            result = await self.layers.validate_layer_5_adversarial(response, survey)
            
            return {
                "challenge_type": challenge_type,
                "passed": result.passed,
                "reasoning": result.reasoning,
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to challenge response: {e}")
            raise
