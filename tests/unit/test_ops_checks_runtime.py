"""Unit tests for the doctor's database, API and game-session checks."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace

import pytest
from ops_fakes import FakeRunner, make_ctx, ok
from pydantic import SecretStr
from typani import Err, Ok, Result

from hullbreach_ops import checks_runtime as cr
from hullbreach_ops import dbstate
from hullbreach_ops.checkbase import DoctorRun, Status
from hullbreach_ops.errors import OpsError
from hullbreach_ops.probe import HttpError, HttpResponse

PS = ("docker", "compose", "-p", "platform", "ps")
KEY = "k" * 40
SESSION = "http://127.0.0.1:8000/api/v1/auth/session"


def _row(state: str = "running", health: str = "healthy", port: int = 5432) -> str:
    return json.dumps(
        {
            "Name": "platform-db-1",
            "State": state,
            "Health": health,
            "Publishers": [{"URL": "127.0.0.1", "PublishedPort": port}],
        }
    )


def _run(tmp_path: Path, **kw: object) -> DoctorRun:
    run = DoctorRun(ctx=make_ctx(tmp_path, **kw))  # type: ignore[arg-type]
    run.app_config = SimpleNamespace(  # type: ignore[assignment]
        database_url="postgresql+psycopg://u:p@127.0.0.1/db",
        game_server_api_keys=[SecretStr(KEY)],
    )
    return run


def test_db_container_missing_stopped_unhealthy_and_wrong_port(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_db_container kind="unit"
    def check(reply: str) -> object:
        runner = FakeRunner(replies={PS: ok(reply)})
        return cr.check_db_container(_run(tmp_path, runner=runner))

    missing = check("")
    assert "does not exist yet" in missing.summary  # type: ignore[attr-defined]
    assert missing.fix[0].startswith("Start everything")  # type: ignore[attr-defined]
    stopped = check(_row(state="exited"))
    assert stopped.summary == "the database container platform-db-1 is exited"  # type: ignore[attr-defined]
    unhealthy = check(_row(health="starting"))
    assert "logs db" in unhealthy.fix[0]  # type: ignore[attr-defined]
    moved = check(_row(port=5434))
    assert "but the settings expect 5432" in moved.summary  # type: ignore[attr-defined]
    assert check(_row()).status == Status.PASS  # type: ignore[attr-defined]


def test_db_connect_explains_a_password_the_database_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_db_connect kind="unit"
    monkeypatch.setattr(
        dbstate,
        "connect",
        lambda _u: Err(OpsError(message="password authentication failed")),
    )
    result = cr.check_db_connect(_run(tmp_path))
    assert result.status == Status.FAIL
    assert "FIRST created" in result.fix[0]
    assert any("reset-db" in step for step in result.fix)


def test_migrations_and_seed_name_the_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_migrations kind="unit"
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_seed kind="unit"
    monkeypatch.setattr(
        dbstate,
        "migration_state",
        lambda _u: Ok(dbstate.MigrationState(current=[], heads=["abc123"])),
    )
    behind = cr.check_migrations(_run(tmp_path))
    assert behind.status == Status.FAIL
    assert behind.fix[0] == cr._UPGRADE
    assert "database at: nothing applied" in behind.details
    monkeypatch.setattr(
        dbstate, "seed_state", lambda _u: Ok(dbstate.SeedState(items=0, admins=0))
    )
    assert cr.check_seed(_run(tmp_path)).fix[0] == cr._SEED
    monkeypatch.setattr(
        dbstate, "seed_state", lambda _u: Ok(dbstate.SeedState(items=12, admins=0))
    )
    assert cr.check_seed(_run(tmp_path)).status == Status.WARN


class SessionApi:
    """A fake /auth/session that checks X-Server-Key like the real one."""

    def __init__(self, known: str | None) -> None:
        self.known = known

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: object = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """Answer like the API whose configured key is `known`."""
        assert url == SESSION
        given = dict(headers or {})
        key = given.get("X-Server-Key")

        def no(detail: str, status: int = 401) -> HttpResponse:
            return HttpResponse(status=status, body=json.dumps({"detail": detail}))

        if self.known is None:
            return Ok(no("server key not configured", 503))
        if key is None:
            return Ok(no("server key missing"))
        if key != self.known:
            return Ok(no("invalid server key"))
        if given.get("Authorization") != "Bearer player-token":
            return Ok(no("not authenticated"))
        return Ok(HttpResponse(status=200, body='{"username": "doctor-x"}'))


def test_game_session_accepts_only_the_right_key(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_runtime.py::check_game_session kind="unit"
    def check(api_key: str | None) -> object:
        run = _run(tmp_path, http=SessionApi(api_key))
        run.session_token = "player-token"
        return cr.check_game_session(run)

    good = check(KEY)
    assert good.status == Status.PASS  # type: ignore[attr-defined]
    assert len(good.details) == 4  # type: ignore[attr-defined]
    stale = check("an-older-key")
    assert stale.status == Status.FAIL  # type: ignore[attr-defined]
    assert "does not know the key" in stale.summary  # type: ignore[attr-defined]
    assert "Restart the API" in stale.fix[0]  # type: ignore[attr-defined]
    unconfigured = check(None)
    assert "running API has no keys" in unconfigured.summary  # type: ignore[attr-defined]
