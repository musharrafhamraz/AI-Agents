"""Survey MCP Server - handles survey creation and management"""
import asyncio
import logging
from typing import Any, Dict
from uuid import UUID

from .tools import SurveyTools
from .resources import SurveyResources
from backend.database.connection import db_manager
from backend.core.config import settings
from backend.models.survey import SurveyCreate, SurveyUpdate, Question

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SurveyMCPServer:
    """MCP Server for survey management"""
    
    def __init__(self):
        self.tools = SurveyTools()
        self.resources = SurveyResources()
        self.running = False
    
    async def start(self) -> None:
        """Start the MCP server"""
        try:
            # Connect to database
            await db_manager.connect()
            
            self.running = True
            logger.info(f"Survey MCP Server started on port {settings.mcp_survey_port}")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start Survey MCP Server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server"""
        self.running = False
        await db_manager.disconnect()
        logger.info("Survey MCP Server stopped")
    
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
            if tool_name == "create_survey":
                # Generate questions if topic provided
                topic = parameters.get("topic")
                account_id = parameters.get("account_id")
                account_context = parameters.get("account_context")
                
                if topic:
                    questions = await self.tools.generate_questions(
                        topic=topic,
                        account_context=account_context
                    )
                    
                    # Create survey with generated questions
                    survey_data = SurveyCreate(
                        account_id=account_id,
                        title=f"Survey: {topic}",
                        description=f"Survey about {topic}",
                        questions=questions
                    )
                else:
                    # Create survey with provided data
                    survey_data = SurveyCreate(**parameters)
                
                survey = await self.resources.create_survey(survey_data)
                return self._success_response({"survey": survey.model_dump()})
            
            elif tool_name == "get_survey":
                survey_id = UUID(parameters["survey_id"])
                survey = await self.resources.get_survey(survey_id)
                
                if survey:
                    return self._success_response({"survey": survey.model_dump()})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif tool_name == "list_templates":
                templates = self.tools.list_templates()
                return self._success_response({
                    "templates": [t.model_dump() for t in templates]
                })
            
            elif tool_name == "add_question":
                survey_id = UUID(parameters["survey_id"])
                question = Question(**parameters["question"])
                survey = await self.resources.add_question(survey_id, question)
                
                if survey:
                    return self._success_response({"survey": survey.model_dump()})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif tool_name == "update_question":
                survey_id = UUID(parameters["survey_id"])
                question_id = parameters["question_id"]
                question = Question(**parameters["question"])
                survey = await self.resources.update_question(survey_id, question_id, question)
                
                if survey:
                    return self._success_response({"survey": survey.model_dump()})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif tool_name == "update_survey":
                survey_id = UUID(parameters["survey_id"])
                update_data = SurveyUpdate(**parameters.get("update_data", {}))
                survey = await self.resources.update_survey(survey_id, update_data)
                
                if survey:
                    return self._success_response({"survey": survey.model_dump()})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif tool_name == "delete_survey":
                survey_id = UUID(parameters["survey_id"])
                deleted = await self.resources.delete_survey(survey_id)
                
                if deleted:
                    return self._success_response({"deleted": True})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif tool_name == "list_surveys":
                surveys = await self.resources.list_surveys(**parameters)
                return self._success_response({
                    "surveys": [s.model_dump() for s in surveys]
                })
            
            else:
                return self._error_response(f"Unknown tool: {tool_name}", status_code=400)
        
        except TypeError as e:
            return self._error_response(f"Invalid parameters: {e}", status_code=400)
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
        - survey://{survey_id} - Get specific survey
        - templates:// - Get all templates
        """
        try:
            if resource_uri.startswith("survey://"):
                survey_id_str = resource_uri.replace("survey://", "")
                survey_id = UUID(survey_id_str)
                survey = await self.resources.get_survey(survey_id)
                
                if survey:
                    return self._success_response({"survey": survey.model_dump()})
                else:
                    return self._error_response("Survey not found", status_code=404)
            
            elif resource_uri == "templates://":
                templates = self.tools.list_templates()
                return self._success_response({
                    "templates": [t.model_dump() for t in templates]
                })
            
            else:
                return self._error_response(f"Unknown resource: {resource_uri}", status_code=404)
        
        except Exception as e:
            logger.error(f"Error getting resource: {e}")
            return self._error_response(f"Failed to get resource: {e}", status_code=500)


async def main():
    """Main entry point for Survey MCP Server"""
    server = SurveyMCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Survey MCP Server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
