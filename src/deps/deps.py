from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.core.clients import SpimexClient
from src.core.db import async_session
from src.core.repository import TradingResultsRepo


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def trading_results_repo(db: Session = Depends(get_session, use_cache=False)) -> TradingResultsRepo:
    return TradingResultsRepo(db=db)


def spimex_client() -> SpimexClient:
    return SpimexClient()
