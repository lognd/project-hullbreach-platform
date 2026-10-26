"""Doctor checks for settings and ports.

Settings are judged as set or not set and loaded through the server's own
loader; values are never printed. Every secret value seen is registered
with the console so it is redacted from any later output.
"""

from __future__ import annotations

import hmac
import re

from sqlalchemy import make_url
from sqlalchemy.exc import ArgumentError

from hullbreach_ops import lifecycle
from hullbreach_ops import readme_links as rl
from hullbreach_ops.accounts import GAME_KEYS_VAR, GAME_SIDE_KEY_VAR
from hullbreach_ops.checkbase import Check, CheckResult, DoctorRun, fail, ok, warn
from hullbreach_ops.checks_tools import check_compose_file
from hullbreach_ops.settings import (
    API_PORT_VAR,
    DB_PORT_VAR,
    WEB_PORT_VAR,
    load_app_config,
)
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_RERUN = "Run ./doctor.sh again."
_EDIT_ENV = "Open .env in a text editor (for example: nano .env)."
_MIN_KEY_LENGTH = 32

# Settings reported as set / not set; the bool marks secrets.
_REPORTED = (
    ("HULLBREACH_DATABASE_URL", True),
    ("POSTGRES_USER", False),
    ("POSTGRES_PASSWORD", True),
    ("POSTGRES_DB", False),
    ("HULLBREACH_ADMIN_USERNAME", False),
    ("HULLBREACH_ADMIN_EMAIL", False),
    ("HULLBREACH_ADMIN_PASSWORD", True),
    (GAME_KEYS_VAR, True),
    (API_PORT_VAR, False),
    (WEB_PORT_VAR, False),
    (DB_PORT_VAR, False),
)
_LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")


def check_env_file(run: DoctorRun) -> CheckResult:
    """A .env file exists (only its existence is checked; it is never read here)."""
    ctx = run.ctx
    if (ctx.settings.root / ".env").is_file():
        return ok(".env exists (its contents are checked by 'settings', never shown)")
    if ctx.environ.get("HULLBREACH_DATABASE_URL"):
        return warn(
            "no .env file; settings come from environment variables in this terminal",
            [
                "That works, but a new terminal will not have them. To keep them: "
                "cp .env.example .env and fill it in.",
            ],
            rl.SETTINGS,
        )
    return fail(
        "there is no .env settings file",
        [
            "Copy the example: cp .env.example .env",
            _EDIT_ENV,
            "Replace change-me-local-only with a password of your own in BOTH "
            "places (POSTGRES_PASSWORD and inside HULLBREACH_DATABASE_URL).",
            "Replace HULLBREACH_ADMIN_PASSWORD=changeme with a password of your own.",
            _RERUN,
        ],
        rl.SETTINGS,
    )


def _register_secrets(run: DoctorRun) -> None:
    """Make sure no secret setting value can ever be printed."""
    for name, secret in _REPORTED:
        if secret:
            for part in run.ctx.environ.get(name, "").split(","):
                run.ctx.console.add_secret(part.strip())
    run.ctx.console.add_secret(run.ctx.environ.get(GAME_SIDE_KEY_VAR))
    url = run.ctx.environ.get("HULLBREACH_DATABASE_URL", "")
    try:
        run.ctx.console.add_secret(make_url(url).password if url else None)
    except ArgumentError:
        _log.info("settings: database URL does not parse; whole value redacted")


def _url_mismatches(run: DoctorRun, url: str) -> list[str]:
    """Ways HULLBREACH_DATABASE_URL disagrees with the compose database settings."""
    env = run.ctx.environ
    try:
        parsed = make_url(url)
    except ArgumentError:
        return ["HULLBREACH_DATABASE_URL is not a valid database URL"]
    problems = []
    if parsed.host and parsed.host not in _LOCAL_HOSTS:
        _log.info("settings: database host is not local; skipping compose comparison")
        return []
    port = parsed.port or 5432
    if port != run.ctx.settings.db_port:
        problems.append(
            f"the port in HULLBREACH_DATABASE_URL is {port} but the database "
            f"container uses {run.ctx.settings.db_port} ({DB_PORT_VAR})"
        )
    user = env.get("POSTGRES_USER") or "hullbreach"
    if parsed.username != user:
        problems.append(
            "the user name in HULLBREACH_DATABASE_URL differs from POSTGRES_USER"
        )
    database = env.get("POSTGRES_DB") or "hullbreach"
    if parsed.database != database:
        problems.append(
            "the database name in HULLBREACH_DATABASE_URL differs from POSTGRES_DB"
        )
    password = env.get("POSTGRES_PASSWORD", "")
    if password and not hmac.compare_digest(
        (parsed.password or "").encode(), password.encode()
    ):
        problems.append(
            "the password inside HULLBREACH_DATABASE_URL differs from POSTGRES_PASSWORD"
        )
    return problems


