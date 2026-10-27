"""Start, stop and inspect the local stack: database container, API and website.

One implementation behind `hullbreach_server start|stop|status|reset-db`
and the Makefile targets of the same names. The API and website run in the
background with their output in `.hullbreach/logs/`; their process ids are
recorded in `.hullbreach/run/` so `stop` ends exactly what `start` began.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ValidationError
from typani import Err, Ok, Result, propagate

from hullbreach_ops import dbstate
from hullbreach_ops import readme_links as rl
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.proc import CommandResult, ProcError
from hullbreach_ops.settings import (
    API_PORT_VAR,
    DB_PORT_VAR,
    WEB_PORT_VAR,
    load_app_config,
)
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

Service = Literal["api", "web"]
_LOG_NAMES: dict[Service, str] = {"api": "api.log", "web": "web.log"}
_DOCKER_FIX = [
    "Run ./doctor.sh; its docker and docker-daemon checks say exactly what is wrong.",
]
_DB_WAIT_SECONDS = 90.0
_API_WAIT_SECONDS = 45.0
_WEB_WAIT_SECONDS = 60.0


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_db_container_parses_compose_ps_lines_and_arrays
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class DbContainer(BaseModel):
    """The compose `db` service as `docker compose ps` reports it."""

    name: str
    state: str
    health: str = ""
    published: list[str] = []

    @property
    def healthy(self) -> bool:
        """True once Postgres answers its health check."""
        return self.state == "running" and self.health in ("healthy", "")

    @property
    def exposed_to_network(self) -> bool:
        """True when the port is published on every interface, not loopback only."""
        return any(not p.startswith("127.0.0.1:") for p in self.published)


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class ProcessRecord(BaseModel):
    """A background API or website process this tooling started."""

    pid: int
    host: str
    port: int


def compose_argv(ctx: OpsContext, *args: str) -> list[str]:
    """`docker compose -p <project> ...` for this checkout's compose project."""
    return ["docker", "compose", "-p", ctx.settings.compose_project, *args]


def _command_error(
    what: str, result: Result[CommandResult, ProcError], fix: list[str]
) -> OpsError:
    """An OpsError for a failed command, quoting the last lines it printed."""
    if result.is_err:
        detail = str(result.danger_err)
    else:
        done = result.danger_ok
        lines = (done.stderr or done.stdout).strip().splitlines()[-5:]
        detail = " | ".join(lines) or f"exit code {done.returncode}"
    return OpsError(message=f"{what} failed: {detail}", fix=fix)


def _run_ok(
    ctx: OpsContext, argv: list[str], what: str, fix: list[str], timeout: float = 120
) -> Result[CommandResult, OpsError]:
    """Run `argv` in the repo root; a non-zero exit is an Err with fix steps."""
    result = ctx.runner.run(
        argv, cwd=ctx.settings.root, env=ctx.environ, timeout=timeout
    )
    if result.is_ok and result.danger_ok.succeeded:
        return Ok(result.danger_ok)
    _log.warning("%s failed", what)
    return Err(_command_error(what, result, fix))


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_db_container_parses_compose_ps_lines_and_arrays
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def parse_compose_ps(text: str) -> list[DbContainer]:
    """Parse `docker compose ps --format json` output (JSON lines or one array)."""
    rows: list[dict] = []
    stripped = text.strip()
    if stripped.startswith("["):
        try:
            loaded = json.loads(stripped)
        except ValueError:
            loaded = []
        rows = [r for r in loaded if isinstance(r, dict)]
    else:
        for line in stripped.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    containers = []
    for row in rows:
        published = [
            f"{p.get('URL', '')}:{p.get('PublishedPort')}"
            for p in row.get("Publishers") or []
            if p.get("PublishedPort")
        ]
        containers.append(
            DbContainer(
                name=str(row.get("Name", "")),
                state=str(row.get("State", "")),
                health=str(row.get("Health", "")),
                published=published,
            )
        )
    return containers


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_db_container_parses_compose_ps_lines_and_arrays
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def db_container(ctx: OpsContext) -> Result[DbContainer | None, OpsError]:
    """This project's database container, or None when it was never created."""
    argv = compose_argv(ctx, "ps", "--all", "--format", "json", "db")
    result = _run_ok(ctx, argv, "docker compose ps", _DOCKER_FIX, timeout=30)
    found = parse_compose_ps(result.unwrap().stdout)
    return Ok(found[0] if found else None)


