"""Tests de validación de URLs de repositorio."""

import pytest

from app.clone.validation import InvalidRepo, parse_github_url


def test_valid_github_url() -> None:
    ref = parse_github_url("https://github.com/LuisFloresA/TechDebt-Radar")
    assert ref.owner == "LuisFloresA"
    assert ref.repo == "TechDebt-Radar"
    assert ref.clone_url.endswith(".git")


def test_www_host_ok() -> None:
    ref = parse_github_url("https://www.github.com/owner/repo")
    assert ref.owner == "owner"


def test_only_https_enforced() -> None:
    with pytest.raises(InvalidRepo):
        parse_github_url("http://github.com/owner/repo")


def test_foreign_host_rejected() -> None:
    with pytest.raises(InvalidRepo):
        parse_github_url("https://gitlab.com/owner/repo")


def test_bad_path_rejected() -> None:
    with pytest.raises(InvalidRepo):
        parse_github_url("https://github.com/onlyowner")