def check_settings(run: DoctorRun) -> CheckResult:
    """Required settings are set and consistent (reported set/unset, never values)."""
    ctx = run.ctx
    _register_secrets(run)
    details = [
        f"{name}: {'set' if ctx.environ.get(name, '').strip() else 'not set'}"
        for name, _ in _REPORTED
    ]
    missing = [
        name
        for name in ("HULLBREACH_DATABASE_URL", "POSTGRES_PASSWORD")
        if not ctx.environ.get(name, "").strip()
    ]
    if missing:
        return fail(
            f"required setting(s) not set: {', '.join(missing)}",
            [
                "Create .env if you have not: cp .env.example .env",
                _EDIT_ENV,
                f"Give {' and '.join(missing)} a value (the password inside "
                "HULLBREACH_DATABASE_URL must equal POSTGRES_PASSWORD).",
                _RERUN,
            ],
            rl.SETTINGS,
            details,
        )
    loaded = load_app_config(ctx.settings)
    if loaded.is_err:
        err = loaded.danger_err
        return fail(err.message, err.fix, rl.SETTINGS, details)
    run.app_config = loaded.danger_ok
    problems = _url_mismatches(run, run.app_config.database_url)
    if problems:
        return fail(
            problems[0],
            [
                _EDIT_ENV,
                "Make HULLBREACH_DATABASE_URL match: "
                "postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@localhost:"
                f"<{DB_PORT_VAR}>/<POSTGRES_DB>",
                _RERUN,
            ],
            rl.SETTINGS,
            details + problems[1:],
        )
    admin = ctx.environ.get("HULLBREACH_ADMIN_PASSWORD", "")
    if not admin:
        return warn(
            "HULLBREACH_ADMIN_PASSWORD is not set: the first admin account cannot be "
            "created",
            [
                _EDIT_ENV,
                "Set HULLBREACH_ADMIN_PASSWORD to a password of your own.",
                _RERUN,
            ],
            rl.SETTINGS,
            details,
        )
    if admin == "changeme":
        return warn(
            "settings load, but HULLBREACH_ADMIN_PASSWORD is still the example value",
            [_EDIT_ENV, "Change HULLBREACH_ADMIN_PASSWORD to a password of your own."],
            rl.SETTINGS,
            details,
        )
    return ok("required settings are set and consistent", details)


def check_game_keys(run: DoctorRun) -> CheckResult:
    """Game-server keys are configured (required for the signed-in game demo)."""
    ctx = run.ctx
    assert run.app_config is not None  # settings PASSed or WARNed, so it loaded
    keys = [k.get_secret_value() for k in run.app_config.game_server_api_keys]
    keys = [k for k in keys if k]
    make_key = (
        "Make a key: uv run hullbreach_server server-key (it says where to put it)."
    )
    if not keys:
        message = (
            f"{GAME_KEYS_VAR} is empty: game servers cannot verify signed-in "
            "players (the website works without it)"
        )
        fix = [make_key, "Restart the API (stop, then start).", _RERUN]
        if run.needs_game:
            return fail(message, fix, rl.GAME)
        return warn(message, fix, rl.GAME)
    short = [k for k in keys if len(k) < _MIN_KEY_LENGTH]
    game_side = ctx.environ.get(GAME_SIDE_KEY_VAR, "")
    if game_side and not any(
        hmac.compare_digest(game_side.encode(), k.encode()) for k in keys
    ):
        return fail(
            f"{GAME_SIDE_KEY_VAR} is set here but matches none of {GAME_KEYS_VAR}",
            [
                f"Use one of the platform's keys as {GAME_SIDE_KEY_VAR} on the "
                "game server, or make a new one: uv run hullbreach_server server-key",
                _RERUN,
            ],
            rl.TROUBLE_GAME,
        )
    if short:
        return warn(
            f"{len(keys)} key(s) configured, {len(short)} shorter than "
            f"{_MIN_KEY_LENGTH} characters (easy to guess)",
            [make_key, "Replace the short key on both sides."],
            rl.GAME,
        )
    return ok(f"{len(keys)} game-server key(s) configured")


