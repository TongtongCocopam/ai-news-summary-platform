from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    MYSQL_DATABASE: str = Field(default="news_briefing")
    MYSQL_ROOT_PASSWORD: str = Field(default="root_password")
    MYSQL_USER: str = Field(default="user")
    MYSQL_PASSWORD: str = Field(default="password")
    MYSQL_PORT: str = Field(default="3306")
    MYSQL_HOST: str = Field(default="localhost")

    DATABASE_URL: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    SECRET_KEY: str = Field(default="secret")
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = Field(default="http://localhost:3000")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