@propagate
def wait_for_db(
    ctx: OpsContext, timeout: float = _DB_WAIT_SECONDS
) -> Result[None, OpsError]:
    """Poll the container until Postgres reports healthy."""
    deadline = ctx.monotonic() + timeout
    while True:
        container = db_container(ctx).unwrap()
        if container is not None and container.state == "running":
            if container.health in ("healthy", ""):
                _log.info("database container is healthy")
                return Ok(None)
        if ctx.monotonic() >= deadline:
            state = "missing" if container is None else container.state
            health = "" if container is None else container.health
            return Err(
                OpsError(
                    message=f"the database container did not become healthy "
                    f"within {timeout:.0f}s (state: {state} {health})".rstrip(),
                    fix=[
                        "Show its log: docker compose -p "
                        f"{ctx.settings.compose_project} logs db",
                        "If the log says the password is wrong or the data "
                        f"directory is broken, see {rl.TROUBLE_DB.describe()}",
                    ],
                )
            )
        ctx.sleep(2.0)


@propagate
def db_up(ctx: OpsContext) -> Result[bool, OpsError]:
    """Create or start the database container; True when it was not already up."""
    if ctx.runner.which("docker") is None:
        return Err(
            OpsError(
                message="docker is not installed (or not on PATH)",
                fix=_DOCKER_FIX,
            )
        )
    if not ctx.environ.get("POSTGRES_PASSWORD"):
        return Err(
            OpsError(
                message="POSTGRES_PASSWORD is not set, so the database cannot start",
                fix=[
                    "Copy the example settings: cp .env.example .env",
                    "Open .env and set POSTGRES_PASSWORD (and the matching "
                    "password inside HULLBREACH_DATABASE_URL).",
                    "Run the same command again.",
                ],
            )
        )
    before = db_container(ctx).unwrap()
    was_up = before is not None and before.healthy
    _log.info("db_up: container already healthy=%s", was_up)
    ctx.console.line(
        f"  Database: starting container (compose project "
        f"{ctx.settings.compose_project}, port {ctx.settings.db_port})"
    )
    _run_ok(
        ctx,
        compose_argv(ctx, "up", "-d", "db"),
        "docker compose up",
        [
            *_DOCKER_FIX,
            f"If the port is taken, set {DB_PORT_VAR} in .env to a free port "
            "and update the port in HULLBREACH_DATABASE_URL to match.",
        ],
        timeout=600,
    ).unwrap()
    wait_for_db(ctx).unwrap()
    ctx.console.line("  Database: running and healthy")
    return Ok(not was_up)


@propagate
def prepare_db(ctx: OpsContext) -> Result[None, OpsError]:
    """Apply migrations and load the seed data (both idempotent)."""
    cfg = load_app_config(ctx.settings).unwrap()
    dbstate.connect(cfg.database_url).unwrap()
    dbstate.migrate(cfg.database_url).unwrap()
    ctx.console.line("  Database: migrations applied")
    dbstate.run_seed(cfg.database_url).unwrap()
    ctx.console.line("  Database: catalog and first admin account loaded")
    return Ok(None)


def _record_path(ctx: OpsContext, service: Service) -> Path:
    """Where the pid record of `service` lives."""
    return ctx.settings.run_dir / f"{service}.json"


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def read_record(ctx: OpsContext, service: Service) -> ProcessRecord | None:
    """The live process `start` recorded for `service`, or None (stale records are removed)."""  # noqa: E501
    path = _record_path(ctx, service)
    try:
        record = ProcessRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError):
        return None
    if ctx.runner.pid_alive(record.pid):
        return record
    _log.info("%s: recorded pid %d is gone; forgetting it", service, record.pid)
    path.unlink(missing_ok=True)
    return None