def _holder(run: DoctorRun, port: int) -> str:
    """Who listens on `port`: a container name, a process name, or 'unknown'."""
    ctx = run.ctx
    if ctx.runner.which("docker") is not None:
        result = ctx.runner.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Ports}}"], timeout=20
        )
        if result.is_ok and result.danger_ok.succeeded:
            for row in result.danger_ok.stdout.splitlines():
                name, _, ports = row.partition("|")
                if re.search(rf":{port}->", ports):
                    return f"docker container {name}"
    result = ctx.runner.run(["ss", "-ltnpH", f"sport = :{port}"], timeout=10)
    if result.is_ok and result.danger_ok.succeeded:
        found = re.search(r'users:\(\("([^"]+)",pid=(\d+)', result.danger_ok.stdout)
        if found:
            return f"{found.group(1)} (pid {found.group(2)})"
    result = ctx.runner.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"], timeout=10
    )
    if result.is_ok and result.danger_ok.succeeded:
        lines = result.danger_ok.stdout.splitlines()[1:]
        if lines:
            parts = lines[0].split()
            return f"{parts[0]} (pid {parts[1]})"
    return "a program this check cannot name (try: sudo ss -ltnp)"


def check_ports(run: DoctorRun) -> CheckResult:
    """The database, API and website ports are free or used by this platform."""
    ctx = run.ctx
    s = ctx.settings
    ours_db = ""
    if ctx.runner.which("docker") is not None:
        found = lifecycle.db_container(ctx)
        if found.is_ok and found.danger_ok is not None:
            ours_db = found.danger_ok.name
    details: list[str] = []
    conflicts: list[tuple[str, int, str, str, rl.ReadmeSection]] = []
    for label, port, var, service, section in (
        ("database", s.db_port, DB_PORT_VAR, None, rl.TROUBLE_DB),
        ("API", s.api_port, API_PORT_VAR, "api", rl.TROUBLE_API),
        ("website", s.web_port, WEB_PORT_VAR, "web", rl.TROUBLE_WEB),
    ):
        if not ctx.ports.port_open(port):
            details.append(f"{port} ({label}): free")
            continue
        holder = _holder(run, port)
        record = lifecycle.read_record(ctx, service) if service else None
        if (ours_db and ours_db in holder) or record is not None:
            details.append(f"{port} ({label}): used by this platform ({holder})")
            continue
        if service == "api":
            health = ctx.http.request("GET", f"{s.api_url}/api/v1/health", timeout=3.0)
            if health.is_ok and health.danger_ok.status == 200:
                details.append(f"{port} ({label}): a Hullbreach API started by hand")
                continue
        details.append(f"{port} ({label}): TAKEN by {holder}")
        conflicts.append((label, port, var, holder, section))
    if conflicts:
        label, port, var, holder, section = conflicts[0]
        return fail(
            f"port {port} ({label}) is already used by {holder}",
            [
                "Stop that program if you do not need it (an old copy of the "
                "platform: press Ctrl+C in its terminal, or run "
                "uv run hullbreach_server stop),",
                f"or use another port: set {var}=<free port> in .env"
                + (
                    " and change the port inside HULLBREACH_DATABASE_URL to match."
                    if var == DB_PORT_VAR
                    else "."
                ),
                _RERUN,
            ],
            section,
            details,
        )
    return ok(f"ports {s.db_port}, {s.api_port}, {s.web_port} are usable", details)


CONFIG_CHECKS = (
    Check("env-file", ".env settings file", check_env_file),
    # Listed after env-file: a missing .env is the cause to fix first.
    Check("compose-file", "docker-compose.yml valid", check_compose_file, ("docker",)),
    Check("settings", "Required settings", check_settings, ("py-deps",)),
    Check("game-keys", "Game-server keys", check_game_keys, ("settings",)),
    Check("ports", "Ports free", check_ports),
)
