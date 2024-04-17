import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.backends.redis import RedisBackend

from src.api.api_v1 import api_router
from src.config import settings
from src.core.db import redis, redis_cache

root_router = APIRouter()


def get_application() -> FastAPI:
    app = FastAPI(title="Spimex FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.include_router(root_router)
    return app


app = get_application()


@app.on_event("startup")
async def startup_event():
    redis_cache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
