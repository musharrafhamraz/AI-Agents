"""Validation Orchestrator - coordinates multi-layer validation workflow"""
import logging
from typing import TypedDict, Optional, List
from uuid import UUID
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.models.validation import LayerResult
from backend.models.response import ValidationStatus

logger = logging.getLogger(__name__)


class ValidationState(TypedDict):
    """State for validation workflow"""
    response_id: UUID
    current_layer: int
    layer_results: List[LayerResult]
    validation_status: str
    error: Optional[str]
    account_context: Optional[dict]


class ValidationOrchestrator:
    """Orchestrates multi-layer validation workflow using LangGraph"""
    
    def __init__(self, validation_mcp_client):
        """
        Initialize orchestrator
        
        Args:
            validation_mcp_client: Client for Validation MCP Server
        """
        self.validation_client = validation_mcp_client
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the validation workflow graph"""
        workflow = StateGraph(ValidationState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_validation)
        workflow.add_node("validate_layer", self._validate_layer)
        workflow.add_node("check_layer_result", self._check_layer_result)
        workflow.add_node("finalize", self._finalize_validation)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("initialize")
        
        # Add edges
        workflow.add_edge("initialize", "validate_layer")
        workflow.add_edge("validate_layer", "check_layer_result")
        
        # Conditional edges from check_layer_result
        workflow.add_conditional_edges(
            "check_layer_result",
            self._should_continue,
            {
                "continue": "validate_layer",
                "finalize": "finalize",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("finalize", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _initialize_validation(self, state: ValidationState) -> ValidationState:
        """Initialize validation state"""
        logger.info(f"Initializing validation for response {state['response_id']}")
        
        state["current_layer"] = 1
        state["layer_results"] = []
        state["validation_status"] = "in_progress"
        state["error"] = None
        
        return state
    
    async def _validate_layer(self, state: ValidationState) -> ValidationState:
        """Validate current layer"""
        try:
            layer = state["current_layer"]
            response_id = state["response_id"]
            
            logger.info(f"Validating layer {layer} for response {response_id}")
            
            # Call Validation MCP Server
            request = {
                "tool": "validate_layer",
                "parameters": {
                    "response_id": str(response_id),
                    "layer": layer,
                    "account_context": state.get("account_context")
                }
            }
            
            response = await self.validation_client.handle_request(request)
            
            if response["status"] == "success":
                layer_result = LayerResult(**response["data"]["layer_result"])
                state["layer_results"].append(layer_result)
                logger.info(f"Layer {layer} completed: {layer_result.passed}")
            else:
                state["error"] = response["error"]["message"]
                logger.error(f"Layer {layer} failed: {state['error']}")
            
        except Exception as e:
            state["error"] = str(e)
            logger.error(f"Error validating layer {state['current_layer']}: {e}")
        
        return state
    
    async def _check_layer_result(self, state: ValidationState) -> ValidationState:
        """Check layer result and determine next action"""
        if state["error"]:
            return state
        
        current_layer = state["current_layer"]
        layer_results = state["layer_results"]
        
        # Check if current layer passed
        if layer_results:
            last_result = layer_results[-1]
            
            # If layer failed critically, we might want to stop
            # For now, continue through all layers
            if not last_result.passed:
                logger.warning(f"Layer {current_layer} failed but continuing validation")
        
        # Move to next layer
        state["current_layer"] = current_layer + 1
        
        return state
    
    def _should_continue(self, state: ValidationState) -> str:
        """Determine if workflow should continue"""
        if state["error"]:
            return "error"
        
        # Continue if we haven't completed all 7 layers
        if state["current_layer"] <= 7:
            return "continue"
        
        return "finalize"
    
    async def _finalize_validation(self, state: ValidationState) -> ValidationState:
        """Finalize validation and determine final status"""
        logger.info(f"Finalizing validation for response {state['response_id']}")
        
        # Determine final status based on all layers
        all_passed = all(result.passed for result in state["layer_results"])
        
        if all_passed:
            state["validation_status"] = ValidationStatus.VALIDATED.value
        else:
            state["validation_status"] = ValidationStatus.FAILED.value
        
        logger.info(f"Validation completed: {state['validation_status']}")
        
        return state
    
    async def _handle_error(self, state: ValidationState) -> ValidationState:
        """Handle validation errors"""
        logger.error(f"Validation error for response {state['response_id']}: {state['error']}")
        
        state["validation_status"] = "error"
        
        return state
    
    async def validate_response(
        self,
        response_id: UUID,
        account_context: Optional[dict] = None
    ) -> ValidationState:
        """
        Execute validation workflow for a response
        
        Args:
            response_id: Response UUID
            account_context: Optional account context
        
        Returns:
            Final validation state
        """
        initial_state = ValidationState(
            response_id=response_id,
            current_layer=0,
            layer_results=[],
            validation_status="pending",
            error=None,
            account_context=account_context
        )
        
        # Execute workflow
        config = {"configurable": {"thread_id": str(response_id)}}
        final_state = await self.workflow.ainvoke(initial_state, config)
        
        return final_state
    
    async def get_validation_history(self, response_id: UUID) -> List[ValidationState]:
        """
        Get validation execution history for a response
        
        Args:
            response_id: Response UUID
        
        Returns:
            List of validation states
        """
        config = {"configurable": {"thread_id": str(response_id)}}
        
        # Get checkpoint history
        history = []
        async for state in self.workflow.aget_state_history(config):
            history.append(state.values)
        
        return history
