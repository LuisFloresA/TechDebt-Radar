"""Tests del selector de ramas (listado, parseo, clonado por rama)."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.clone.branches import BranchListError, parse_ls_remote
from app.clone.validation import InvalidRepo, validate_branch_name
from app.gitana.parser import parse_numstat, run_git_log


def test_parse_ls_remote_names() -> None:
    out = "abc123\trefs/heads/main\ndef456\trefs/heads/dev\n"
    branches, default = parse_ls_remote(out)
    assert branches == ["main", "dev"]
    assert default is None


def test_parse_ls_remote_detects_default_symref() -> None:
    out = "ref: refs/heads/master\tHEAD\nabc\trefs/heads/master\n"
    branches, default = parse_ls_remote(out)
    assert branches == ["master"]
    assert default == "master"


def test_parse_ls_remote_ignores_others() -> None:
    out = "abc\trefs/heads/main\nxyz\trefs/tags/v1\n"
    branches, _ = parse_ls_remote(out)
    assert branches == ["main"]


def test_validate_branch_allowed() -> None:
    assert validate_branch_name("main") == "main"
    assert validate_branch_name("feature/ui") == "feature/ui"
    assert validate_branch_name("all") == "all"


def test_validate_branch_rejects_bad() -> None:
    for bad in ["..", "foo/../../bar", "@{", "-lead", "a b", "../x"]:
        try:
            validate_branch_name(bad)
        except InvalidRepo:
            continue
        raise AssertionError(f"branch {bad!r} debería haberse rechazado")


def test_branches_endpoint(
    client: TestClient, monkeypatch
) -> None:
    import app.api.analyze as analyze_api

    monkeypatch.setattr(
        analyze_api,
        "repo_heads",
        lambda ref: (["zeta", "main", "alpha", "docs"], "main"),
    )
    res = client.get("/api/repos/octocat/Hello-World/branches")
    assert res.status_code == 200
    body = res.json()
    assert body["branches"] == ["zeta", "main", "alpha", "docs"]
    assert body["default"] == "main"


def test_branches_endpoint_failure_404(
    client: TestClient, monkeypatch
) -> None:
    import app.api.analyze as analyze_api

    def boom(ref):
        raise BranchListError("no repo")

    monkeypatch.setattr(analyze_api, "repo_heads", boom)
    res = client.get("/api/repos/octocat/nope/branches")
    assert res.status_code == 404


def test_analyze_with_branch_persists_and_runs(
    client: TestClient, _local_clone: None
) -> None:
    res = client.post(
        "/api/analyze",
        json={"url": "https://github.com/LuisFloresA/TechDebt-Radar", "branch": "dev"},
    )
    assert res.status_code == 202
    job_id = res.json()["id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    body = status_res.json()
    assert body["job"]["branch"] == "dev"
    assert body["job"]["status"] == "succeeded"


def test_analyze_rejects_invalid_branch(client: TestClient) -> None:
    res = client.post(
        "/api/analyze",
        json={"url": "https://github.com/o/r", "branch": "../escape"},
    )
    assert res.status_code == 422


def test_all_branches_log_counts_more(tmp_path: Path) -> None:
    from tests.test_gitana import make_repo_two_branches

    root = make_repo_two_branches(tmp_path)
    single = parse_numstat(run_git_log(root))
    multi = parse_numstat(run_git_log(root, all_branches=True))
    assert multi.total_commits > single.total_commits
