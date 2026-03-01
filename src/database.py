import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# O default pega de variáveis ambiente; o replace ajusta a URL sincrona para async
raw_url = os.getenv("DATABASE_URL", "postgresql://hana_admin:c0c1164a842da069a9a9@hana-db:5432/hana_intel")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
if raw_url.startswith("postgresql://"):
    database_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    database_url = raw_url

# Cria a engine assíncrona.
# Em modo read-only, garantimos que transações não farão write a menos que permitido.
try:
    engine = create_async_engine(
        database_url, 
        echo=False, 
        future=True, 
        pool_size=10, 
        max_overflow=20
    )
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    logger.info("✅ Async Database Engine initialized.")
except Exception as e:
    logger.error(f"❌ Failed to initialize database engine: {e}")
    engine = None
    async_session_maker = None

Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session."""
    if not async_session_maker:
        raise Exception("Database engine is not initialized.")
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
