"""Tests del parser de `git log --numstat` y de las métricas."""

from pathlib import Path

from app.gitana.metrics import bus_factor, cadence, churn, hotspots, summarize
from app.gitana.parser import parse_numstat, run_git_log


def make_repo_two_branches(tmp_path: Path) -> Path:
    """Repo git con dos ramas (main + feature), cada una con commits propios."""
    import os
    import subprocess

    root = tmp_path / "twobranches"
    root.mkdir(parents=True, exist_ok=True)

    def run(cmd: list[str], env_extra: dict[str, str] | None = None) -> None:
        env = os.environ.copy()
        env.update(env_extra or {})
        subprocess.run(cmd, cwd=str(root), check=True, capture_output=True, text=True, env=env)

    def commit(name: str, author: str, day: str) -> None:
        env = {
            "GIT_AUTHOR_NAME": author,
            "GIT_AUTHOR_EMAIL": f"{author}@example.com",
            "GIT_AUTHOR_DATE": f"{day}T12:00:00Z",
            "GIT_COMMITTER_NAME": author,
            "GIT_COMMITTER_EMAIL": f"{author}@example.com",
            "GIT_COMMITTER_DATE": f"{day}T12:00:00Z",
        }
        (root / "f.txt").write_text(name)
        run(["git", "add", "."], env)
        run(["git", "commit", "-m", name, "--no-gpg-sign"], env)

    run(["git", "init", "-q", "-b", "main"])
    run(["git", "config", "user.email", "dev@example.com"])
    run(["git", "config", "user.name", "dev"])
    run(["git", "config", "commit.gpgsign", "false"])
    commit("c-main-1", "Ana", "2026-01-01")
    commit("c-main-2", "Bob", "2026-01-02")
    run(["git", "branch", "feature"])
    run(["git", "checkout", "-q", "feature"])
    commit("c-feature-1", "Ana", "2026-01-03")
    commit("c-feature-2", "Ana", "2026-01-04")
    run(["git", "checkout", "-q", "main"])
    return root


def test_parse_numstat_from_fake_repo(fake_repo: Path) -> None:
    output = run_git_log(fake_repo)
    analysis = parse_numstat(output)

    assert analysis.total_commits == 3
    assert len(analysis.total_authors) >= 2
    assert "Ana" in analysis.total_authors
    assert "Bob" in analysis.total_authors
    assert set(analysis.files) == {"app.py", "utils.py", "README.md"}


def test_hotspots_ranking(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    hs = hotspots(analysis)
    assert hs
    assert hs[0]["path"] == "app.py"


def test_churn_counts(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    ch = churn(analysis)
    total_churn = sum(item["churn"] for item in ch)
    assert total_churn > 0


def test_bus_factor_distribution(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    bf = bus_factor(analysis)
    assert bf
    assert all(isinstance(item["changes"], int) for item in bf)


def test_cadence_ordered(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    cd = cadence(analysis)
    assert cd
    days = list(cd.keys())
    assert days == sorted(days)


def test_summarize_shape(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    report = summarize(analysis)
    assert set(report) == {"summary", "hotspots", "churn", "bus_factor", "cadence"}
    assert report["summary"]["total_commits"] == 3
