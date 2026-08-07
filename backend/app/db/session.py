"""Sesión y motor de base de datos (SQLAlchemy)."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos."""


def make_engine():
    settings = get_settings()
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    )


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _apply_sqlite_migrations() -> None:
    """Mini-migraciones idempotentes para SQLite (evita recrear el volumen)."""
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.begin() as conn:
        for table, column, ddl in (
            ("jobs", "branch", "ALTER TABLE jobs ADD COLUMN branch VARCHAR(20) DEFAULT 'main'"),
        ):
            if table in inspect(conn).get_table_names():
                cols = {c["name"] for c in inspect(conn).get_columns(table)}
                if column not in cols:
                    conn.execute(text(ddl))


def init_db() -> None:
    """Crea las tablas y aplica migraciones (debe ejecutarse tras importar los modelos)."""
    Base.metadata.create_all(engine)
    _apply_sqlite_migrations()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
