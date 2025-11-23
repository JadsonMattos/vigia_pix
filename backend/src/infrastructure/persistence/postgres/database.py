"""Database configuration and session management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from typing import AsyncGenerator

# Get DATABASE_URL from environment, with fallback
# Try to detect if running inside Docker or locally
def get_database_url():
    """Get database URL, detecting environment"""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Check if running inside Docker (check if 'postgres' hostname resolves)
    # If not, use localhost
    import socket
    try:
        socket.gethostbyname('postgres')
        # Inside Docker, use postgres hostname
        return "postgresql+asyncpg://postgres:postgres@postgres:5432/voz_cidada"
    except socket.gaierror:
        # Outside Docker, use localhost
        return "postgresql+asyncpg://postgres:postgres@localhost:5432/voz_cidada"

DATABASE_URL = get_database_url()

# Base class for models (must be defined before engine)
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    from src.infrastructure.persistence.postgres.models import legislation, emenda_pix, user_preferences, emenda_history
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

