from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base

# Database URIs
_main_uri = "postgres:postgres@localhost:5432/postgres"
_sync_uri = f"postgresql://{_main_uri}"
_async_uri = f"postgresql+asyncpg://{_main_uri}"

# Synchronous engine for creating tables
sync_engine = create_engine(_sync_uri)
Base.metadata.create_all(sync_engine)

# Asynchronous engine for main operations
async_engine = create_async_engine(_async_uri, echo=True, future=True)

# AsyncSession factory
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency function to get a database session
async def get_db():
    async with async_session() as session:
        yield session