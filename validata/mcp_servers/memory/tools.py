"""Memory MCP Server tools for storage and retrieval"""
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime

from .vector_db import vector_db_client

logger = logging.getLogger(__name__)


class MemoryTools:
    """Tools for memory management"""
    
    @staticmethod
    async def store_memory(
        account_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a new memory in the vector database
        
        Args:
            account_id: Account identifier
            content: Memory content text
            metadata: Additional metadata (survey_id, timestamp, type, etc.)
        
        Returns:
            memory_id: Unique identifier for the stored memory
        """
        try:
            memory_id = str(uuid4())
            
            # Prepare metadata
            full_metadata = {
                "account_id": account_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Store in vector database
            await vector_db_client.upsert_memory(memory_id, content, full_metadata)
            
            logger.info(f"Memory stored: {memory_id} for account {account_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    @staticmethod
    async def search_memories(
        account_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for memories using semantic search
        
        Args:
            account_id: Account identifier
            query: Search query text
            limit: Maximum number of results
        
        Returns:
            List of matching memories with scores
        """
        try:
            memories = await vector_db_client.search_memories(
                account_id=account_id,
                query=query,
                limit=limit
            )
            
            logger.info(f"Found {len(memories)} memories for account {account_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    @staticmethod
    async def get_account_context(account_id: str) -> Dict[str, Any]:
        """
        Retrieve aggregated context for an account
        
        Args:
            account_id: Account identifier
        
        Returns:
            Account context including stats and recent memories
        """
        try:
            # Get account statistics
            stats = await vector_db_client.get_account_stats(account_id)
            
            # Get recent memories (using a broad query)
            recent_memories = await vector_db_client.search_memories(
                account_id=account_id,
                query="recent activity patterns insights",
                limit=20
            )
            
            # Aggregate context
            context = {
                "account_id": account_id,
                "total_memories": stats["total_memories"],
                "recent_memories": recent_memories[:10],  # Top 10 most relevant
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved context for account {account_id}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get account context: {e}")
            raise
    
    @staticmethod
    async def update_memory(
        memory_id: str,
        account_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing memory
        
        Args:
            memory_id: Memory identifier
            account_id: Account identifier
            content: Updated content
            metadata: Updated metadata
        
        Returns:
            Updated memory information
        """
        try:
            # Prepare metadata
            full_metadata = {
                "account_id": account_id,
                "content": content,
                "updated_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            
            # Update in vector database
            await vector_db_client.update_memory(
                memory_id=memory_id,
                account_id=account_id,
                content=content,
                metadata=full_metadata
            )
            
            logger.info(f"Memory updated: {memory_id}")
            return {
                "memory_id": memory_id,
                "account_id": account_id,
                "updated_at": full_metadata["updated_at"]
            }
            
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            raise
    
    @staticmethod
    async def delete_memory(memory_id: str, account_id: str) -> bool:
        """
        Delete a memory
        
        Args:
            memory_id: Memory identifier
            account_id: Account identifier
        
        Returns:
            True if deleted successfully
        """
        try:
            await vector_db_client.delete_memory(memory_id, account_id)
            logger.info(f"Memory deleted: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise
    
    @staticmethod
    async def get_memory(memory_id: str, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID
        
        Args:
            memory_id: Memory identifier
            account_id: Account identifier
        
        Returns:
            Memory data or None if not found
        """
        try:
            memory = await vector_db_client.get_memory(memory_id, account_id)
            if memory:
                logger.info(f"Memory retrieved: {memory_id}")
            else:
                logger.warning(f"Memory not found: {memory_id}")
            return memory
        except Exception as e:
            logger.error(f"Failed to get memory: {e}")
            raise
