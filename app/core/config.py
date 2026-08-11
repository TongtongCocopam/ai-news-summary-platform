from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import (
    BaseSettings,
    NoDecode,
    SettingsConfigDict,
)


def split_comma(value: Any) -> Any:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",")]
    return value


CommaSeparatedList = Annotated[list[str], NoDecode, BeforeValidator(split_comma),]


class Settings(BaseSettings):
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    cors_origins: CommaSeparatedList = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://"
            f"{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}"
            f"/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )


settings = Settings()
