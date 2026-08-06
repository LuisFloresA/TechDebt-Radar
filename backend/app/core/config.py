"""Configuración central de la aplicación (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuración leídos desde entorno / .env."""

    app_name: str = "TechDebt Radar"
    debug: bool = False
    database_url: str = "sqlite:///./radar.db"
    allowed_origins: str = (
        "http://localhost:5173,http://localhost:8080,http://localhost:3000"
    )
    require_sqlite_ready: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
