"""Rate limiting simple en memoria por IP cliente (ventana deslizante)."""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Iterator

from app.core.config import get_settings

_hits: dict[str, deque[float]] = {}
_locks: dict[str, threading.Lock] = {}
_state_lock = threading.Lock()


def _lock_for(key: str) -> threading.Lock:
    with _state_lock:
        lock = _locks.setdefault(key, threading.Lock())
    return lock


def allow(key: str, limit: int, window_seconds: float = 60.0) -> bool:
    """True si la clave puede emitir otra petición dentro del límite."""
    now = time.monotonic()
    with _lock_for(key):
        hits = _hits.setdefault(key, deque())
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


def reset() -> None:
    """Limpia el estado (usado en tests)."""
    for key in list(_hits):
        with _lock_for(key):
            _hits[key].clear()


def client_ip(
    request_host: str, forwarded_for: str | None = None
) -> str:
    """Devuelve el IP real del cliente, respetando el proxy de nginx."""
    if forwarded_for:
        first = forwarded_for.split(",")[0].strip()
        if first:
            return first
    return request_host


def is_rate_limited(ip: str) -> bool:
    """Decide si la petición de `ip` supera el límite configurado."""
    settings = get_settings()
    return not allow(f"ip:{ip}", settings.rate_limit_per_minute)


def iter_state() -> Iterator[tuple[str, int]]:
    """Expone el estado (diagnóstico): clave -> hits actuales."""
    for key, hits in list(_hits.items()):
        yield key, len(hits)
