"""Tests del escaneo estático y del score/recomendaciones."""

from pathlib import Path

from app.analytics import build_report
from app.gitana.parser import RepoAnalysis, parse_numstat, run_git_log
from app.scoring.recommendations import build_recommendations
from app.scoring.score import compute_score
from app.static.scan import scan_repo


def _write_tree(root: Path) -> None:
    (root / "mod.py").write_text(
        "def f():\n"
        "    # TODO: refactor esto\n"
        "    if x:\n"
        "        return 1\n"
        "    return 2\n"
    )
    (root / "mod.js").write_text("// FIXME: leaks memory\nconst a = 1\n")
    (root / "vendor").mkdir()
    (root / "vendor" / "lib.py").write_text("skip = True\n")
    (root / "big.py").write_text(f"# {0}\n" + "\n".join(f"x{i}=1" for i in range(600)))
    (root / "dup_a.py").write_text("LINE_A\n" * 20)
    (root / "dup_b.py").write_text("LINE_A\n" * 20)
    (root / "data.bin").write_bytes(b"\x00\x01\x02\x03")


def test_scan_counts_todos_fixmes_and_skips(tmp_path: Path) -> None:
    _write_tree(tmp_path)
    scan = scan_repo(tmp_path)

    assert scan.total_todos == 1
    assert scan.total_fixmes == 1
    paths = [f.path for f in scan.files]
    assert "vendor/lib.py" not in paths
    assert "data.bin" not in paths
    assert any(f.path == "mod.py" for f in scan.files)


def test_scan_detects_large_files_and_duplicates(tmp_path: Path) -> None:
    _write_tree(tmp_path)
    scan = scan_repo(tmp_path)

    assert any(f.path == "big.py" for f in scan.large_files)
    assert scan.duplicate_units >= 1
    assert scan.total_lines > 0


def test_score_in_bounds_and_components(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    static = scan_repo(fake_repo)
    result = compute_score(analysis, static)

    assert 0 <= result["score"] <= 100
    assert set(result["components"]) == {
        "bus_factor",
        "hotspots",
        "churn",
        "tech_debt",
        "cadence",
    }
    for value in result["components"].values():
        assert 0 <= value <= 100


def test_tech_debt_penalizes_markers(tmp_path: Path) -> None:
    analysis = RepoAnalysis(total_commits=0)
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "a.py").write_text("x = 1\n")
    dirty = tmp_path / "dirty"
    dirty.mkdir()
    (dirty / "a.py").write_text("# TODO: a\n# TODO: b\n# TODO: c\n# TODO: d\n# TODO: e\n")
    (dirty / "b.py").write_text("# FIXME: f\n# FIXME: g\n# FIXME: h\n")

    clean_score = compute_score(analysis, scan_repo(clean))["components"]["tech_debt"]
    dirty_score = compute_score(analysis, scan_repo(dirty))["components"]["tech_debt"]
    assert clean_score > dirty_score


def test_recommendations_prioritize_high_severity(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    static = scan_repo(fake_repo)
    recs = build_recommendations(analysis, static)

    severities = [r["severity"] for r in recs]
    assert severities == sorted(
        severities, key={"high": 0, "medium": 1, "low": 2}.get
    )
    for rec in recs:
        assert {"severity", "title", "detail"} <= set(rec)


def test_build_report_has_f2_sections(fake_repo: Path) -> None:
    analysis = parse_numstat(run_git_log(fake_repo))
    report = build_report(analysis, fake_repo)

    assert {"summary", "hotspots", "churn", "bus_factor", "cadence"} <= set(report)
    assert "static" in report
    assert report["score"]["score"] == round(report["score"]["score"])
    assert 0 <= report["score"]["score"] <= 100
    assert isinstance(report["recommendations"], list)
    assert "total_todos" in report["static"]
