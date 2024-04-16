from fastapi import APIRouter

from src.api.api_v1.endpoints import router

api_router = APIRouter()

api_router.include_router(router, prefix="/trading_results", tags=["trading_results"])
