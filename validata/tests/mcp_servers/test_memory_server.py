"""Tests for Memory MCP Server"""
import pytest
from uuid import uuid4

from mcp_servers.memory.server import MemoryMCPServer


@pytest.fixture
async def memory_server():
    """Create memory server instance"""
    server = MemoryMCPServer()
    yield server


@pytest.mark.asyncio
async def test_store_memory(memory_server):
    """Test storing a memory"""
    request = {
        "tool": "store_memory",
        "parameters": {
            "account_id": "test_account",
            "content": "Test memory content",
            "metadata": {"type": "test"}
        }
    }
    
    response = await memory_server.handle_request(request)
    
    assert response["status"] == "success"
    assert "memory_id" in response["data"]


@pytest.mark.asyncio
async def test_search_memories(memory_server):
    """Test searching memories"""
    # First store a memory
    store_request = {
        "tool": "store_memory",
        "parameters": {
            "account_id": "test_account",
            "content": "Important survey about customer satisfaction",
            "metadata": {"type": "survey"}
        }
    }
    await memory_server.handle_request(store_request)
    
    # Then search for it
    search_request = {
        "tool": "search_memories",
        "parameters": {
            "account_id": "test_account",
            "query": "customer satisfaction",
            "limit": 10
        }
    }
    
    response = await memory_server.handle_request(search_request)
    
    assert response["status"] == "success"
    assert "memories" in response["data"]


@pytest.mark.asyncio
async def test_get_account_context(memory_server):
    """Test getting account context"""
    request = {
        "tool": "get_account_context",
        "parameters": {
            "account_id": "test_account"
        }
    }
    
    response = await memory_server.handle_request(request)
    
    assert response["status"] == "success"
    assert "context" in response["data"]
    assert "account_id" in response["data"]["context"]


@pytest.mark.asyncio
async def test_invalid_tool(memory_server):
    """Test handling invalid tool name"""
    request = {
        "tool": "invalid_tool",
        "parameters": {}
    }
    
    response = await memory_server.handle_request(request)
    
    assert response["status"] == "error"
    assert "Unknown tool" in response["error"]["message"]
