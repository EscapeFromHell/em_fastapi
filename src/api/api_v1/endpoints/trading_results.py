from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache

from src.config import settings
from src.core.clients import SpimexClient
from src.core.repository import TradingResultsRepo
from src.core.schemas import LastTradingDates, SuccessResponseMessage, TradingResultsList
from src.deps import spimex_client as deps_spimex_client
from src.deps import trading_results_repo as deps_trading_results_repo

router = APIRouter()


@router.get("/", status_code=200, response_model=SuccessResponseMessage)
async def get_spimex_trading_results(
    *,
    target_date: date,
    repo: TradingResultsRepo = Depends(deps_trading_results_repo),
    spimex_client: SpimexClient = Depends(deps_spimex_client),
) -> SuccessResponseMessage:
    """
    Получает и записывает в БД результаты торгов до указанной целевой даты с использованием SpimexClient.

    Args:
        target_date (date): Целевая дата, для которой запрашиваются результаты торгов.
        repo (TradingResultsRepo, optional): Зависимость от TradingResultsRepo для доступа к базе данных.
        spimex_client (SpimexClient, optional): Зависимость от SpimexClient для доступа к API Spimex.

    Returns:
        SuccessResponseMessage: Объект SuccessResponseMessage, указывающий на успешное получение результатов торгов.
    """
    return await repo.get_spimex_trading_results(target_data=target_date, spimex_client=spimex_client)


@router.get("/last_trading_dates", status_code=200, response_model=LastTradingDates)
@cache(expire=settings.REDIS_EXPIRATION_TIME)
async def get_last_trading_dates(
    days: int, repo: TradingResultsRepo = Depends(deps_trading_results_repo)
) -> LastTradingDates:
    """
    Получает список дат за указанный период, по которым есть результаты торгов в базе данных.

    Args:
        days (int): Количество дней.
        repo (TradingResultsRepo, optional): Зависимость от TradingResultsRepo для доступа к базе данных.

    Returns:
        LastTradingDates: Список дат, по которым есть результаты торгов.
    """
    return await repo.get_last_trading_dates(days)


@router.get("/trading_results_in_period", status_code=200, response_model=TradingResultsList)
@cache(expire=settings.REDIS_EXPIRATION_TIME)
async def get_dynamics(
    start_date: date,
    end_date: date,
    oil_id: Optional[str] = None,
    delivery_type_id: Optional[str] = None,
    delivery_basis_id: Optional[str] = None,
    repo: TradingResultsRepo = Depends(deps_trading_results_repo),
) -> TradingResultsList:
    """
    Получает результаты торгов за указанный период из базы данных.

    Args:
        start_date (date): Начальная дата, для которой запрашиваются результаты торгов.
        end_date (date): Конечная дата, для которой запрашиваются результаты торгов.
        oil_id (Optional[str]): Параметр для фильтрации результатов по идентификатору нефти.
        delivery_type_id (Optional[str]): Параметр для фильтрации результатов по идентификатору типа доставки.
        delivery_basis_id (Optional[str]): Параметр для фильтрации результатов по идентификатору базиса поставки.
        repo (TradingResultsRepo, optional): Зависимость от TradingResultsRepo для доступа к базе данных.

    Returns:
        TradingResultsList: Список результатов торгов за период, отфильтрованный по предоставленным параметрам.
    """
    return await repo.get_trading_results_in_period(
        start_date=start_date,
        end_date=end_date,
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )


@router.get("/last_trading_results", status_code=200, response_model=TradingResultsList)
@cache(expire=settings.REDIS_EXPIRATION_TIME)
async def get_trading_results(
    *,
    oil_id: Optional[str] = None,
    delivery_type_id: Optional[str] = None,
    delivery_basis_id: Optional[str] = None,
    repo: TradingResultsRepo = Depends(deps_trading_results_repo),
) -> TradingResultsList:
    """
    Получает последние результаты торгов из базы данных.

    Args:
        oil_id (Optional[str]): Параметр для фильтрации результатов по идентификатору нефти.
        delivery_type_id (Optional[str]): Параметр для фильтрации результатов по идентификатору типа доставки.
        delivery_basis_id (Optional[str]): Параметр для фильтрации результатов по идентификатору базиса поставки.
        repo (TradingResultsRepo, optional): Зависимость от TradingResultsRepo для доступа к базе данных.

    Returns:
        TradingResultsList: Список результатов последних торгов, отфильтрованный по предоставленным параметрам.
    """
    return await repo.get_last_trading_results(
        oil_id=oil_id, delivery_type_id=delivery_type_id, delivery_basis_id=delivery_basis_id
    )
