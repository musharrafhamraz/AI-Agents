"""Vector database client for memory storage and retrieval"""
import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import openai

from backend.core.config import settings

logger = logging.getLogger(__name__)


class VectorDBClient:
    """Client for interacting with Pinecone vector database"""
    
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.dimension = 1536  # OpenAI embedding dimension
        self.openai_client = None
    
    async def connect(self) -> None:
        """Initialize connection to Pinecone and OpenAI"""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Check if index exists, create if not
            index_name = settings.pinecone_index_name
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            
            # Initialize OpenAI client
            self.openai_client = openai.AsyncOpenAI(
                api_key=settings.openai_api_key,
                organization=settings.openai_org_id
            )
            
            logger.info("Vector database connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to vector database: {e}")
            raise RuntimeError(f"Vector database connection failed: {e}") from e
    
    async def disconnect(self) -> None:
        """Close vector database connection"""
        self.index = None
        self.pc = None
        self.openai_client = None
        logger.info("Vector database connection closed")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def upsert_memory(
        self,
        memory_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Store a memory in the vector database"""
        if not self.index:
            raise RuntimeError("Vector database not connected")
        
        try:
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(memory_id, embedding, metadata)],
                namespace=metadata.get("account_id", "default")
            )
            
            logger.debug(f"Memory {memory_id} stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def search_memories(
        self,
        account_id: str,
        query: str,
        limit: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar memories using semantic search"""
        if not self.index:
            raise RuntimeError("Vector database not connected")
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                namespace=account_id,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Format results
            memories = []
            for match in results.matches:
                memories.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            logger.debug(f"Found {len(memories)} memories for query")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    async def get_memory(self, memory_id: str, account_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID"""
        if not self.index:
            raise RuntimeError("Vector database not connected")
        
        try:
            result = self.index.fetch(ids=[memory_id], namespace=account_id)
            
            if memory_id in result.vectors:
                vector_data = result.vectors[memory_id]
                return {
                    "id": memory_id,
                    "metadata": vector_data.metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            raise
    
    async def update_memory(
        self,
        memory_id: str,
        account_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update an existing memory"""
        # Pinecone upsert handles both insert and update
        await self.upsert_memory(memory_id, content, {**metadata, "account_id": account_id})
    
    async def delete_memory(self, memory_id: str, account_id: str) -> None:
        """Delete a memory from the vector database"""
        if not self.index:
            raise RuntimeError("Vector database not connected")
        
        try:
            self.index.delete(ids=[memory_id], namespace=account_id)
            logger.debug(f"Memory {memory_id} deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise
    
    async def get_account_stats(self, account_id: str) -> Dict[str, Any]:
        """Get statistics for an account's memories"""
        if not self.index:
            raise RuntimeError("Vector database not connected")
        
        try:
            stats = self.index.describe_index_stats()
            namespace_stats = stats.namespaces.get(account_id, {})
            
            return {
                "account_id": account_id,
                "total_memories": namespace_stats.get("vector_count", 0),
                "dimension": self.dimension
            }
        except Exception as e:
            logger.error(f"Failed to get account stats: {e}")
            raise


# Global vector DB client instance
vector_db_client = VectorDBClient()
