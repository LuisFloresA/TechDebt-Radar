"""Listado de ramas remotas vía `git ls-remote` (sin clonar el árbol)."""

from __future__ import annotations

import os
import re
import subprocess
import time

from app.clone.validation import RepoRef
from app.core.config import get_settings

_CACHE_TTL_S = 60
_cache: dict[str, tuple[float, tuple[list[str], str]]] = {}
_HEAD_SYMREF_RE = re.compile(r"^ref:\s+refs/heads/(.+)\s+HEAD$")


class BranchListError(RuntimeError):
    """No se pudieron listar las ramas del repositorio."""


def parse_ls_remote(output: str) -> tuple[list[str], str | None]:
    """Ramas de `refs/heads/` y, si aparece, la rama por defecto (HEAD symref)."""
    branches: list[str] = []
    default: str | None = None
    for line in output.splitlines():
        line = line.rstrip("\n")
        symref = _HEAD_SYMREF_RE.match(line)
        if symref:
            default = symref.group(1)
            continue
        if "\t" not in line:
            continue
        ref = line.split("\t", 1)[1].strip()
        marker = "refs/heads/"
        if ref.startswith(marker):
            branches.append(ref[len(marker):])
    return branches, default


def _run_ls_remote(cmd: list[str], timeout: float) -> str:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if proc.returncode != 0:
        raise BranchListError((proc.stderr or "").strip()[:400] or "git ls-remote falló")
    return proc.stdout


def repo_heads(repo: RepoRef, use_cache: bool = True) -> tuple[list[str], str]:
    """Devuelve (ramas, rama por defecto) de un repo GitHub, con cache corta."""
    key = f"{repo.owner}/{repo.repo}"
    now = time.monotonic()
    if use_cache:
        cached = _cache.get(key)
        if cached and now - cached[0] < _CACHE_TTL_S:
            return cached[1]

    output = _run_ls_remote(
        ["git", "ls-remote", "--symref", repo.clone_url],
        get_settings().ls_remote_timeout_seconds,
    )
    branches, symref_default = parse_ls_remote(output)
    if symref_default and symref_default in branches:
        default = symref_default
    elif "main" in branches:
        default = "main"
    else:
        default = branches[0] if branches else "main"
    result = (branches, default)
    if use_cache:
        _cache[key] = (now, result)
    return result


def list_remote_branches(repo: RepoRef) -> list[str]:
    return repo_heads(repo)[0]


def clear_cache() -> None:
    _cache.clear()
