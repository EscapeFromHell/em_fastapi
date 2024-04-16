import sqlalchemy.orm as so
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, so.DeclarativeBase):
    pass
