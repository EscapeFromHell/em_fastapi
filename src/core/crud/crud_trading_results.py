from datetime import date

from fastapi.exceptions import HTTPException
from sqlalchemy import and_, desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crud import CRUDBase
from src.core.models import SpimexTradingResults
from src.core.schemas import SpimexTradingResultsCreate, SpimexTradingResultsUpdate


class CRUDSpimexTradingResults(CRUDBase[SpimexTradingResults, SpimexTradingResultsCreate, SpimexTradingResultsUpdate]):
    def __add_filters_to_query(self, query, oil_id, delivery_type_id, delivery_basis_id):
        """
        Добавляет фильтры к заданному запросу SQLAlchemy на основе предоставленных параметров.

        Args:
            query (SQLAlchemy Query): Запрос SQLAlchemy, к которому нужно добавить фильтры.
            oil_id (str | None): Идентификатор нефти для фильтрации.
            delivery_type_id (str | None): Идентификатор типа доставки для фильтрации.
            delivery_basis_id (str | None): Идентификатор базиса поставки для фильтрации.

        Returns:
            SQLAlchemy Query: Измененный запрос с добавленными фильтрами.
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
        Добавляет список объектов SpimexTradingResults в сеанс базы данных.

        Args:
            db (AsyncSession): Сеанс базы данных для добавления объектов.
            objects (list[SpimexTradingResults]): Список объектов SpimexTradingResults для добавления.

        Returns:
            None
        """
        async with db.begin():
            db.add_all(objects)

    async def fetch_one_trading_result_by_date(self, db: AsyncSession, date: date) -> SpimexTradingResults | None:
        """
        Получает один объект SpimexTradingResults из базы данных по его дате.

        Args:
            db (AsyncSession): Сеанс базы данных для получения объекта.
            date (date): Дата торгового результата для получения.

        Returns:
            SpimexTradingResults | None: Полученный объект SpimexTradingResults или None, если не найден.
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
        Получает последние результаты торгов из базы данных,
        при необходимости фильтруемые по oil_id, delivery_type_id и delivery_basis_id.

        Args:
            db (AsyncSession): Сеанс базы данных для получения результатов.
            oil_id (str | None): Идентификатор нефти для фильтрации.
            delivery_type_id (str | None): Идентификатор типа доставки для фильтрации.
            delivery_basis_id (str | None): Идентификатор базиса поставки для фильтрации.

        Returns:
            list[SpimexTradingResults]: Полученный список объектов SpimexTradingResults.
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
        delivery_basis_id: str | None,
    ) -> list[SpimexTradingResults]:
        """
        Получает результаты торгов из базы данных в указанном диапазоне дат,
        при необходимости фильтруемые по oil_id, delivery_type_id и delivery_basis_id.

        Args:
            start_date (date): Начальная дата диапазона.
            end_date (date): Конечная дата диапазона.
            db (AsyncSession): Сеанс базы данных для получения результатов.
            oil_id (str | None): Идентификатор нефти для фильтрации.
            delivery_type_id (str | None): Идентификатор типа доставки для фильтрации.
            delivery_basis_id (str | None): Идентификатор базиса поставки для фильтрации.

        Returns:
            list[SpimexTradingResults]: Полученный список объектов SpimexTradingResults в указанном диапазоне дат.
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
