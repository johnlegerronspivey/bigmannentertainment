"""
PostgreSQL Database Connection Manager
Dual database setup: MongoDB (existing) + PostgreSQL (new for profiles)
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# PostgreSQL connection string from environment
# Format: postgresql+asyncpg://username:password@host:port/database
POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/bigmann_profiles"
)

# Create async engine with timeout settings
async_engine = create_async_engine(
    POSTGRES_URL,
    echo=False,  # Set to True for SQL debugging
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "timeout": 5,  # 5 second connection timeout
        "command_timeout": 5,  # 5 second command timeout
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()

@asynccontextmanager
async def get_async_session():
    """Dependency for getting async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ PostgreSQL database initialized")

async def close_db():
    """Close database connections"""
    await async_engine.dispose()
    print("✅ PostgreSQL database connections closed")
