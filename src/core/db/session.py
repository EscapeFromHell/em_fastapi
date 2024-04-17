from __future__ import annotations

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings

url = settings.DRIVER + settings.USER + settings.PASSWORD + settings.HOST + settings.PORT + settings.NAME

engine = create_async_engine(url=url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
