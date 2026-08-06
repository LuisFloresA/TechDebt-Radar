"""Endpoints de salud (liveness y readiness)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    status: str
    database: str


def _database_ok(settings: Settings) -> bool:
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse, summary="Liveness")
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Indica que el proceso responde (liveness)."""
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/health/ready", response_model=ReadyResponse, summary="Readiness")
def ready(settings: Settings = Depends(get_settings)) -> ReadyResponse:
    """Indica que la app está lista para servir tráfico (readiness)."""
    db_ok = _database_ok(settings)
    if settings.require_sqlite_ready and not db_ok:
        return ReadyResponse(status="not_ready", database="error")
    return ReadyResponse(status="ok", database="ok")
