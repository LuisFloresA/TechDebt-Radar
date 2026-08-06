"""Acceso a base de datos (modelos + sesión)."""

from app.db.models import Job, Report
from app.db.session import Base, SessionLocal, engine, get_db, init_db

init_db()

__all__ = ["Base", "SessionLocal", "Job", "Report", "engine", "get_db", "init_db"]
