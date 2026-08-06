"""Configuración central de la aplicación (pydantic-settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores de configuración leídos desde entorno / .env."""

    app_name: str = "TechDebt Radar"
    debug: bool = False
    database_url: str = "sqlite:///./radar.db"
    allowed_origins: str = (
        "http://localhost:5173,http://localhost:8080,http://localhost:8888,"
        "http://localhost:3000"
    )
    require_sqlite_ready: bool = True

    redis_url: str = "redis://localhost:6379/0"
    repo_storage_dir: str = "./data/repos"
    max_repo_size_mb: int = 200
    clone_depth: int = 1
    clone_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
