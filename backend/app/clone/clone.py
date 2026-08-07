"""Clonado seguro de repositorios GitHub con límites de recursos."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from app.clone.validation import RepoRef
from app.core.config import get_settings


class CloneError(RuntimeError):
    """Error durante el clonado del repositorio."""


def _size_mb(path: Path) -> float:
    total = 0
    for file in path.rglob("*"):
        if file.is_file():
            total += file.stat().st_size
    return total / (1024 * 1024)


def clone_repo(
    ref: RepoRef,
    dest: Path,
    branch: str | None = "main",
    all_branches: bool = False,
) -> None:
    """Clona `ref` en `dest` de forma aislada y con límites."""
    settings = get_settings()
    dest.mkdir(parents=True, exist_ok=True)

    depth = max(1, settings.clone_depth)
    cmd = ["git", "clone", "--depth", str(depth), "--no-tags"]
    if all_branches:
        cmd.append("--no-single-branch")
    else:
        cmd.extend(["--single-branch", "--branch", branch or "main"])
    cmd += [ref.clone_url, str(dest)]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=settings.clone_timeout_seconds,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        shutil.rmtree(dest, ignore_errors=True)
        stderr = getattr(exc, "stderr", "") or str(exc)
        raise CloneError(f"No se pudo clonar: {stderr.strip()[:500]}") from exc

    if not (dest / ".git").exists():
        shutil.rmtree(dest, ignore_errors=True)
        raise CloneError("El clon no contiene un repositorio Git válido")

    if _size_mb(dest) > settings.max_repo_size_mb:
        shutil.rmtree(dest, ignore_errors=True)
        raise CloneError(
            f"Repositorio excede el límite de {settings.max_repo_size_mb} MB"
        )


def clone_to_storage(
    ref: RepoRef, job_id: int, branch: str = "main"
) -> Path:
    """Clona dentro del directorio de storage aislado por job."""
    settings = get_settings()
    base = Path(settings.repo_storage_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)

    job_dir = f"job-{int(job_id)}"
    root = base / job_dir
    if not root.resolve().is_relative_to(base):
        raise CloneError("Ruta de job inválida (fuera del storage)")

    shutil.rmtree(root, ignore_errors=True)
    all_branches = branch == "all"
    clone_repo(ref, root, branch=branch, all_branches=all_branches)
    return root


def cleanup(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
