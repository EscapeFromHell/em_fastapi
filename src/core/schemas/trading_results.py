from datetime import date, datetime

from pydantic import BaseModel, PositiveInt


class SpimexTradingResultsBase(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: str
    total: str
    count: str
    date: date


class SpimexTradingResultsCreate(SpimexTradingResultsBase):
    pass


class SpimexTradingResultsUpdate(SpimexTradingResultsBase):
    pass


class SpimexTradingResultsInDB(SpimexTradingResultsBase):
    id: PositiveInt
    created_on: datetime
    updated_on: datetime

    class Config:
        from_attributes = True


class SpimexTradingResults(SpimexTradingResultsInDB):
    pass


class SuccessResponseMessage(BaseModel):
    response_message: str


class LastTradingDates(BaseModel):
    last_trading_dates: list[date]


class TradingResultsList(BaseModel):
    trading_results: list[SpimexTradingResults]
