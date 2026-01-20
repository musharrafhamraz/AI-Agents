"""Analytics MCP Server - handles insights and analytics generation"""
import asyncio
import logging
from typing import Any, Dict
from uuid import UUID

from .tools import AnalyticsTools
from backend.database.connection import db_manager
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsMCPServer:
    """MCP Server for analytics and insights"""
    
    def __init__(self):
        self.tools = AnalyticsTools()
        self.running = False
    
    async def start(self) -> None:
        """Start the MCP server"""
        try:
            # Connect to database
            await db_manager.connect()
            
            self.running = True
            logger.info(f"Analytics MCP Server started on port {settings.mcp_analytics_port}")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start Analytics MCP Server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server"""
        self.running = False
        await db_manager.disconnect()
        logger.info("Analytics MCP Server stopped")
    
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
            if tool_name == "generate_insights":
                survey_id = UUID(parameters["survey_id"])
                account_context = parameters.get("account_context")
                
                insights = await self.tools.generate_insights(survey_id, account_context)
                return self._success_response({
                    "insights": [i.model_dump() for i in insights]
                })
            
            elif tool_name == "aggregate_responses":
                survey_id = UUID(parameters["survey_id"])
                filters = parameters.get("filters", {})
                
                aggregated = await self.tools.aggregate_responses(survey_id, filters)
                return self._success_response({
                    "aggregated_data": aggregated.model_dump()
                })
            
            elif tool_name == "detect_patterns":
                survey_id = UUID(parameters["survey_id"])
                
                patterns = await self.tools.detect_patterns(survey_id)
                return self._success_response({
                    "patterns": [p.model_dump() for p in patterns]
                })
            
            elif tool_name == "get_insight_trace":
                insight_id = UUID(parameters["insight_id"])
                
                trace = await self.tools.get_insight_trace(insight_id)
                return self._success_response({"trace": trace})
            
            elif tool_name == "get_insights":
                survey_id = UUID(parameters["survey_id"])
                
                insights = await self.tools.get_insights_for_survey(survey_id)
                return self._success_response({
                    "insights": [i.model_dump() for i in insights]
                })
            
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
        - insights://{survey_id} - Get insights for survey
        - patterns://{survey_id} - Get patterns for survey
        """
        try:
            if resource_uri.startswith("insights://"):
                survey_id_str = resource_uri.replace("insights://", "")
                survey_id = UUID(survey_id_str)
                
                insights = await self.tools.get_insights_for_survey(survey_id)
                return self._success_response({
                    "insights": [i.model_dump() for i in insights]
                })
            
            elif resource_uri.startswith("patterns://"):
                survey_id_str = resource_uri.replace("patterns://", "")
                survey_id = UUID(survey_id_str)
                
                patterns = await self.tools.detect_patterns(survey_id)
                return self._success_response({
                    "patterns": [p.model_dump() for p in patterns]
                })
            
            else:
                return self._error_response(f"Unknown resource: {resource_uri}", status_code=404)
        
        except Exception as e:
            logger.error(f"Error getting resource: {e}")
            return self._error_response(f"Failed to get resource: {e}", status_code=500)


async def main():
    """Main entry point for Analytics MCP Server"""
    server = AnalyticsMCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Analytics MCP Server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
