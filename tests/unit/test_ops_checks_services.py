"""Unit tests for the doctor's API, website, sign-in and LAN checks."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from ops_fakes import FakeHttp, FakeRunner, make_ctx, ok
from pydantic import SecretStr
from typani import Err, Ok, Result

from hullbreach_ops import checks_runtime as cr
from hullbreach_ops.checkbase import DoctorRun, Status
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import ProcessRecord
from hullbreach_ops.probe import HttpResponse
from hullbreach_ops.settings import PlatformInfo

API = "http://127.0.0.1:8000"
HEALTH = HttpResponse(status=200, body='{"status": "ok", "version": "0.1.0"}')
PAGE = HttpResponse(status=200, body='<html><div id="root"></div></html>')


def _run(
    tmp_path: Path, environ: dict[str, str] | None = None, **kw: object
) -> DoctorRun:
    run = DoctorRun(ctx=make_ctx(tmp_path, environ, **kw))  # type: ignore[arg-type]
    run.app_config = SimpleNamespace(  # type: ignore[assignment]
        database_url="postgresql+psycopg://u:p@127.0.0.1/db",
        game_server_api_keys=[SecretStr("k" * 40)],
    )
    return run


def _finish(run: DoctorRun) -> None:
    """Run the cleanups the way run_checks does at the end of a doctor run."""
    for cleanup in reversed(run.cleanups):
        cleanup()


def test_api_already_running_passes_without_starting_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_api kind="unit"
    def no_start(ctx: OpsContext, host: str) -> Result[ProcessRecord, OpsError]:
        raise AssertionError("the API answered; nothing should start")

    monkeypatch.setattr(cr.lifecycle, "start_api", no_start)
    http = FakeHttp(routes={("GET", f"{API}/api/v1/health"): HEALTH})
    run = _run(tmp_path, http=http)
    result = cr.check_api(run)
    assert result.status == Status.PASS
    assert "version 0.1.0" in result.summary
    assert result.details == ["started by hand"]
    assert run.cleanups == []


def test_api_started_for_the_check_is_stopped_afterwards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_api kind="unit"
    http = FakeHttp()
    stopped: list[str] = []

    def start(ctx: OpsContext, host: str) -> Result[ProcessRecord, OpsError]:
        assert host == "127.0.0.1"
        http.routes[("GET", f"{API}/api/v1/health")] = HEALTH
        return Ok(ProcessRecord(pid=4200, host=host, port=8000))

    monkeypatch.setattr(cr.lifecycle, "start_api", start)
    monkeypatch.setattr(
        cr.lifecycle, "stop_service", lambda ctx, svc: bool(stopped.append(svc))
    )
    run = _run(tmp_path, http=http)
    result = cr.check_api(run)
    assert result.status == Status.PASS
    assert "started by the doctor" in result.details[0]
    _finish(run)
    assert stopped == ["api"]


def test_api_that_will_not_start_fails_with_its_log_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_api kind="unit"
    def start(ctx: OpsContext, host: str) -> Result[ProcessRecord, OpsError]:
        return Err(
            OpsError(
                message="the API stopped while starting",
                fix=["   | configuration error: database_url: Field required"],
            )
        )

    monkeypatch.setattr(cr.lifecycle, "start_api", start)
    run = _run(tmp_path)
    result = cr.check_api(run)
    assert result.status == Status.FAIL
    assert result.summary == "the API stopped while starting"
    assert "uv run hullbreach_server --port 8000" in result.fix[0]
    assert "   | configuration error" in result.fix[1]
    assert run.notes == []
    assert run.cleanups == []


def test_web_passes_when_the_page_and_api_proxy_answer(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_web kind="unit"
    http = FakeHttp(
        routes={
            ("GET", "http://localhost:5173/"): PAGE,
            ("GET", "http://localhost:5173/api/v1/health"): HEALTH,
        }
    )
    result = cr.check_web(_run(tmp_path, http=http))
    assert result.status == Status.PASS
    assert "reaches the API through /api" in result.summary


def test_web_names_the_api_port_when_the_proxy_fails(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_web kind="unit"
    http = FakeHttp(
        routes={
            ("GET", "http://127.0.0.1:5175/"): PAGE,
            ("GET", "http://127.0.0.1:5175/api/v1/health"): HttpResponse(
                status=502, body=""
            ),
        }
    )
    env = {"HULLBREACH_WEB_PORT": "5175", "HULLBREACH_PORT": "8004"}
    result = cr.check_web(_run(tmp_path, env, http=http))
    assert result.status == Status.FAIL
    assert "port 8004" in result.summary
    assert "HULLBREACH_PORT" in result.fix[0]


def test_web_fails_when_another_program_serves_the_port(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_web kind="unit"
    other = HttpResponse(status=200, body="<html>someone else</html>")
    http = FakeHttp(routes={("GET", "http://localhost:5173/"): other})
    result = cr.check_web(_run(tmp_path, http=http))
    assert result.status == Status.FAIL
    assert "does not serve the Hullbreach page" in result.summary
    assert any("--only ports" in step for step in result.fix)


def _e2e_routes(fail_patch: bool = False) -> dict[tuple[str, str], HttpResponse]:
    v1 = f"{API}/api/v1"
    return {
        ("POST", f"{v1}/auth/register"): HttpResponse(status=201, body="{}"),
        ("POST", f"{v1}/auth/login"): HttpResponse(
            status=200, body='{"token": "tok-secret-123"}'
        ),
        ("GET", f"{v1}/me"): HttpResponse(status=200, body="{}"),
        ("PATCH", f"{v1}/me"): HttpResponse(
            status=400 if fail_patch else 200,
            body='{"detail": "wrong password"}' if fail_patch else "{}",
        ),
        ("GET", f"{v1}/me/matches"): HttpResponse(status=200, body="[]"),
    }


def test_e2e_walks_the_account_and_deletes_the_throwaway_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_e2e kind="unit"
    deleted: list[str] = []

    def delete_user(url: str, username: str) -> Result[bool, OpsError]:
        deleted.append(username)
        return Ok(True)

    monkeypatch.setattr(cr.dbstate, "delete_user", delete_user)
    http = FakeHttp(routes=_e2e_routes())
    run = _run(tmp_path, http=http)
    result = cr.check_e2e(run)
    assert result.status == Status.PASS
    assert result.details[0] == "created throwaway account doctor-20261015123000"
    assert run.session_token == "tok-secret-123"
    register = http.requests[0]
    password = register[3]["password"]  # type: ignore[index]
    run.ctx.console.line(f"leak? {password} tok-secret-123")
    assert password not in run.ctx.console.transcript
    assert "tok-secret-123" not in run.ctx.console.transcript
    assert deleted == []
    _finish(run)
    assert deleted == ["doctor-20261015123000"]


def test_e2e_failure_names_the_step_and_still_cleans_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_e2e kind="unit"
    monkeypatch.setattr(cr.dbstate, "delete_user", lambda url, name: Ok(False))
    run = _run(tmp_path, http=FakeHttp(routes=_e2e_routes(fail_patch=True)))
    result = cr.check_e2e(run)
    assert result.status == Status.FAIL
    assert result.summary.startswith("change email (PATCH /me): expected HTTP 200")
    assert "wrong password" in result.summary
    _finish(run)
    assert "could not delete the test account" in run.ctx.console.transcript


def test_e2e_with_no_api_fails_without_a_cleanup(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_e2e kind="unit"
    run = _run(tmp_path)
    result = cr.check_e2e(run)
    assert result.status == Status.FAIL
    assert result.summary == "create account: no answer from the API"
    assert run.cleanups == []


def test_lan_warns_on_loopback_and_passes_on_all_interfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_lan kind="unit"
    monkeypatch.setattr(cr.lan, "lan_ips", lambda ctx: ["192.168.1.23"])
    local = cr.check_lan(_run(tmp_path))
    assert local.status == Status.WARN
    assert "only this computer" in local.summary
    assert "uv run hullbreach_server lan" in local.fix[0]
    shared = cr.check_lan(_run(tmp_path, {"HULLBREACH_HOST": "0.0.0.0"}))
    assert shared.status == Status.PASS
    assert "192.168.1.23" in shared.details[1]


def test_lan_on_wsl_nat_wants_the_windows_port_forward(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_lan kind="unit"
    monkeypatch.setattr(cr.lan, "lan_ips", lambda ctx: ["192.168.1.23"])
    wsl = PlatformInfo(system="Linux", release="6.6-microsoft", wsl=True, wsl_version=2)
    env = {"HULLBREACH_HOST": "0.0.0.0"}
    eth0 = "2: eth0    inet 172.20.1.5/20 brd 172.20.15.255 scope global eth0"
    runner = FakeRunner(
        replies={
            ("wslinfo",): ok("nat\n"),
            ("ip", "-4", "-o", "addr", "show", "eth0"): ok(eth0),
            ("netsh.exe",): ok(""),
        }
    )
    missing = cr.check_lan(_run(tmp_path, env, runner=runner, platform=wsl))
    assert missing.status == Status.WARN
    assert "not forwarding" in missing.summary
    rules = "0.0.0.0  8000  172.20.1.5  8000\n0.0.0.0  5173  172.20.1.5  5173\n"
    runner.replies[("netsh.exe",)] = ok(rules)
    forwarded = cr.check_lan(_run(tmp_path, env, runner=runner, platform=wsl))
    assert forwarded.status == Status.PASS
