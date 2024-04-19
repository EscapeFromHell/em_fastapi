import logging

from celery import Celery
from celery.schedules import crontab

from src.core.db import redis_cache
from src.utils import get_logger

logger = get_logger(log_level=logging.DEBUG)

app = Celery("tasks", broker="redis://redis:6379/0")


@app.task
async def reset_cache():
    logger.info("CELERY reset cache")
    await redis_cache.clear()


app.conf.beat_schedule = {
    "reset-cache-at-14-11": {
        "task": "reset_cache",
        "schedule": crontab(hour="14", minute="11"),
    },
}
