"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from loguru import logger
import asyncio
from typing import AsyncGenerator

from .base import Base, SessionLocal
from ..config.settings import get_settings

# Initialize settings
settings = get_settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# Configure session maker
SessionLocal.configure(bind=engine)


async def init_database():
    """
    Initialize database tables
    """
    try:
        logger.info("Initializing database...")
        
        # Import all models to ensure they are registered
        from ..models import User, Image, Layout, LayoutElement, OCRResult
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db_session():
    """
    Get database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db_session() -> AsyncGenerator:
    """
    Get async database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """
    Database manager for handling connections and transactions
    """
    
    def __init__(self):
        self.engine = engine
        self.session_maker = SessionLocal
    
    def get_session(self):
        """Get a new database session"""
        return self.session_maker()
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
    
    def reset_database(self):
        """Reset database by dropping and recreating tables"""
        self.drop_tables()
        self.create_tables()
    
    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager() 