def _write_record(ctx: OpsContext, service: Service, record: ProcessRecord) -> None:
    """Remember a started process so `stop` can end it."""
    path = _record_path(ctx, service)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.model_dump_json(), encoding="utf-8")


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def log_path(ctx: OpsContext, service: Service) -> Path:
    """The log file the background `service` writes to."""
    return ctx.settings.logs_dir / _LOG_NAMES[service]


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_reports_an_api_that_never_answers_with_its_log
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def log_tail(path: Path, lines: int = 20) -> list[str]:
    """The last `lines` lines of a log file ([] when it does not exist)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()[-lines:]


def _wait_http(ctx: OpsContext, url: str, timeout: float) -> bool:
    """Poll `url` until it answers 200 or `timeout` passes."""
    deadline = ctx.monotonic() + timeout
    while True:
        result = ctx.http.request("GET", url, timeout=3.0)
        if result.is_ok and result.danger_ok.status == 200:
            return True
        if ctx.monotonic() >= deadline:
            return False
        ctx.sleep(1.0)


def _port_taken_error(port: int, var: str, what: str) -> OpsError:
    """Something else already listens where `what` should run."""
    return OpsError(
        message=f"port {port} is already used by another program, so the {what} "
        "cannot start there",
        fix=[
            "Run ./doctor.sh --only ports to see which program holds it.",
            "Stop that program (if it is an old copy of the platform, press "
            "Ctrl+C in its terminal),",
            f"or pick another port: set {var}=<free port> in .env.",
        ],
    )


def _service_failed(ctx: OpsContext, service: Service, message: str) -> OpsError:
    """A start failure with the redacted end of the service's log attached."""
    log = log_path(ctx, service)
    tail = [ctx.console.redact(line, log=True) for line in log_tail(log, 15)]
    fix = [f"Read the end of its log below (full log: {log})."]
    fix.extend(f"   | {line}" for line in tail)
    fix.append("Run ./doctor.sh for a full diagnosis.")
    return OpsError(message=message, fix=fix)


@propagate
def start_api(ctx: OpsContext, host: str) -> Result[ProcessRecord, OpsError]:
    """Start the API in the background on `host` (reusing one already started)."""
    port = ctx.settings.api_port
    existing = read_record(ctx, "api")
    if existing is not None and existing.host == host:
        ctx.console.line(f"  API: already running (pid {existing.pid})")
        return Ok(existing)
    if existing is not None:
        ctx.console.line(f"  API: restarting to listen on {host}")
        stop_service(ctx, "api")
    if ctx.ports.port_open(port):
        if _wait_http(ctx, f"{ctx.settings.api_url}/api/v1/health", 0):
            return Err(
                OpsError(
                    message=f"an API that this tool did not start is already "
                    f"running on port {port}",
                    fix=[
                        "Find the terminal running `uv run hullbreach_server` and "
                        "press Ctrl+C there,",
                        "then run the same command again.",
                    ],
                )
            )
        return Err(_port_taken_error(port, API_PORT_VAR, "API"))
    argv = [
        sys.executable,
        "-m",
        "hullbreach_server",
        "--host",
        host,
        "--port",
        str(port),
    ]
    pid = (
        ctx.runner.spawn(
            argv,
            cwd=ctx.settings.root,
            # Demo stack: console shows payload summaries unless opted out.
            env={
                "HULLBREACH_LOG_PAYLOADS": "1",
                **ctx.environ,
            },  # frob:ticket 01M5XX20F95MPV6YY454BQSNSF
            log_path=log_path(ctx, "api"),
        )
        .map_err(lambda e: OpsError(message=f"could not start the API: {e}"))
        .unwrap()
    )
    record = ProcessRecord(pid=pid, host=host, port=port)
    _write_record(ctx, "api", record)
    if not _wait_http(ctx, f"{ctx.settings.api_url}/api/v1/health", _API_WAIT_SECONDS):
        stop_service(ctx, "api")
        return Err(_service_failed(ctx, "api", "the API did not start"))
    ctx.console.line(f"  API: running on {host}:{port} (pid {pid})")
    return Ok(record)


