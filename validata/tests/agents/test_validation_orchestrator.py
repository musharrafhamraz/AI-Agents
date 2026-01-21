"""Tests for Validation Orchestrator"""
import pytest
from uuid import uuid4

from agents.validation_orchestrator import ValidationOrchestrator, ValidationState


class MockValidationClient:
    """Mock validation MCP client for testing"""
    
    async def handle_request(self, request):
        """Mock request handler"""
        tool = request["tool"]
        
        if tool == "validate_layer":
            layer = request["parameters"]["layer"]
            return {
                "status": "success",
                "data": {
                    "layer_result": {
                        "layer": layer,
                        "layer_name": f"Layer {layer}",
                        "passed": True,
                        "reasoning": "Test passed",
                        "confidence": 0.9,
                        "timestamp": "2024-01-16T12:00:00"
                    }
                }
            }
        
        return {"status": "error", "error": {"message": "Unknown tool"}}


@pytest.fixture
def orchestrator():
    """Create orchestrator with mock client"""
    mock_client = MockValidationClient()
    return ValidationOrchestrator(mock_client)


@pytest.mark.asyncio
async def test_validation_workflow(orchestrator):
    """Test complete validation workflow"""
    response_id = uuid4()
    
    final_state = await orchestrator.validate_response(response_id)
    
    assert final_state["response_id"] == response_id
    assert final_state["validation_status"] in ["validated", "failed"]
    assert len(final_state["layer_results"]) == 7
    assert final_state["error"] is None


@pytest.mark.asyncio
async def test_validation_state_initialization(orchestrator):
    """Test validation state initialization"""
    response_id = uuid4()
    
    initial_state = ValidationState(
        response_id=response_id,
        current_layer=0,
        layer_results=[],
        validation_status="pending",
        error=None,
        account_context=None
    )
    
    assert initial_state["response_id"] == response_id
    assert initial_state["current_layer"] == 0
    assert len(initial_state["layer_results"]) == 0
