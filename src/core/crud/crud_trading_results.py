from datetime import date

from fastapi.exceptions import HTTPException
from sqlalchemy import and_, desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crud import CRUDBase
from src.core.models import SpimexTradingResults
from src.core.schemas import SpimexTradingResultsCreate, SpimexTradingResultsUpdate


class CRUDSpimexTradingResults(CRUDBase[SpimexTradingResults, SpimexTradingResultsCreate, SpimexTradingResultsUpdate]):
    """Custom CRUD operations for the SpimexTradingResults model."""
    def __add_filters_to_query(self, query, oil_id, delivery_type_id, delivery_basis_id):
        """
        Adds filters to the given SQLAlchemy query based on the provided parameters.

        Args:
            query (SQLAlchemy Query): The SQLAlchemy query to add filters to.
            oil_id (str | None): The ID of the oil to filter by.
            delivery_type_id (str | None): The ID of the delivery type to filter by.
            delivery_basis_id (str | None): The ID of the delivery basis to filter by.

        Returns:
            SQLAlchemy Query: The modified query with added filters.
        """
        if oil_id:
            query = query.filter(SpimexTradingResults.oil_id == oil_id)
        if delivery_type_id:
            query = query.filter(SpimexTradingResults.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            query = query.filter(SpimexTradingResults.delivery_basis_id == delivery_basis_id)
        return query

    async def add_to_db(self, db: AsyncSession, objects: list[SpimexTradingResults]) -> None:
        """
        Adds the given list of SpimexTradingResults objects to the database session.

        Args:
            db (AsyncSession): The database session to add the objects to.
            objects (list[SpimexTradingResults]): The list of SpimexTradingResults objects to add.

        Returns:
            None
        """
        db.add_all(objects)

    async def fetch_one_trading_result_by_date(self, db: AsyncSession, date: date) -> SpimexTradingResults | None:
        """
        Fetches a single SpimexTradingResults object from the database by its date.

        Args:
            db (AsyncSession): The database session to fetch the object from.
            date (date): The date of the trading result to fetch.

        Returns:
            SpimexTradingResults | None: The fetched SpimexTradingResults object, or None if not found.
        """
        query = await db.execute(select(SpimexTradingResults).filter_by(date=date).limit(1))
        try:
            result = query.scalars().one()
            return result
        except NoResultFound:
            return None

    async def get_last_results(
            self, db: AsyncSession, oil_id: str | None, delivery_type_id: str | None, delivery_basis_id: str | None
    ) -> list[SpimexTradingResults]:
        """
        Fetches the last trading results from the database,
        optionally filtered by oil_id, delivery_type_id, and delivery_basis_id.

        Args:
            db (AsyncSession): The database session to fetch the results from.
            oil_id (str | None): The ID of the oil to filter by.
            delivery_type_id (str | None): The ID of the delivery type to filter by.
            delivery_basis_id (str | None): The ID of the delivery basis to filter by.

        Returns:
            list[SpimexTradingResults]: The fetched list of SpimexTradingResults objects.
        """
        query = await db.execute(select(SpimexTradingResults.date.distinct()).order_by(desc(SpimexTradingResults.date)))
        dates = query.scalars().all()

        if not dates:
            raise HTTPException(status_code=404, detail="Database is empty!")

        last_date = dates[0]
        base_query = select(SpimexTradingResults).filter(SpimexTradingResults.date == last_date)
        base_query = self.__add_filters_to_query(
            query=base_query, oil_id=oil_id, delivery_type_id=delivery_type_id, delivery_basis_id=delivery_basis_id
        )

        query = await db.execute(base_query)
        results = query.scalars().all()
        return list(results)

    async def get_trading_results_in_period(
            self,
            start_date: date,
            end_date: date,
            db: AsyncSession,
            oil_id: str | None,
            delivery_type_id: str | None,
            delivery_basis_id: str | None
    ) -> list[SpimexTradingResults]:
        """
        Fetches the trading results from the database within the specified date range,
        optionally filtered by oil_id, delivery_type_id, and delivery_basis_id.

        Args:
            start_date (date): The start date of the date range.
            end_date (date): The end date of the date range.
            db (AsyncSession): The database session to fetch the results from.
            oil_id (str | None): The ID of the oil to filter by.
            delivery_type_id (str | None): The ID of the delivery type to filter by.
            delivery_basis_id (str | None): The ID of the delivery basis to filter by.

        Returns:
            list[SpimexTradingResults]: The fetched list of SpimexTradingResults objects
            within the specified date range.
        """
        base_query = select(SpimexTradingResults).filter(
            and_(SpimexTradingResults.date >= start_date, SpimexTradingResults.date <= end_date)
        )
        base_query = self.__add_filters_to_query(
            query=base_query, oil_id=oil_id, delivery_type_id=delivery_type_id, delivery_basis_id=delivery_basis_id
        )

        query = await db.execute(base_query)
        results = query.scalars().all()
        return list(results)


crud_trading_results = CRUDSpimexTradingResults(SpimexTradingResults)
