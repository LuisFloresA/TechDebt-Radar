"""Tests del parser de `git log --numstat` y de las métricas."""

from pathlib import Path

from app.gitana.metrics import bus_factor, cadence, churn, hotspots, summarize
from app.gitana.parser import parse_numstat, run_git_log


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
