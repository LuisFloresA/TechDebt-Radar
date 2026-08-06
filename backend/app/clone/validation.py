"""Validación de URLs de repositorio (anti-SSRF)."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

GITHUB_HOSTS = ("github.com", "www.github.com")
_REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


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
