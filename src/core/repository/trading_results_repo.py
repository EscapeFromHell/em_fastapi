import logging
import os
from datetime import date, datetime, timedelta
from typing import Generator

import pandas as pd
from fastapi import HTTPException

from src.core.clients import SpimexClient
from src.core.crud import crud_trading_results
from src.core.models import SpimexTradingResults
from src.core.repository.repository import Repository
from src.core.schemas import LastTradingDates, SuccessResponseMessage, TradingResultsList
from src.utils import get_logger

logger = get_logger(__file__, logging.DEBUG)


class TradingResultsRepo(Repository):
    def __init__(self, db) -> None:
        super().__init__(db)
        self.target_date: date | None = None
        self.date_list: list | None = None

    def __remove_excel(self) -> None:
        for str_date in self.date_list:
            if os.path.exists(f"{str_date}_oil_data.xls"):
                os.remove(f"{str_date}_oil_data.xls")

    def __prepare_date_list(self) -> list[str]:
        date_list = []
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        while current_date >= self.target_date:
            str_date = str(current_date).replace("-", "")
            date_list.append(str_date)
            current_date -= timedelta(days=1)
        return date_list

    async def __check_date(self, str_date: date) -> bool:
        result = await crud_trading_results.fetch_one_trading_result_by_date(db=self.db, date=str_date)
        return True if result else False

    def __get_dates_for_period(self, days: int):
        date_list = []
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        for i in range(days):
            date_list.append(current_date)
            current_date -= timedelta(days=1)
        return date_list

    def __get_data_from_excel(self) -> Generator[tuple[list, str], None, None]:
        for str_date in self.date_list:
            if os.path.exists(f"{str_date}_oil_data.xls"):
                df = pd.read_excel(f"{str_date}_oil_data.xls")
                target = 0
                for index, row in df.iterrows():
                    try:
                        if "Единица измерения: Метрическая тонна" in row.iloc[1]:
                            target = index
                            break
                    except TypeError:
                        pass
                df = df.iloc[target + 2:]
                df = df.iloc[:-2, [1, 2, 3, 4, 5, -1]]
                df = df.replace("-", 0)
                df = df.fillna(0)
                result = df[df.iloc[:, -1].astype(int) > 0]
                for index, row in result.iterrows():
                    yield row.tolist(), str_date

    def __prepare_objects(self) -> list[SpimexTradingResults]:
        objects = []
        for data, str_date in self.__get_data_from_excel():
            trading_result = SpimexTradingResults(
                exchange_product_id=str(data[0]),
                exchange_product_name=str(data[1]),
                oil_id=str(data[0][:4]),
                delivery_basis_id=str(data[0][4:7]),
                delivery_basis_name=str(data[2]),
                delivery_type_id=str(data[0][-1]),
                volume=str(data[3]),
                total=str(data[4]),
                count=str(data[5]),
                date=datetime.strptime(str_date, "%Y%m%d").date()
            )
            objects.append(trading_result)
        return objects

    async def get_spimex_trading_results(
            self, target_data: date, spimex_client: SpimexClient
    ) -> SuccessResponseMessage:
        try:
            logger.info("Выполнение...")
            self.target_date = target_data
            self.date_list = self.__prepare_date_list()
            await spimex_client.download_spimex_bulletins(date_list=self.date_list)
            objects = self.__prepare_objects()
            await crud_trading_results.add_to_db(db=self.db, objects=objects)
            self.__remove_excel()

        except Exception as error:
            logger.error(f"Возникла ошибка при выполнении! {error}")
            raise HTTPException(status_code=400, detail="Возникла ошибка при выполнении!")

        else:
            logger.info("Выполнение завершено!")
            return SuccessResponseMessage(response_message="Выполнение завершено!")

    async def get_last_trading_dates(self, days: int) -> LastTradingDates:
        result = []
        dates = self.__get_dates_for_period(days=days)
        for str_date in dates:
            check = await self.__check_date(str_date=str_date)
            if check:
                result.append(str_date)
        return LastTradingDates(last_trading_dates=result)

    async def get_last_trading_results(
            self, oil_id: str | None, delivery_type_id: str | None, delivery_basis_id: str | None
    ) -> TradingResultsList:
        result = await crud_trading_results.get_last_results(
            db=self.db, oil_id=oil_id, delivery_type_id=delivery_type_id, delivery_basis_id=delivery_basis_id
        )
        return TradingResultsList(trading_results=result)

    async def get_trading_results_in_period(
            self,
            start_date: date,
            end_date: date,
            oil_id: str | None,
            delivery_type_id: str | None,
            delivery_basis_id: str | None
    ) -> TradingResultsList:
        result = await crud_trading_results.get_trading_results_in_period(
            db=self.db, start_date=start_date, end_date=end_date, oil_id=oil_id,
            delivery_type_id=delivery_type_id, delivery_basis_id=delivery_basis_id
        )
        return TradingResultsList(trading_results=result)
