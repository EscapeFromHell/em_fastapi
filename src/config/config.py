from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api_v1"
    REDIS_URL: str = "redis://redis:6379"
    REDIS_EXPIRATION_TIME: int = 24 * 60 * 60
    URL: str = "https://spimex.com/upload/reports/oil_xls/oil_xls_"
    DRIVER: str = "postgresql+asyncpg://"
    USER: str = "postgres"
    PASSWORD: str = ":password"
    HOST: str = "@spimex-fastapi-db"
    PORT: str = ":5432/"
    NAME: str = "spimex-fastapi"

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost",
        "http://127.0.0.1",
    ]
    BACKEND_HOST_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost",
        "http://127.0.0.1",
    ]

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()
