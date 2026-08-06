"""Extracción del historial de Git mediante `git log --numstat`."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileStats:
    """Estadísticas por archivo a lo largo del historial."""

    path: str
    changes: int = 0
    added: int = 0
    deleted: int = 0
    commits: int = 0
    authors: set[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.authors is None:
            self.authors = set()


@dataclass
class RepoAnalysis:
    """Resultado agregado del análisis de un repositorio."""

    total_commits: int = 0
    total_authors: set[str] = None  # type: ignore[assignment]
    files: dict[str, FileStats] = None  # type: ignore[assignment]
    commits_per_day: dict[str, int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.total_authors is None:
            self.total_authors = set()
        if self.files is None:
            self.files = defaultdict(FileStats)
        if self.commits_per_day is None:
            self.commits_per_day = defaultdict(int)


def run_git_log(repo: Path) -> str:
    """Ejecuta `git log --numstat` y devuelve su salida."""
    cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        "--numstat",
        "--pretty=format:COMMIT %H|%an|%ad",
        "--date=short",
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, cwd=str(repo)
    )
    return result.stdout


# Stack trace: it doesn't matter for compute but tests need parser independent.
def parse_numstat(output: str) -> RepoAnalysis:
    """Convierte salida de `git log --numstat` en un RepoAnalysis."""
    analysis = RepoAnalysis()
    files: dict[str, FileStats] = {}
    day_counts: dict[str, int] = defaultdict(int)

    current_author: str | None = None

    for line in output.splitlines():
        line = line.rstrip("\n")
        if line.startswith("COMMIT "):
            # COMMIT_<hash>|<author>|<date>
            parts = line.split("|")
            author = parts[1] if len(parts) > 1 else "unknown"
            day = parts[2] if len(parts) > 2 else "unknown"
            analysis.total_authors.add(author)
            analysis.total_commits += 1
            current_author = author
            if day not in ("unknown",) and day:
                day_counts[day] += 1
            continue

        # Línea numstat: <added>\t<deleted>\t<path>  (o path con -/binary)
        if "\t" not in line:
            continue
        added_s, deleted_s, path = line.split("\t", 2)
        if added_s == "-" or deleted_s == "-":
            continue
        if path.startswith('"') and path.endswith('"'):
            # git escapa rutas con caracteres no-ascii entre comillas
            continue
        if "/vendor/" in path or "/node_modules/" in path or "/.git" in path:
            continue

        st = files.get(path)
        if st is None:
            st = FileStats(path=path)
            files[path] = st
        try:
            added = int(added_s)
            deleted = int(deleted_s)
        except ValueError:
            continue
        st.added += added
        st.deleted += deleted
        st.changes += added + deleted
        st.commits += 1
        if current_author:
            st.authors.add(current_author)

    analysis.files = files
    analysis.commits_per_day = dict(day_counts)
    return analysis
