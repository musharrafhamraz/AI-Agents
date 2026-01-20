"""Database connection management with async support"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()


class DatabaseConnectionManager:
    """Manages database connections with retry logic and connection pooling"""
    
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._max_retries = 3
        self._retry_delay = 1.0  # seconds
    
    def _create_engine(self) -> AsyncEngine:
        """Create async database engine with connection pooling"""
        # Convert postgresql:// to postgresql+asyncpg://
        database_url = settings.database_url
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Configure connection pool
        pool_class = QueuePool if settings.environment == "production" else NullPool
        
        engine = create_async_engine(
            database_url,
            poolclass=pool_class,
            pool_size=settings.database_pool_size if pool_class == QueuePool else 0,
            max_overflow=10 if pool_class == QueuePool else 0,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.debug,  # Log SQL queries in debug mode
        )
        
        # Add connection event listeners
        @event.listens_for(engine.sync_engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Log successful connections"""
            logger.debug("Database connection established")
        
        @event.listens_for(engine.sync_engine, "close")
        def receive_close(dbapi_conn, connection_record):
            """Log connection closures"""
            logger.debug("Database connection closed")
        
        return engine
    
    async def connect(self) -> None:
        """Initialize database connection with retry logic"""
        for attempt in range(self._max_retries):
            try:
                self._engine = self._create_engine()
                
                # Test connection
                async with self._engine.begin() as conn:
                    await conn.execute("SELECT 1")
                
                # Create session factory
                self._session_factory = async_sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False,
                )
                
                logger.info("Database connection established successfully")
                return
                
            except Exception as e:
                logger.warning(
                    f"Database connection attempt {attempt + 1}/{self._max_retries} failed: {e}"
                )
                
                if attempt < self._max_retries - 1:
                    # Exponential backoff
                    delay = self._retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Failed to connect to database after all retries")
                    raise RuntimeError(
                        f"Could not connect to database after {self._max_retries} attempts: {e}"
                    ) from e
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a transactional scope for database operations
        
        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)
                await session.commit()
        """
        if not self._session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine"""
        if not self._engine:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._engine


# Global database manager instance
db_manager = DatabaseConnectionManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with db_manager.session() as session:
        yield session


# Convenience exports
engine = db_manager.engine
get_session = get_db_session
