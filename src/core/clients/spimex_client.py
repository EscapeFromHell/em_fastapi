import logging

import httpx
from fastapi import HTTPException

from src.config import settings
from src.utils import get_logger

logger = get_logger(__file__, logging.DEBUG)


class SpimexClient:
    async def download_spimex_bulletins(self, date_list: list[str]) -> None:
        """
        Загружает бюллетени Spimex.

        Raises:
            Exception: Если произошла ошибка при загрузке бюллетеня.
        """
        try:
            async with httpx.AsyncClient() as client:
                for date in date_list:
                    url = settings.URL + date + "162000.xls"
                    response = await client.get(url=url, timeout=3)
                    if response.status_code == 200:
                        with open(f"{date}_oil_data.xls", "wb") as file:
                            file.write(response.content)

        except (httpx.ConnectError, httpx.ConnectTimeout) as error:
            logger.error(f"Ошибка при скачивании бюллетеня: {error}")
            raise HTTPException(status_code=400, detail="Ошибка при скачивании бюллетеня!")
