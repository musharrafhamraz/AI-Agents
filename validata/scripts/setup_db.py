"""Database setup script"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.connection import engine, Base
from backend.core.config import settings


async def create_tables():
    """Create all database tables"""
    print(f"Creating tables in database: {settings.database_url}")
    
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database tables created successfully")


async def main():
    """Main setup function"""
    try:
        await create_tables()
        print("\n✓ Database setup completed successfully!")
    except Exception as e:
        print(f"\n✗ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
