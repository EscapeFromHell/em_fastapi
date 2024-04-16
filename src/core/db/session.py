from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.models import Base

DATABASE_DSN: str = "postgresql+asyncpg://postgres:password@spimex-fastapi-db:5432/spimex-fastapi"

engine = create_async_engine(url=DATABASE_DSN, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_metadata() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
