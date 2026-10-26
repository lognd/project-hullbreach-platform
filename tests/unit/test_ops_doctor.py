"""Unit tests for the doctor's ordering, PENDING logic and report."""

from __future__ import annotations

from pathlib import Path

import pytest
from ops_fakes import make_ctx, output

from hullbreach_ops import doctor as doc
from hullbreach_ops import readme_links as rl
from hullbreach_ops.checkbase import (
    DEMOS,
    Check,
    CheckResult,
    DoctorRun,
    Status,
    fail,
    ok,
    warn,
)


def _ids(checks: list[Check]) -> list[str]:
    return [check.id for check in checks]


def test_registry_ids_are_unique_and_needs_come_first() -> None:
    seen: list[str] = []
    for check in doc.REGISTRY:
        assert check.id not in seen
        for need in check.needs:
            assert need in seen, f"{check.id} needs {need}, which runs later"
        seen.append(check.id)


def test_select_adds_what_a_check_needs() -> None:
    # frob:tests src/hullbreach_ops/doctor.py::select kind="unit"
    only = _ids(doc.select("full", "migrations").danger_ok)
    assert only[-1] == "migrations"
    assert "db-connect" in only and "settings" in only
    assert "api" not in only
    err = doc.select("full", "nope").danger_err
    assert err.message == "there is no check called 'nope'"
    assert "migrations" in err.fix[0]


def test_demo_profiles_pick_their_checks() -> None:
    # frob:tests src/hullbreach_ops/doctor.py::select kind="unit"
    assert set(DEMOS) == {"website", "guest", "online", "platform"}
    assert doc.select("guest").danger_ok == []
    assert doc.select("online").danger_ok == []
    website = _ids(doc.select("website").danger_ok)
    assert not {"game-keys", "game-session", "lan"} & set(website)
    assert "e2e" in website
    assert _ids(doc.select("platform").danger_ok) == _ids(list(doc.REGISTRY))


def _fake_registry(monkeypatch: pytest.MonkeyPatch, a: CheckResult) -> None:
    """Three checks: a, b needs a, c needs nothing."""
    monkeypatch.setattr(
        doc,
        "REGISTRY",
        (
            Check("a", "first", lambda _r: a),
            Check("b", "second", lambda _r: ok("b fine"), needs=("a",)),
            Check("c", "third", lambda _r: warn("c meh", ["Do c."])),
        ),
    )


def test_failed_check_marks_dependents_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/doctor.py::run_checks kind="unit"
    # frob:tests src/hullbreach_ops/doctor.py::passed kind="unit"
    # frob:tests src/hullbreach_ops/checkbase.py::Status kind="unit"
    # frob:tests src/hullbreach_ops/checkbase.py::CheckResult kind="unit"
    # frob:tests src/hullbreach_ops/checkbase.py::DoctorRun kind="unit"
    # frob:tests src/hullbreach_ops/checkbase.py::Check kind="unit"
    _fake_registry(monkeypatch, fail("a broke", ["Fix a."]))
    cleaned: list[str] = []
    run = DoctorRun(ctx=make_ctx(tmp_path))
    run.cleanups.append(lambda: cleaned.append("x"))
    doc.run_checks(run, list(doc.REGISTRY))
    assert [r.status for r in run.results.values()] == [
        Status.FAIL,
        Status.PENDING,
        Status.WARN,
    ]
    assert run.results["b"].summary == "waiting for: a (fix that first)"
    assert cleaned == ["x"] and run.cleanups == []
    assert not doc.passed(run)

    _fake_registry(monkeypatch, warn("a works", ["Look at a."]))
    fine = DoctorRun(ctx=make_ctx(tmp_path))
    doc.run_checks(fine, list(doc.REGISTRY))
    assert fine.results["b"].status == Status.PASS
    assert doc.passed(fine)


def test_doctor_prints_fix_steps_and_the_first_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/doctor.py::doctor kind="unit"
    _fake_registry(monkeypatch, fail("a broke", ["Fix a.", "Run again."], rl.DOCKER))
    ctx = make_ctx(tmp_path)
    run = doc.doctor(ctx).danger_ok
    text = output(ctx)
    assert "[FAIL]    a                a broke" in text
    assert "[PENDING] b                waiting for: a (fix that first)" in text
    assert "How to fix:" in text
    assert "1. Fix a." in text and "2. Run again." in text
    assert f"More help: README '2b. Docker': {rl.DOCKER.url}" in text
    assert "Summary: 0 PASS, 1 WARN, 1 FAIL, 1 PENDING" in text
    assert "Fix the first FAIL (a) using its steps above" in text
    assert "./doctor.sh --only a" in text
    assert "--collect" in text
    assert "Next" not in text
    assert not doc.passed(run)

    _fake_registry(monkeypatch, ok("a fine"))
    good = make_ctx(tmp_path)
    assert doc.passed(doc.doctor(good, "website").danger_ok)
    assert "1. Start everything:" in output(good)
    assert doc.doctor(good, only="zzz").is_err


def test_doctor_game_only_demo_points_to_the_game_doctor(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/doctor.py::doctor kind="unit"
    for profile in ("guest", "online"):
        ctx = make_ctx(tmp_path)
        run = doc.doctor(ctx, profile).danger_ok
        text = output(ctx)
        assert run.results == {}
        assert f"The {profile} demo is {DEMOS[profile]}" in text
        assert "https://github.com/lognd/project-hullbreach-game#readme" in text
        assert ("--demo platform" in text) == (profile == "online")
        assert "Summary" not in text
