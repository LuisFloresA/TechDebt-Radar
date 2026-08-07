"""Fixtures compartidos de pytest."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator
from contextlib import suppress
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.ratelimit import reset
from app.db.session import Base, engine
from app.main import app


def _run(cmd: list[str], cwd: str) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture(autouse=True)
def _clean_db() -> Iterator[None]:
    """Recrea el esquema en una base efímera por test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _rate_limit_clean() -> Iterator[None]:
    """Limita alto por defecto y resetea el estado entre tests."""
    settings = get_settings()
    previous = settings.rate_limit_per_minute
    settings.rate_limit_per_minute = 1000
    reset()
    yield
    settings.rate_limit_per_minute = previous
    reset()


@pytest.fixture(autouse=True)
def _eager(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ejecuta las tareas Celery de forma síncrona (eager) en tests."""
    from app.workers.celery_app import celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True


@pytest.fixture()
def _local_clone(monkeypatch: pytest.MonkeyPatch, fake_repo: Path) -> None:
    """Evita redir hacia GitHub: el 'clon' es el repo ficticio local."""

    import app.workers.tasks as tasks

    monkeypatch.setattr(
        tasks, "clone_to_storage", lambda ref, job_id, branch="main": fake_repo
    )


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def _commit(repo: str, author: str, day: str, count: int = 1) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = author
    env["GIT_AUTHOR_EMAIL"] = f"{author.replace(' ', '.').lower()}@example.com"
    env["GIT_AUTHOR_DATE"] = f"{day}T12:00:00Z"
    env["GIT_COMMITTER_NAME"] = author
    env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
    env["GIT_COMMITTER_DATE"] = f"{day}T12:00:00Z"

    _run(["git", "add", "."], repo)
    subprocess.run(
        ["git", "commit", "-m", f"commit {count} on {day}"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    """Repositorio git ficticio con 2 autores y algunos commits."""
    root = tmp_path / "fake"
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text("# README\n")
    (root / "app.py").write_text("x = 1\n")
    (root / "utils.py").write_text("y = 2\n")

    _run(["git", "init", "-q", "-b", "main"], str(root))
    _run(["git", "config", "user.email", "dev@example.com"], str(root))
    _run(["git", "config", "user.name", "dev"], str(root))
    with suppress(Exception):
        _run(["git", "config", "commit.gpgsign", "false"], str(root))
    _run(["git", "add", "."], str(root))
    _run(["git", "commit", "-q", "-m", "chore: initial"], str(root))

    (root / "app.py").write_text("x = 1\nz = 3\n")
    (root / "utils.py").write_text("y = 2\nw = 4\n")
    _commit(str(root), "Ana", "2026-01-01", count=2)

    (root / "app.py").write_text("x = 1\nz = 3\nw = 4\n")
    _commit(str(root), "Bob", "2026-01-02", count=3)

    return root
