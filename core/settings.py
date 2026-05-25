from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    FONTS_PATH: str = Field(default="/usr/share/fonts/")
    ASSETS_PATH: str = Field(default="templates/assets/")

    model_config = {"env_file": ".env/.env.app"}


class DatabaseSettings(BaseSettings):
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: str = Field(default="5432")
    DB_NAME: str = Field(default="sieej")

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @classmethod
    def from_env(cls, name: str) -> "DatabaseSettings":
        return cls(_env_file=Path(".env") / f".env.{name}")


class HistoriaSettings(BaseSettings):
    HISTORIA_MAPS_URL: str = Field(default="")

    model_config = {"env_file": ".env/.env.historia"}


class GeografiaSettings(BaseSettings):
    GEOGRAFIA_MAPS_FOLDER_URL: str = Field(default="")
    GEOGRAFIA_MAPS_QUALITY: str = Field(default="full")

    model_config = {"env_file": ".env/.env.geografia"}
