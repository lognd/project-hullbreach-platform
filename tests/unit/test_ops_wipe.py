"""Unit tests for demo-wipe over fake docker and a throwaway checkout."""

from __future__ import annotations

import io
from pathlib import Path

from ops_fakes import FakeRunner, make_ctx, ok, output

from hullbreach_ops import wipe
from hullbreach_ops.console import Console
from hullbreach_ops.context import OpsContext

VOLUME_LS = ("docker", "volume", "ls")
DOWN = ("docker", "compose", "-p", "platform", "down", "-v")


def _asking(answer: str) -> Console:
    """A console that types `answer` at every prompt."""
    return Console(io.StringIO(), interactive=True, ask=lambda _q: answer)


def _stale_state(ctx: OpsContext) -> list[Path]:
    """Create the files a previous demo run leaves behind; return the removable ones."""
    s = ctx.settings
    s.logs_dir.mkdir(parents=True)
    s.run_dir.mkdir(parents=True)
    files = [
        s.logs_dir / "api.log",
        s.logs_dir / "web.log",
        s.root / "hullbreach-support-20260101-000000.zip",
    ]
    for f in files:
        f.write_text("POST /auth/register user=logand\n", encoding="utf-8")
    (s.logs_dir / "ops.log").write_text("old ops\n", encoding="utf-8")
    return files


def test_wipe_demo_needs_a_person_and_the_exact_volume_name(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/wipe.py::wipe_demo kind="unit"
    runner = FakeRunner()
    quiet = make_ctx(tmp_path, runner=runner)
    files = _stale_state(quiet)
    err = wipe.wipe_demo(quiet).danger_err
    assert err.message == "demo-wipe needs a person at the keyboard to confirm"

    wrong = make_ctx(tmp_path, runner=runner, console=_asking("yes"))
    assert wipe.wipe_demo(wrong).is_ok
    assert "Not confirmed; nothing was deleted." in output(wrong)
    assert not runner.ran("docker", "compose", "-p", "platform", "down")
    assert all(f.exists() for f in files)


def test_wipe_demo_removes_volumes_and_local_files(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/wipe.py::wipe_demo kind="unit"
    # frob:tests src/hullbreach_ops/wipe.py::clear_local_files kind="unit"
    runner = FakeRunner(
        replies={VOLUME_LS: ok(stdout="platform_pgdata\nother-checkout_pgdata\n")}
    )
    ctx = make_ctx(tmp_path, runner=runner, console=_asking("platform_pgdata"))
    files = _stale_state(ctx)
    assert wipe.wipe_demo(ctx).is_ok
    assert runner.ran(*DOWN)
    assert not any(f.exists() for f in files)
    # ops.log is open for this very command, so it is emptied, not removed.
    assert (ctx.settings.logs_dir / "ops.log").read_text(encoding="utf-8") == ""
    text = output(ctx)
    assert "Deleted the database container and volume platform_pgdata" in text
    assert "other-checkout_pgdata" in text
    assert "Browser" in text and "PlayerPrefs" in text
    assert "HULLBREACH_PLATFORM_USERNAME" in text
    assert "uv run hullbreach_server demo" in text


def test_wipe_demo_warns_when_the_project_name_is_overridden(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/wipe.py::wipe_demo kind="unit"
    env = {"COMPOSE_PROJECT_NAME": "hullbreach"}
    ctx = make_ctx(tmp_path, env, console=_asking("no"))
    wipe.wipe_demo(ctx)
    assert "COMPOSE_PROJECT_NAME is set to hullbreach" in output(ctx)
    plain = make_ctx(tmp_path, console=_asking("no"))
    wipe.wipe_demo(plain)
    assert "COMPOSE_PROJECT_NAME is set" not in output(plain)


def test_wipe_demo_reports_a_docker_failure_without_touching_files(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/wipe.py::wipe_demo kind="unit"
    runner = FakeRunner(replies={DOWN: ok(stderr="daemon down", returncode=1)})
    ctx = make_ctx(tmp_path, runner=runner, console=_asking("platform_pgdata"))
    files = _stale_state(ctx)
    err = wipe.wipe_demo(ctx).danger_err
    assert err.message.startswith("docker compose down -v failed")
    assert all(f.exists() for f in files)


def test_other_pgdata_volumes_skips_ours_and_tolerates_docker_errors(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/wipe.py::other_pgdata_volumes kind="unit"
    runner = FakeRunner(replies={VOLUME_LS: ok(stdout="platform_pgdata\nx_pgdata\n")})
    assert wipe.other_pgdata_volumes(make_ctx(tmp_path, runner=runner)) == ["x_pgdata"]
    broken = FakeRunner(replies={VOLUME_LS: ok(stderr="no", returncode=1)})
    assert wipe.other_pgdata_volumes(make_ctx(tmp_path, runner=broken)) == []
