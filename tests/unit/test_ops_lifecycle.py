"""Unit tests for start/stop/status/reset-db over fake docker, processes and HTTP."""

from __future__ import annotations

import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from ops_fakes import FakeHttp, FakeRunner, make_ctx, ok, output
from typani import Ok

from hullbreach_ops import lifecycle
from hullbreach_ops.console import Console
from hullbreach_ops.context import OpsContext
from hullbreach_ops.probe import HttpResponse

API_HEALTH = "http://127.0.0.1:8000/api/v1/health"
WEB_HOME = "http://127.0.0.1:5173/"
PS = ("docker", "compose", "-p", "platform", "ps")
HEALTHY = json.dumps(
    {
        "Name": "platform-db-1",
        "State": "running",
        "Health": "healthy",
        "Publishers": [
            {"URL": "127.0.0.1", "PublishedPort": 5432},
            {"URL": "::1", "PublishedPort": 0},
        ],
    }
)
ENV = {"POSTGRES_PASSWORD": "placeholder-pw"}


@pytest.fixture
def fake_db(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace migrations and seeding with recorders (no real database)."""
    done: list[str] = []
    cfg = SimpleNamespace(database_url="postgresql+psycopg://u:p@127.0.0.1/db")
    monkeypatch.setattr("hullbreach_ops.lifecycle.load_app_config", lambda _s: Ok(cfg))
    for step in ("connect", "migrate", "run_seed"):
        monkeypatch.setattr(
            lifecycle.dbstate,
            step,
            lambda _url, step=step: done.append(step) or Ok(None),
        )
    return done


def _http_up() -> FakeHttp:
    """API and website both answer."""
    return FakeHttp(
        routes={
            ("GET", API_HEALTH): HttpResponse(status=200, body="{}"),
            ("GET", WEB_HOME): HttpResponse(status=200, body="<html>"),
        }
    )


def _ctx(
    tmp_path: Path, runner: FakeRunner, http: FakeHttp, **kw: object
) -> OpsContext:
    """A context with the database settings start needs."""
    return make_ctx(tmp_path, ENV, runner=runner, http=http, **kw)  # type: ignore[arg-type]


def test_db_container_parses_compose_ps_lines_and_arrays(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::parse_compose_ps kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::DbContainer kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::db_container kind="unit"
    (row,) = lifecycle.parse_compose_ps(HEALTHY + "\nnot json\n")
    assert row.published == ["127.0.0.1:5432"]
    assert row.healthy and not row.exposed_to_network
    (arr,) = lifecycle.parse_compose_ps(
        '[{"Name": "x", "State": "exited", '
        '"Publishers": [{"URL": "0.0.0.0", "PublishedPort": 5432}]}]'
    )
    assert not arr.healthy and arr.exposed_to_network
    assert lifecycle.parse_compose_ps("") == []

    runner = FakeRunner(replies={PS: ok(HEALTHY)})
    found = lifecycle.db_container(make_ctx(tmp_path, runner=runner)).danger_ok
    assert found is not None and found.name == "platform-db-1"
    assert runner.calls[0] == [*PS, "--all", "--format", "json", "db"]
    broken = FakeRunner(replies={PS: ok(stderr="Cannot connect", returncode=1)})
    err = lifecycle.db_container(make_ctx(tmp_path, runner=broken)).danger_err
    assert err.message == "docker compose ps failed: Cannot connect"


def test_start_reports_a_compose_failure_with_fix_steps(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::start kind="unit"
    # frob:tests src/hullbreach_ops/errors.py::OpsError kind="unit"
    # frob:tests src/hullbreach_ops/context.py::OpsContext kind="unit"
    no_docker = FakeRunner(programs={"npm"})
    err = lifecycle.start(_ctx(tmp_path, no_docker, FakeHttp())).danger_err
    assert err.message == "docker is not installed (or not on PATH)"

    no_password = make_ctx(tmp_path)
    err = lifecycle.start(no_password).danger_err
    assert err.message == "POSTGRES_PASSWORD is not set, so the database cannot start"
    assert err.fix[0] == "Copy the example settings: cp .env.example .env"

    taken = FakeRunner(
        replies={
            ("docker", "compose", "-p", "platform", "up"): ok(
                stderr="Error: Bind for 127.0.0.1:5432 failed: port is already "
                "allocated",
                returncode=1,
            )
        }
    )
    err = lifecycle.start(_ctx(tmp_path, taken, FakeHttp())).danger_err
    assert err.message.startswith("docker compose up failed: Error: Bind for")
    assert any("HULLBREACH_DB_PORT" in step for step in err.fix)


def test_start_stop_records_and_ends_the_api_and_web(
    tmp_path: Path, fake_db: list[str]
) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::start kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::stop kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::stop_service kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::read_record kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::ProcessRecord kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::log_path kind="unit"
    runner = FakeRunner(replies={PS: ok(HEALTHY)})
    ctx = _ctx(tmp_path, runner, _http_up())
    assert lifecycle.start(ctx).is_ok
    assert fake_db == ["connect", "migrate", "run_seed"]
    api, web = runner.spawned
    assert api[1:] == [
        "-m",
        "hullbreach_server",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    assert web == [
        "/usr/bin/npm", "run", "dev", "--", "--host", "127.0.0.1",
        "--port", "5173", "--strictPort",
    ]  # fmt: skip
    assert runner.spawn_envs[1]["HULLBREACH_PORT"] == "8000"
    # The demo API logs payload summaries for the console unless opted out.
    assert runner.spawn_envs[0]["HULLBREACH_LOG_PAYLOADS"] == "1"
    assert lifecycle.read_record(ctx, "api").pid == 4101  # type: ignore[union-attr]
    assert lifecycle.log_path(ctx, "web").exists()
    assert "The platform is running" in output(ctx)

    # A second start reuses what runs instead of starting twice.
    again = _ctx(tmp_path, runner, _http_up())
    assert lifecycle.start(again).is_ok
    assert len(runner.spawned) == 2
    assert "API: already running (pid 4101)" in output(again)

    stopping = _ctx(tmp_path, runner, _http_up())
    assert lifecycle.stop(stopping).is_ok
    assert sorted(runner.terminated) == [4101, 4102]
    assert runner.ran("docker", "compose", "-p", "platform", "stop", "db")
    assert lifecycle.read_record(stopping, "api") is None
    assert "Database: stopped (your data is kept)" in output(stopping)

    after = _ctx(tmp_path, runner, FakeHttp())
    assert lifecycle.stop(after).is_ok
    assert "API: was not started by this tool" in output(after)


def test_start_restarts_an_api_that_outlived_a_stopped_database(
    tmp_path: Path, fake_db: list[str]
) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::start kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::db_up kind="unit"
    runner = FakeRunner(replies={PS: ok(HEALTHY)})
    assert lifecycle.start(_ctx(tmp_path, runner, _http_up())).is_ok
    (first_api, _web) = sorted(runner.alive)

    # The database container stopped; `up -d` brings it back healthy.
    runner.replies[PS] = ok(HEALTHY.replace('"running"', '"exited"'))
    up = ("docker", "compose", "-p", "platform", "up")
    runner.replies[up] = ok()
    original_run = runner.run

    def run(argv: list[str], **kw: object):  # type: ignore[no-untyped-def]
        if tuple(argv[: len(up)]) == up:
            runner.replies[PS] = ok(HEALTHY)
        return original_run(argv, **kw)  # type: ignore[arg-type]

    runner.run = run  # type: ignore[method-assign]
    again = _ctx(tmp_path, runner, _http_up())
    assert lifecycle.start(again).is_ok
    assert first_api in runner.terminated
    assert len(runner.spawned) == 3
    assert "API: restarting so it reconnects to the database" in output(again)
    assert "Website: already running" in output(again)

    # With the database already healthy, nothing is restarted.
    steady = _ctx(tmp_path, runner, _http_up())
    assert lifecycle.start(steady).is_ok
    assert len(runner.spawned) == 3
    assert "API: already running" in output(steady)


def test_start_reports_an_api_that_never_answers_with_its_log(
    tmp_path: Path, fake_db: list[str]
) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::start_api kind="unit"
    # frob:tests src/hullbreach_ops/lifecycle.py::log_tail kind="unit"
    runner = FakeRunner(replies={PS: ok(HEALTHY)})
    ctx = _ctx(tmp_path, runner, FakeHttp())
    log = lifecycle.log_path(ctx, "api")
    log.parent.mkdir(parents=True)
    log.write_text(
        "starting\nconnecting to postgresql://u:placeholder-pw@127.0.0.1/db\n"
        "sqlalchemy.exc.OperationalError: connection refused\n"
    )
    err = lifecycle.start(ctx).danger_err
    assert err.message == "the API did not start"
    assert err.fix[0] == f"Read the end of its log below (full log: {log})."
    assert "   | sqlalchemy.exc.OperationalError: connection refused" in err.fix
    assert not any("placeholder-pw" in step for step in err.fix)
    assert runner.terminated == [4101]
    assert lifecycle.read_record(ctx, "api") is None

    held = _ctx(tmp_path, FakeRunner(replies={PS: ok(HEALTHY)}), _http_up())
    held.ports.open_ports.add(8000)  # type: ignore[attr-defined]
    err = lifecycle.start(held).danger_err
    assert err.message == (
        "an API that this tool did not start is already running on port 8000"
    )
    other = _ctx(tmp_path, FakeRunner(replies={PS: ok(HEALTHY)}), FakeHttp())
    other.ports.open_ports.add(8000)  # type: ignore[attr-defined]
    err = lifecycle.start(other).danger_err
    assert err.message.startswith("port 8000 is already used by another program")


def test_status_lists_each_part(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::status kind="unit"
    ctx = make_ctx(tmp_path, runner=FakeRunner(replies={PS: ok("")}))
    assert lifecycle.status(ctx).is_ok
    text = output(ctx)
    assert "Platform status" in text
    assert "not created yet (run start)" in text
    assert text.count("not running (run start)") == 2

    up = make_ctx(
        tmp_path, runner=FakeRunner(replies={PS: ok(HEALTHY)}), http=_http_up()
    )
    assert lifecycle.status(up).is_ok
    assert "platform-db-1: running healthy" in output(up)
    assert f"answering at {API_HEALTH} (started by hand)" in output(up)


def test_reset_db_requires_the_exact_volume_name(
    tmp_path: Path, fake_db: list[str]
) -> None:
    # frob:tests src/hullbreach_ops/lifecycle.py::reset_db kind="unit"
    runner = FakeRunner(replies={PS: ok(HEALTHY)})
    err = lifecycle.reset_db(_ctx(tmp_path, runner, FakeHttp())).danger_err
    assert err.message == "reset-db needs a person at the keyboard to confirm"

    def asking(answer: str) -> Console:
        return Console(io.StringIO(), interactive=True, ask=lambda _q: answer)

    wrong = _ctx(tmp_path, runner, FakeHttp(), console=asking("yes"))
    assert lifecycle.reset_db(wrong).is_ok
    assert "Not confirmed; nothing was deleted." in output(wrong)
    assert not runner.ran("docker", "compose", "-p", "platform", "down")

    right = _ctx(tmp_path, runner, FakeHttp(), console=asking("platform_pgdata"))
    assert lifecycle.reset_db(right).is_ok
    assert runner.ran("docker", "compose", "-p", "platform", "down", "-v")
    assert "Deleted the database container and volume platform_pgdata" in output(right)
    assert fake_db == ["connect", "migrate", "run_seed"]
