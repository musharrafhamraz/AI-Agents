"""Memory MCP Server - handles memory storage and retrieval"""
import asyncio
import logging
from typing import Any, Dict
import json

from .tools import MemoryTools
from .vector_db import vector_db_client
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryMCPServer:
    """MCP Server for memory management"""
    
    def __init__(self):
        self.tools = MemoryTools()
        self.running = False
    
    async def start(self) -> None:
        """Start the MCP server"""
        try:
            # Connect to vector database
            await vector_db_client.connect()
            
            self.running = True
            logger.info(f"Memory MCP Server started on port {settings.mcp_memory_port}")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start Memory MCP Server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the MCP server"""
        self.running = False
        await vector_db_client.disconnect()
        logger.info("Memory MCP Server stopped")
    
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
            if tool_name == "store_memory":
                result = await self.tools.store_memory(**parameters)
                return self._success_response({"memory_id": result})
            
            elif tool_name == "search_memories":
                result = await self.tools.search_memories(**parameters)
                return self._success_response({"memories": result})
            
            elif tool_name == "get_account_context":
                result = await self.tools.get_account_context(**parameters)
                return self._success_response({"context": result})
            
            elif tool_name == "update_memory":
                result = await self.tools.update_memory(**parameters)
                return self._success_response({"memory": result})
            
            elif tool_name == "delete_memory":
                result = await self.tools.delete_memory(**parameters)
                return self._success_response({"deleted": result})
            
            elif tool_name == "get_memory":
                result = await self.tools.get_memory(**parameters)
                if result:
                    return self._success_response({"memory": result})
                else:
                    return self._error_response("Memory not found", status_code=404)
            
            else:
                return self._error_response(f"Unknown tool: {tool_name}", status_code=400)
        
        except TypeError as e:
            return self._error_response(f"Invalid parameters: {e}", status_code=400)
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
        - memory://{account_id} - Get all memories for account
        - context://{account_id} - Get account context
        """
        try:
            if resource_uri.startswith("memory://"):
                account_id = resource_uri.replace("memory://", "")
                # Get all memories for account (using broad search)
                memories = await self.tools.search_memories(
                    account_id=account_id,
                    query="",
                    limit=100
                )
                return self._success_response({"memories": memories})
            
            elif resource_uri.startswith("context://"):
                account_id = resource_uri.replace("context://", "")
                context = await self.tools.get_account_context(account_id)
                return self._success_response({"context": context})
            
            else:
                return self._error_response(f"Unknown resource: {resource_uri}", status_code=404)
        
        except Exception as e:
            logger.error(f"Error getting resource: {e}")
            return self._error_response(f"Failed to get resource: {e}", status_code=500)


async def main():
    """Main entry point for Memory MCP Server"""
    server = MemoryMCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down Memory MCP Server...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
