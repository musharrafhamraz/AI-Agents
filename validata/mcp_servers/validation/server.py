"""Validation MCP Server - handles 7-Layer Reasoning Engine validation"""
import asyncio
import logging
from typing import Any, Dict
from uuid import UUID

from .tools import ValidationTools
from backend.database.connection import db_manager
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationMCPServer:
    """MCP Server for response validation using 7-Layer Reasoning Engine"""
    
    def __init__(self):
        self.tools = ValidationTools()
        self.running = False
    
    async def start(self) -> None:
        """Start the MCP server"""
        try:
            # Connect to database
            await db_manager.connect()
            
            self.running = True
            logger.info(f"Validation MCP Server started on port {settings.mcp_validation_port}")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start Validation MCP Server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server"""
        self.running = False
        await db_manager.disconnect()
        logger.info("Validation MCP Server stopped")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming MCP requests
        
        Request format:
        {
            "tool": "tool_name",
            "parameters": {...}
        }
        """
        try:
            tool_name = request.get("tool")
            parameters = request.get("parameters", {})
            
            # Validate request
            if not tool_name:
                return self._error_response("Missing 'tool' field in request")
            
            # Route to appropriate tool
            if tool_name == "validate_response":
                response_id = UUID(parameters["response_id"])
                account_context = parameters.get("account_context")
                
                result = await self.tools.validate_response(response_id, account_context)
                return self._success_response({"validation": result.model_dump()})
            
            elif tool_name == "validate_layer":
                response_id = UUID(parameters["response_id"])
                layer = parameters["layer"]
                account_context = parameters.get("account_context")
                
                result = await self.tools.validate_layer(response_id, layer, account_context)
                return self._success_response({"layer_result": result.model_dump()})
            
            elif tool_name == "get_validation_status":
                response_id = UUID(parameters["response_id"])
                
                status = await self.tools.get_validation_status(response_id)
                return self._success_response({"status": status})
            
            elif tool_name == "challenge_response":
                response_id = UUID(parameters["response_id"])
                challenge_type = parameters.get("challenge_type", "general")
                
                result = await self.tools.challenge_response(response_id, challenge_type)
                return self._success_response({"challenge": result})
            
            else:
                return self._error_response(f"Unknown tool: {tool_name}", status_code=400)
        
        except ValueError as e:
            return self._error_response(f"Invalid value: {e}", status_code=400)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._error_response(f"Internal server error: {e}", status_code=500)
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format success response"""
        return {
            "status": "success",
            "data": data
        }
    
    def _error_response(self, message: str, status_code: int = 400) -> Dict[str, Any]:
        """Format error response"""
        return {
            "status": "error",
            "error": {
                "message": message,
                "code": status_code
            }
        }
    
    async def get_resources(self, resource_uri: str) -> Dict[str, Any]:
        """
        Handle resource requests
        
        Supported resources:
        - validation://{response_id} - Get validation results
        - layers:// - Get layer definitions
        """
        try:
            if resource_uri.startswith("validation://"):
                response_id_str = resource_uri.replace("validation://", "")
                response_id = UUID(response_id_str)
                
                status = await self.tools.get_validation_status(response_id)
                return self._success_response({"validation": status})
            
            elif resource_uri == "layers://":
                layers_info = {
                    "layers": [
                        {"layer": 1, "name": "Syntax Layer", "description": "Validates response format and structure"},
                        {"layer": 2, "name": "Semantic Layer", "description": "Checks response meaning and coherence"},
                        {"layer": 3, "name": "Consistency Layer", "description": "Ensures internal consistency"},
                        {"layer": 4, "name": "Context Layer", "description": "Validates against survey context and memory"},
                        {"layer": 5, "name": "Adversarial Layer", "description": "Challenges response with counter-arguments"},
                        {"layer": 6, "name": "Hallucination Layer", "description": "Detects fabricated or unsupported claims"},
                        {"layer": 7, "name": "Confidence Layer", "description": "Assigns overall confidence score"}
                    ]
                }
                return self._success_response(layers_info)
            
            else:
                return self._error_response(f"Unknown resource: {resource_uri}", status_code=404)
        
        except Exception as e:
            logger.error(f"Error getting resource: {e}")
            return self._error_response(f"Failed to get resource: {e}", status_code=500)


async def main():
    """Main entry point for Validation MCP Server"""
    server = ValidationMCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Validation MCP Server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
