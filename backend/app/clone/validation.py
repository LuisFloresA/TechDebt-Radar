"""Validación de URLs de repositorio (anti-SSRF)."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

GITHUB_HOSTS = ("github.com", "www.github.com")
_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")
_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
_BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-/]{0,255}$")


class InvalidRepo(ValueError):
    """URL de repositorio no aceptada."""


@dataclass(frozen=True)
class RepoRef:
    """Identidad normalizada de un repositorio GitHub público."""

    owner: str
    repo: str

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}.git"


def _host_resolves_private(hostname: str) -> bool:
    """True si el hostno es global (bloquea SSRF a IPs privadas/reservadas)."""
    try:
        infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        # No resuelve: no permitimos hosts no verificables.
        return True
    for _family, _type, _proto, _canon, sockaddr in infos:
        if ipaddress.ip_address(sockaddr[0]).is_global:
            return False
    return True


def parse_github_url(url: str) -> RepoRef:
    """Valida y normaliza una URL devolviendo un RepoRef seguro."""
    try:
        parsed = urlparse(url.strip())
    except ValueError as exc:
        raise InvalidRepo(f"URL inválida: {url!r}") from exc

    if parsed.scheme != "https":
        raise InvalidRepo("Solo se admiten URLs https://github.com/...")

    host = parsed.hostname
    if host not in GITHUB_HOSTS:
        raise InvalidRepo("Solo se admiten URLs de github.com")

    if _host_resolves_private(host):
        raise InvalidRepo("Host no verificable (posible SSRF)")
    path = parsed.path.lstrip("/")
    match = _REPO_PATTERN.match(path)
    if not match:
        raise InvalidRepo('Formato esperado: "owner/repositorio"')

    owner, repo = (p.strip("/") for p in match.group(0).split("/")[:2])
    if not owner or not repo or ".." in (owner, repo):
        raise InvalidRepo("Ruta de repositorio inválida")

    return RepoRef(owner=owner, repo=repo)


def validate_owner_repo(owner: str, repo: str) -> RepoRef:
    """Valida los componentes owner/repo de una URL de GitHub."""
    if not owner or not repo:
        raise InvalidRepo("owner y repo son obligatorios")
    if not _OWNER_PATTERN.fullmatch(owner) or not _OWNER_PATTERN.fullmatch(repo):
        raise InvalidRepo("owner/repo contiene caracteres inválidos")
    if ".." in owner or ".." in repo:
        raise InvalidRepo("owner/repo inválido")
    return RepoRef(owner=owner, repo=repo)


def validate_branch_name(branch: str) -> str:
    """Valida un nombre de rama. Devuelve el nombre normalizado."""
    value = branch.strip()
    if value == "all":
        return value
    if not _BRANCH_PATTERN.fullmatch(value):
        raise InvalidRepo("Nombre de rama inválido")
    if ".." in value or "@{" in value or value.lstrip().startswith("-"):
        raise InvalidRepo("Nombre de rama inválido")
    return value
