"""Análisis estático ligero del árbol de código."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

_ANALYZE_EXTS = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
    ".rb", ".php", ".c", ".h", ".cpp", ".hpp", ".cs", ".sh", ".kt", ".swift",
}
_SKIP_DIRS = {
    "node_modules", ".git", "vendor", "dist", "build", ".venv", "venv",
    "__pycache__", ".next", "target", ".data",
}
_SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock"}
_CONTROL_RE = re.compile(
    r"\b(if|elif|else|for|while|switch|case|catch|finally)\b", re.IGNORECASE
)
_TODO_RE = re.compile(r"\bTODO\b")
_FIXME_RE = re.compile(r"\bFIXME\b")
_MAX_FILES = 3000
_MAX_LINES = 200_000


@dataclass
class StaticFile:
    path: str
    ext: str
    lines: int = 0
    todos: int = 0
    fixmes: int = 0
    complexity: int = 0
    digest: str = ""


@dataclass
class StaticScan:
    files: list[StaticFile] = field(default_factory=list)

    @property
    def total_lines(self) -> int:
        return sum(f.lines for f in self.files)

    @property
    def total_todos(self) -> int:
        return sum(f.todos for f in self.files)

    @property
    def total_fixmes(self) -> int:
        return sum(f.fixmes for f in self.files)

    @property
    def large_files(self) -> list[StaticFile]:
        return [f for f in self.files if f.lines > 500]

    @property
    def duplicate_units(self) -> int:
        by_digest: dict[str, list[StaticFile]] = {}
        for f in self.files:
            by_digest.setdefault(f.digest, []).append(f)
        return sum(len(group) - 1 for group in by_digest.values() if len(group) > 1)


def _should_skip(path: Path, rel: str) -> bool:
    if path.name in _SKIP_FILES:
        return True
    return any(part in _SKIP_DIRS for part in path.parts)


def scan_repo(repo: Path) -> StaticScan:
    """Escanea el árbol del repo aplicando heurísticos simples por archivo."""
    scan = StaticScan()
    count = 0
    for path in repo.rglob("*"):
        if not path.is_file() or count >= _MAX_FILES:
            continue
        rel = path.relative_to(repo).as_posix()
        ext = path.suffix.lower()
        if ext not in _ANALYZE_EXTS or _should_skip(path, rel):
            continue
        try:
            content = path.read_bytes()[: _MAX_LINES * 4]
        except OSError:
            continue
        if b"\x00" in content:
            continue

        count += 1
        text = content.decode("utf-8", errors="replace")
        lines = text.count("\n")
        sf = StaticFile(
            path=rel,
            ext=ext,
            lines=lines,
            todos=len(_TODO_RE.findall(text)),
            fixmes=len(_FIXME_RE.findall(text)),
            complexity=len(_CONTROL_RE.findall(text)),
            digest=hashlib.sha256(content).hexdigest()[:16],
        )
        scan.files.append(sf)
    return scan
