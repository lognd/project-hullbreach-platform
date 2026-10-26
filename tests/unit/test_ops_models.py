"""Unit tests for the small derived properties of the operator data models."""

from __future__ import annotations

import io
from pathlib import Path

from ops_fakes import make_ctx

from hullbreach_ops.checkbase import CheckResult, DoctorRun, Status
from hullbreach_ops.console import Console
from hullbreach_ops.dbstate import MigrationState
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import DbContainer
from hullbreach_ops.probe import HttpError
from hullbreach_ops.proc import CommandResult, ProcError
from hullbreach_ops.readme_links import REPO_URL, ReadmeSection
from hullbreach_ops.settings import OpsSettings


def test_only_pass_and_warn_let_dependent_checks_run() -> None:
    # frob:tests src/hullbreach_ops/checkbase.py::CheckResult.usable kind="unit"
    usable = {s: CheckResult(status=s, summary="x").usable for s in Status}
    assert usable == {
        Status.PASS: True,
        Status.WARN: True,
        Status.FAIL: False,
        Status.PENDING: False,
    }


def test_only_the_platform_demo_needs_game_sign_in(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checkbase.py::DoctorRun.needs_game kind="unit"
    ctx = make_ctx(tmp_path)
    assert DoctorRun(ctx=ctx, profile="platform").needs_game
    for profile in ("full", "website", "guest", "online"):
        assert not DoctorRun(ctx=ctx, profile=profile).needs_game


def test_console_reports_interactivity_and_a_redacted_plain_transcript() -> None:
    # frob:tests src/hullbreach_ops/console.py::Console.interactive kind="unit"
    # frob:tests src/hullbreach_ops/console.py::Console.transcript kind="unit"
    # frob:tests src/hullbreach_ops/console.py::Console.status kind="unit"
    console = Console(io.StringIO(), interactive=True, color=True)
    assert console.interactive
    assert not Console(io.StringIO(), interactive=False).interactive
    console.add_secret("hunter2-secret")
    console.status("PASS", "uv", "uv hunter2-secret works")
    assert "hunter2-secret" not in console.transcript
    assert "\x1b[" not in console.transcript
    assert "uv" in console.transcript


def test_migrations_are_at_head_only_when_every_head_is_applied() -> None:
    # frob:tests src/hullbreach_ops/dbstate.py::MigrationState.at_head kind="unit"
    assert MigrationState(current=["b", "a"], heads=["a", "b"]).at_head
    assert not MigrationState(current=["a"], heads=["b"]).at_head
    assert not MigrationState(current=[], heads=["a"]).at_head


def test_errors_print_as_their_plain_message() -> None:
    # frob:tests src/hullbreach_ops/errors.py::OpsError.__str__ kind="unit"
    # frob:tests src/hullbreach_ops/probe.py::HttpError.__str__ kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::ProcError.__str__ kind="unit"
    assert str(OpsError(message="db down", fix=["start it"])) == "db down"
    assert f"{HttpError(message='refused')}" == "refused"
    assert str(ProcError(kind="timeout", message="took too long")) == "took too long"


def test_db_container_health_and_exposure() -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::DbContainer.healthy kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::DbContainer.exposed_to_network kind="unit"
    up = DbContainer(name="db", state="running", health="healthy")
    assert up.healthy
    assert DbContainer(name="db", state="running").healthy
    assert not DbContainer(name="db", state="running", health="starting").healthy
    assert not DbContainer(name="db", state="exited", health="healthy").healthy
    local = DbContainer(name="db", state="running", published=["127.0.0.1:5432"])
    assert not local.exposed_to_network
    shared = DbContainer(name="db", state="running", published=["0.0.0.0:5432"])
    assert shared.exposed_to_network


def test_command_succeeds_only_on_exit_zero() -> None:
    # frob:tests src/hullbreach_ops/proc.py::CommandResult.succeeded kind="unit"
    assert CommandResult(argv=["true"], returncode=0).succeeded
    assert not CommandResult(argv=["false"], returncode=1).succeeded


def test_readme_section_links_to_its_anchor_on_github() -> None:
    # frob:tests src/hullbreach_ops/readme_links.py::ReadmeSection.url kind="unit"
    # frob:tests src/hullbreach_ops/readme_links.py::ReadmeSection.describe kind="unit"
    section = ReadmeSection(title="Step 5", anchor="step-5")
    assert section.url == f"{REPO_URL}#step-5"
    assert section.describe() == f"README 'Step 5': {REPO_URL}#step-5"


def test_settings_derive_paths_volume_and_urls(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.state_dir kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.logs_dir kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.run_dir kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.db_volume kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.api_url kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings.web_url kind="unit"
    env = {
        "HULLBREACH_PORT": "8004",
        "HULLBREACH_WEB_PORT": "5175",
        "COMPOSE_PROJECT_NAME": "hbtest",
    }
    s = OpsSettings.from_environ(env, tmp_path).danger_ok
    assert s.state_dir == tmp_path / ".hullbreach"
    assert s.logs_dir == tmp_path / ".hullbreach" / "logs"
    assert s.run_dir == tmp_path / ".hullbreach" / "run"
    assert s.db_volume == "hbtest_pgdata"
    assert s.api_url == "http://127.0.0.1:8004"
    assert s.web_url == "http://localhost:5175"