@propagate
def start_web(ctx: OpsContext, host: str) -> Result[ProcessRecord, OpsError]:
    """Start the vite dev server in the background on `host`."""
    port = ctx.settings.web_port
    existing = read_record(ctx, "web")
    if existing is not None and existing.host == host:
        ctx.console.line(f"  Website: already running (pid {existing.pid})")
        return Ok(existing)
    if existing is not None:
        ctx.console.line(f"  Website: restarting to listen on {host}")
        stop_service(ctx, "web")
    if ctx.ports.port_open(port):
        return Err(_port_taken_error(port, WEB_PORT_VAR, "website"))
    npm = ctx.runner.which("npm")
    if npm is None:
        return Err(
            OpsError(
                message="npm is not installed (or not on PATH)",
                fix=["Run ./doctor.sh; its node check explains how to install it."],
            )
        )
    env = dict(ctx.environ)
    env[API_PORT_VAR] = str(ctx.settings.api_port)
    env[WEB_PORT_VAR] = str(port)
    argv = [
        npm,
        "run",
        "dev",
        "--",
        "--host",
        host,
        "--port",
        str(port),
        "--strictPort",
    ]
    pid = (
        ctx.runner.spawn(
            argv, cwd=ctx.settings.root, env=env, log_path=log_path(ctx, "web")
        )
        .map_err(lambda e: OpsError(message=f"could not start the website: {e}"))
        .unwrap()
    )
    record = ProcessRecord(pid=pid, host=host, port=port)
    _write_record(ctx, "web", record)
    if not _wait_http(ctx, f"http://127.0.0.1:{port}/", _WEB_WAIT_SECONDS):
        stop_service(ctx, "web")
        return Err(_service_failed(ctx, "web", "the website did not start"))
    ctx.console.line(f"  Website: running on {host}:{port} (pid {pid})")
    return Ok(record)


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def stop_service(ctx: OpsContext, service: Service) -> bool:
    """End the recorded `service` process; False when none was running."""
    record = read_record(ctx, service)
    if record is None:
        return False
    ctx.runner.terminate(record.pid)
    _record_path(ctx, service).unlink(missing_ok=True)
    _log.info("%s: stopped pid %d", service, record.pid)
    return True


def print_urls(ctx: OpsContext, host: str) -> None:
    """Tell the operator where everything is and what they should see."""
    s = ctx.settings
    ctx.console.heading("The platform is running")
    ctx.console.line(f"  Website:  {s.web_url}")
    ctx.console.line(f"  API:      {s.api_url}/api/v1/health")
    ctx.console.line(f"  Logs:     {s.logs_dir}")
    ctx.console.line()
    ctx.console.line("What you should see:")
    ctx.console.line(
        f"  - Open {s.web_url} in a browser: the Hullbreach home page with "
        "Sign in and Create account."
    )
    ctx.console.line(f'  - {s.api_url}/api/v1/health shows {{"status":"ok",...}}.')
    if host != "127.0.0.1":
        ctx.console.line(
            "  - Other computers use this computer's network address; "
            "`uv run hullbreach_server lan` prints it."
        )
    ctx.console.line()
    ctx.console.line(
        "Stop everything with: uv run hullbreach_server stop   (or: make stop)"
    )


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_reports_a_compose_failure_with_fix_steps
# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def start(ctx: OpsContext, host: str | None = None) -> Result[None, OpsError]:
    """Database up and healthy, migrated and seeded, then API and website.

    Safe to run again: whatever is already running is reused.
    """
    bind = host or ctx.settings.api_host
    _log.info("start: host=%s", bind)
    ctx.console.heading("Starting the platform")
    restarted = db_up(ctx).unwrap()
    if restarted and read_record(ctx, "api") is not None:
        # An API that outlived its database holds dead pooled connections.
        _log.info("start: database was restarted; restarting the API too")
        ctx.console.line("  API: restarting so it reconnects to the database")
        stop_service(ctx, "api")
    prepare_db(ctx).unwrap()
    start_api(ctx, bind).unwrap()
    start_web(ctx, bind).unwrap()
    print_urls(ctx, bind)
    return Ok(None)


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_stop_records_and_ends_the_api_and_web
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def stop(ctx: OpsContext) -> Result[None, OpsError]:
    """Stop the website, the API and the database container (data is kept)."""
    ctx.console.heading("Stopping the platform")
    for service, label in (("web", "Website"), ("api", "API")):
        if stop_service(ctx, service):
            ctx.console.line(f"  {label}: stopped")
        else:
            ctx.console.line(f"  {label}: was not started by this tool")
    if ctx.ports.port_open(ctx.settings.api_port):
        ctx.console.line(
            f"  Something still listens on port {ctx.settings.api_port}: if you "
            "started the API by hand, press Ctrl+C in its terminal."
        )
    if ctx.runner.which("docker") is not None:
        _run_ok(
            ctx, compose_argv(ctx, "stop", "db"), "docker compose stop", _DOCKER_FIX
        ).unwrap()
        ctx.console.line("  Database: stopped (your data is kept)")
    return Ok(None)


# frob:tests tests/unit/test_ops_lifecycle.py::test_status_lists_each_part
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def status(ctx: OpsContext) -> Result[None, OpsError]:
    """Print whether the database, API and website are running."""
    s = ctx.settings
    ctx.console.heading("Platform status")
    if ctx.runner.which("docker") is None:
        ctx.console.status("FAIL", "database", "docker is not installed")
    else:
        found = db_container(ctx)
        if found.is_err:
            ctx.console.status("FAIL", "database", str(found.danger_err))
        elif found.danger_ok is None:
            ctx.console.status("WARN", "database", "not created yet (run start)")
        else:
            c = found.danger_ok
            label = "PASS" if c.healthy else "WARN"
            ctx.console.status(
                label, "database", f"{c.name}: {c.state} {c.health}".rstrip()
            )
    for service, label, url in (
        ("api", "api", f"{s.api_url}/api/v1/health"),
        ("web", "website", f"http://127.0.0.1:{s.web_port}/"),
    ):
        record = read_record(ctx, service)
        answer = ctx.http.request("GET", url, timeout=3.0)
        up = answer.is_ok and answer.danger_ok.status == 200
        owner = (
            f"started by this tool, pid {record.pid}" if record else "started by hand"
        )
        if up:
            ctx.console.status("PASS", label, f"answering at {url} ({owner})")
        elif record is not None:
            ctx.console.status(
                "WARN", label, f"process {record.pid} runs but {url} does not answer"
            )
        else:
            ctx.console.status("WARN", label, "not running (run start)")
    return Ok(None)


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_reset_db_requires_the_exact_volume_name
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def reset_db(ctx: OpsContext) -> Result[None, OpsError]:
    """Delete this project's database volume and rebuild it, after confirmation."""
    s = ctx.settings
    ctx.console.heading("Reset the database")
    ctx.console.line(
        "THIS DELETES EVERY ACCOUNT, MATCH AND SETTING IN THE LOCAL DATABASE."
    )
    ctx.console.line(f"  Compose project: {s.compose_project}")
    ctx.console.line(f"  Docker volume:   {s.db_volume}")
    ctx.console.line("It cannot be undone. Other compose projects are not touched.")
    if not ctx.console.interactive:
        return Err(
            OpsError(
                message="reset-db needs a person at the keyboard to confirm",
                fix=["Run it in a terminal: uv run hullbreach_server reset-db"],
            )
        )
    typed = ctx.console.ask_text(f"Type the volume name ({s.db_volume}) to continue: ")
    if typed != s.db_volume:
        ctx.console.line("Not confirmed; nothing was deleted.")
        _log.info("reset-db: not confirmed")
        return Ok(None)
    _log.warning("reset-db: deleting volume %s", s.db_volume)
    for service in ("web", "api"):
        if stop_service(ctx, service):
            ctx.console.line(f"  Stopped the {service} (it was using the database)")
    _run_ok(
        ctx, compose_argv(ctx, "down", "-v"), "docker compose down -v", _DOCKER_FIX
    ).unwrap()
    ctx.console.line(f"  Deleted the database container and volume {s.db_volume}")
    db_up(ctx).unwrap()
    prepare_db(ctx).unwrap()
    ctx.console.line()
    ctx.console.line(
        "Done. Start the API and website again with: uv run hullbreach_server start"
    )
    return Ok(None)
