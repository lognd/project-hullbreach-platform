"""Doctor checks for the running stack: database, API, website, sign-in, LAN.

When the API or website is not running, the doctor starts it for the check
and stops it again afterwards, so the result says whether `start` would work.
The end-to-end probe registers a throwaway `doctor-<timestamp>` account and
deletes it at the end of the run.
"""

from __future__ import annotations

import dataclasses
import secrets

from hullbreach_ops import dbstate, lan, lifecycle
from hullbreach_ops import readme_links as rl
from hullbreach_ops.accounts import GAME_KEYS_VAR
from hullbreach_ops.checkbase import Check, CheckResult, DoctorRun, fail, ok, warn
from hullbreach_ops.context import OpsContext
from hullbreach_ops.lifecycle import Service
from hullbreach_ops.probe import HttpResponse
from hullbreach_ops.settings import API_PORT_VAR, DB_PORT_VAR
from hullbreach_server.logging import get_logger, sanitize_for_log

_log = get_logger(__name__)

_RERUN = "Run ./doctor.sh again."
_START = "Start everything: uv run hullbreach_server start"
_UPGRADE = "Apply the migrations: uv run hullbreach_server db upgrade"
_SEED = "Load the seed data: uv run hullbreach_server db seed"
_LOOPBACK = "127.0.0.1"


def _database_url(run: DoctorRun) -> str:
    """The database URL (the settings check, which these checks need, loaded it)."""
    assert run.app_config is not None  # every caller needs the settings check
    return run.app_config.database_url


def check_db_container(run: DoctorRun) -> CheckResult:
    """This project's Postgres container exists, runs, is healthy, on the right port."""
    ctx = run.ctx
    s = ctx.settings
    found = lifecycle.db_container(ctx)
    if found.is_err:
        err = found.danger_err
        return fail(err.message, err.fix, rl.TROUBLE_DB)
    container = found.danger_ok
    start_fix = [_START, _RERUN]
    if container is None:
        return fail(
            f"the database container of compose project {s.compose_project} does "
            "not exist yet",
            start_fix,
            rl.START,
        )
    if container.state != "running":
        return fail(
            f"the database container {container.name} is {container.state}",
            start_fix,
            rl.TROUBLE_DB,
        )
    if not container.healthy:
        return fail(
            f"the database container {container.name} is {container.health}",
            [
                f"Look at its log: docker compose -p {s.compose_project} logs db",
                "If it is still starting, wait 30 seconds.",
                _RERUN,
            ],
            rl.TROUBLE_DB,
        )
    details = [f"published: {', '.join(container.published) or 'nothing'}"]
    ports = {p.rsplit(":", 1)[-1] for p in container.published}
    if str(s.db_port) not in ports:
        return fail(
            f"{container.name} publishes port {', '.join(sorted(ports)) or 'none'}, "
            f"but the settings expect {s.db_port}",
            [
                f"Recreate it on the expected port: docker compose -p "
                f"{s.compose_project} up -d db",
                f"Or set {DB_PORT_VAR} (and the port in HULLBREACH_DATABASE_URL) "
                "to the published port.",
                _RERUN,
            ],
            rl.TROUBLE_DB,
            details,
        )
    if container.exposed_to_network:
        return warn(
            f"{container.name} accepts connections from other computers",
            [
                "The database should only listen on 127.0.0.1 (invariant INV-005).",
                "Undo local edits: git checkout docker-compose.yml",
                f"Recreate it: docker compose -p {s.compose_project} up -d db",
            ],
            rl.TROUBLE_DB,
            details,
        )
    return ok(f"{container.name} is running and healthy on port {s.db_port}", details)


def check_db_connect(run: DoctorRun) -> CheckResult:
    """The API's database URL opens a connection."""
    result = dbstate.connect(_database_url(run))
    if result.is_ok:
        return ok("connected with HULLBREACH_DATABASE_URL")
    message = result.danger_err.message
    fix = [_START, _RERUN]
    if "password" in message:
        fix = [
            "The database remembers the password it was FIRST created with; "
            "changing POSTGRES_PASSWORD later does not change it.",
            "Either put the original password back in .env (both places),",
            "or delete the local database and start over (deletes all local "
            "accounts): uv run hullbreach_server reset-db",
            _RERUN,
        ]
    elif "does not exist" in message:
        fix = [
            "Make POSTGRES_USER, POSTGRES_DB and HULLBREACH_DATABASE_URL agree "
            "in .env.",
            "The database keeps the user and name it was first created with; "
            "to start over: uv run hullbreach_server reset-db",
            _RERUN,
        ]
    return fail(message, fix, rl.TROUBLE_DB)


def check_migrations(run: DoctorRun) -> CheckResult:
    """Every database migration has been applied."""
    found = dbstate.migration_state(_database_url(run))
    if found.is_err:
        return fail(found.danger_err.message, [_UPGRADE, _RERUN], rl.TROUBLE_DB)
    state = found.danger_ok
    details = [f"database at: {', '.join(state.current) or 'nothing applied'}"]
    details.append(f"newest:      {', '.join(state.heads)}")
    if state.at_head:
        return ok("all migrations are applied", details)
    return fail(
        "the database is missing migrations (its tables are out of date)",
        [_UPGRADE, "(start does this for you: uv run hullbreach_server start)", _RERUN],
        rl.TROUBLE_DB,
        details,
    )


def check_seed(run: DoctorRun) -> CheckResult:
    """The catalog items and the first admin account are loaded."""
    found = dbstate.seed_state(_database_url(run))
    if found.is_err:
        return fail(found.danger_err.message, [_SEED, _RERUN], rl.TROUBLE_DB)
    state = found.danger_ok
    details = [f"catalog items: {state.items}", f"admin accounts: {state.admins}"]
    if state.items == 0:
        return fail(
            "the item catalog is empty", [_SEED, _RERUN], rl.TROUBLE_DB, details
        )
    if state.admins == 0:
        return warn(
            "no admin account exists",
            [
                "Set HULLBREACH_ADMIN_PASSWORD in .env (and HULLBREACH_ADMIN_USERNAME "
                "if you want another name than admin).",
                _SEED,
            ],
            rl.SETTINGS,
            details,
        )
    return ok("catalog and admin account are loaded", details)


def _quiet(run: DoctorRun) -> OpsContext:
    """The run's context with console output muted (for starting services)."""
    return dataclasses.replace(run.ctx, console=run.ctx.console.muted())


def _answers(run: DoctorRun, service: Service) -> bool:
    """Whether `service` answers HTTP 200 on its local port right now."""
    if service == "web":
        page = _web_get(run, "/")
        return page is not None and page.status == 200
    url = f"{run.ctx.settings.api_url}/api/v1/health"
    answer = run.ctx.http.request("GET", url, timeout=3.0)
    return answer.is_ok and answer.danger_ok.status == 200


def _ensure_running(run: DoctorRun, service: Service) -> tuple[str, str]:
    """Make `service` answer, starting it for this run if needed.

    Returns (who started it, error message); the error is "" on success.
    """
    ctx = run.ctx
    if _answers(run, service):
        record = lifecycle.read_record(ctx, service)
        owner = (
            f"started by `start`, pid {record.pid}, on {record.host}"
            if record
            else "started by hand"
        )
        return owner, ""
    quiet = _quiet(run)
    if service == "api":
        started = lifecycle.start_api(quiet, _LOOPBACK)
    else:
        started = lifecycle.start_web(quiet, _LOOPBACK)
    if started.is_err:
        err = started.danger_err
        run.notes.extend(err.fix)
        return "", err.message
    _log.info("doctor: started %s for the checks", service)

    def stop() -> None:
        """Stop what the doctor started, leaving the computer as it was."""
        lifecycle.stop_service(ctx, service)

    run.cleanups.append(stop)
    return "started by the doctor for this check; stopped again at the end", ""


def check_api(run: DoctorRun) -> CheckResult:
    """The API starts and /api/v1/health answers ok."""
    ctx = run.ctx
    url = f"{ctx.settings.api_url}/api/v1/health"
    owner, error = _ensure_running(run, "api")
    if error:
        fix = [line for line in run.notes if line.startswith("   |")]
        run.notes.clear()
        return fail(
            error,
            [
                f"Start it in a terminal to see its messages: uv run hullbreach_server "
                f"--port {ctx.settings.api_port}",
                *fix,
                "Read the last lines it prints; the README section below explains "
                "the common ones.",
                _RERUN,
            ],
            rl.TROUBLE_API,
        )
    answer = ctx.http.request("GET", url, timeout=3.0)
    body = answer.danger_ok.json_body() if answer.is_ok else None
    version = body.get("version", "?") if isinstance(body, dict) else "?"
    return ok(f"answering at {url} (version {version})", [owner])


def _web_get(run: DoctorRun, path: str) -> HttpResponse | None:
    """GET `path` from the dev server (localhost first, then 127.0.0.1)."""
    port = run.ctx.settings.web_port
    for host in ("localhost", _LOOPBACK):
        answer = run.ctx.http.request("GET", f"http://{host}:{port}{path}", timeout=5.0)
        if answer.is_ok:
            return answer.danger_ok
    return None


def check_web(run: DoctorRun) -> CheckResult:
    """The website serves its page and passes /api through to the API."""
    ctx = run.ctx
    s = ctx.settings
    owner, error = _ensure_running(run, "web")
    if error:
        fix = [line for line in run.notes if line.startswith("   |")]
        run.notes.clear()
        return fail(
            error,
            [
                "Start it in a terminal to see its messages: npm run dev",
                *fix,
                "If it says a package is missing: npm ci",
                _RERUN,
            ],
            rl.TROUBLE_WEB,
        )
    page = _web_get(run, "/")
    if page is None or page.status != 200 or 'id="root"' not in page.body:
        return fail(
            f"{s.web_url} does not serve the Hullbreach page",
            [
                f"Open {s.web_url} in a browser and read what it shows.",
                "If another program uses that port: ./doctor.sh --only ports",
                _RERUN,
            ],
            rl.TROUBLE_WEB,
            [owner],
        )
    proxied = _web_get(run, "/api/v1/health")
    body = proxied.json_body() if proxied is not None else None
    if not (isinstance(body, dict) and body.get("status") == "ok"):
        return fail(
            f"the website cannot pass /api requests to the API on port {s.api_port}",
            [
                f"The website forwards /api to port {API_PORT_VAR} "
                f"(now {s.api_port}); make sure the API runs there.",
                "Restart the website so it reads the port again: "
                "uv run hullbreach_server stop, then uv run hullbreach_server start",
                _RERUN,
            ],
            rl.TROUBLE_WEB,
            [owner],
        )
    return ok(f"{s.web_url} serves the page and reaches the API through /api", [owner])


def _expect(answer: HttpResponse | None, status: int, step: str) -> str:
    """Empty when `answer` has `status`, else a sentence saying what came back."""
    if answer is None:
        return f"{step}: no answer from the API"
    if answer.status == status:
        return ""
    detail = answer.detail() or answer.body[:120]
    return f"{step}: expected HTTP {status}, got {answer.status} ({detail})"


def check_e2e(run: DoctorRun) -> CheckResult:
    """Sign-up, sign-in, profile read, profile edit and match history all work."""
    ctx = run.ctx
    api = f"{ctx.settings.api_url}/api/v1"
    username = f"doctor-{ctx.now():%Y%m%d%H%M%S}"
    password = secrets.token_urlsafe(16)
    ctx.console.add_secret(password)
    email = f"{username}@example.com"

    def call(
        method: str, path: str, body: dict | None = None, token: str | None = None
    ) -> HttpResponse | None:
        """One API call; None when nothing answered."""
        headers = {"Authorization": f"Bearer {token}"} if token else None
        answer = ctx.http.request(
            method, f"{api}{path}", headers=headers, json_body=body, timeout=15.0
        )
        return answer.danger_ok if answer.is_ok else None

    steps = []
    problem = _expect(
        call(
            "POST",
            "/auth/register",
            {"username": username, "email": email, "password": password},
        ),
        201,
        "create account",
    )
    if not problem:
        steps.append(f"created throwaway account {username}")
        database_url = _database_url(run)

        def delete() -> None:
            """Remove the throwaway account (its sessions go with it)."""
            deleted = dbstate.delete_user(database_url, username)
            if deleted.is_ok and deleted.danger_ok:
                _log.info("doctor: deleted %s", sanitize_for_log(username))
            else:
                run.ctx.console.line(
                    f"Note: could not delete the test account {username}; it is "
                    "harmless and can stay."
                )

        run.cleanups.append(delete)
        login = call(
            "POST", "/auth/login", {"username": username, "password": password}
        )
        problem = _expect(login, 200, "sign in")
        body = login.json_body() if login is not None else None
        token = body.get("token") if isinstance(body, dict) else None
        if not problem and isinstance(token, str):
            ctx.console.add_secret(token)
            run.session_token = token
            steps.append("signed in")
            for method, path, payload, status, label in (
                ("GET", "/me", None, 200, "read profile (GET /me)"),
                (
                    "PATCH",
                    "/me",
                    {
                        "email": f"{username}-x@example.com",
                        "current_password": password,
                    },
                    200,
                    "change email (PATCH /me)",
                ),
                ("GET", "/me/matches", None, 200, "match history (GET /me/matches)"),
            ):
                problem = _expect(call(method, path, payload, token), status, label)
                if problem:
                    break
                steps.append(label)
        elif not problem:
            problem = "sign in: the answer had no token"
    if problem:
        return fail(
            problem,
            [
                "Read the API log: .hullbreach/logs/api.log (or the terminal "
                "running the API).",
                "Make sure the database is migrated: "
                "uv run hullbreach_server db upgrade",
                "If the database was restarted while the API kept running, "
                "restart both: uv run hullbreach_server stop, then "
                "uv run hullbreach_server start",
                _RERUN,
            ],
            rl.TROUBLE_SIGNIN,
            steps,
        )
    return ok("sign-up, sign-in, profile and match history work", steps)


def check_game_session(run: DoctorRun) -> CheckResult:
    """GET /auth/session refuses missing and wrong server keys, accepts a right one."""
    ctx = run.ctx
    url = f"{ctx.settings.api_url}/api/v1/auth/session"
    assert run.app_config is not None and run.session_token is not None  # needs e2e
    keys = [
        k.get_secret_value()
        for k in run.app_config.game_server_api_keys
        if k.get_secret_value()
    ]
    bearer = {"Authorization": f"Bearer {run.session_token}"}

    def ask(extra: dict[str, str]) -> HttpResponse | None:
        """GET /auth/session with the player's token and `extra` headers."""
        answer = ctx.http.request("GET", url, headers={**bearer, **extra}, timeout=10.0)
        return answer.danger_ok if answer.is_ok else None

    restart = [
        "Restart the API so it reads the keys in .env: uv run hullbreach_server "
        "stop, then uv run hullbreach_server start (or Ctrl+C a hand-started API "
        "and start it again).",
        _RERUN,
    ]
    without = ask({})
    if not keys:
        if without is not None and without.detail() == "server key not configured":
            return warn(
                "game servers are refused with 'server key not configured' "
                f"({GAME_KEYS_VAR} is empty)",
                ["Make a key: uv run hullbreach_server server-key", *restart],
                rl.GAME,
            )
        return fail(
            "/auth/session did not answer 'server key not configured' although "
            "no keys are set",
            restart,
            rl.TROUBLE_GAME,
        )
    steps = []
    if without is not None and without.detail() == "server key not configured":
        problem = "the running API has no keys although .env has them"
    else:
        problem = _expect(without, 401, "no server key")
    if not problem:
        steps.append("no key: refused with 'server key missing'")
        wrong = ask({"X-Server-Key": "doctor-wrong-" + secrets.token_hex(8)})
        problem = _expect(wrong, 401, "wrong server key")
    if not problem:
        steps.append("wrong key: refused with 'invalid server key'")
        right = ask({"X-Server-Key": keys[0]})
        problem = _expect(right, 200, "right server key")
        if problem and right is not None and right.detail() == "invalid server key":
            problem = "the running API does not know the key in .env (it started before the key was added)"  # noqa: E501
    if not problem:
        steps.append("right key and player token: accepted")
        bad_token = ctx.http.request(
            "GET",
            url,
            headers={
                "Authorization": "Bearer doctor-not-a-token",
                "X-Server-Key": keys[0],
            },
            timeout=10.0,
        )
        problem = _expect(
            bad_token.danger_ok if bad_token.is_ok else None, 401, "bad player token"
        )
    if problem:
        return fail(problem, restart, rl.TROUBLE_GAME, steps)
    steps.append("right key, bad player token: refused with 'not authenticated'")
    return ok("game servers can verify signed-in players", steps)


def _portproxy_rules(run: DoctorRun) -> str | None:
    """`netsh interface portproxy show v4tov4` output, or None when unavailable."""
    result = run.ctx.runner.run(
        ["netsh.exe", "interface", "portproxy", "show", "v4tov4"], timeout=20
    )
    if result.is_ok and result.danger_ok.succeeded:
        return result.danger_ok.stdout
    return None


def check_lan(run: DoctorRun) -> CheckResult:
    """Whether other computers (a friend, a game server) can reach the platform."""
    ctx = run.ctx
    s = ctx.settings
    record = lifecycle.read_record(ctx, "api")
    host = record.host if record else ctx.settings.api_host
    ips = lan.lan_ips(ctx)
    details = [
        f"API listens on: {host}",
        f"this computer's LAN address(es): {', '.join(ips) or 'none found'}",
    ]
    serve_lan = ["Run: uv run hullbreach_server lan (it prints the URL to share)."]
    if host == _LOOPBACK or host == "localhost":
        return warn(
            "only this computer can reach the platform (fine for a one-computer demo)",
            serve_lan,
            rl.LAN,
            details,
        )
    if ctx.platform.wsl:
        mode = lan.networking_mode(ctx)
        details.append(f"WSL networking mode: {mode}")
        if mode == "nat":
            target = lan.wsl_ip(ctx)
            rules = _portproxy_rules(run) or ""
            forwarded = target is not None and all(
                any(str(p) in line and target in line for line in rules.splitlines())
                for p in (s.api_port, s.web_port)
            )
            if not forwarded:
                return warn(
                    "WSL is not forwarding the ports from Windows yet, so other "
                    "computers cannot connect",
                    [
                        *serve_lan,
                        "Answer y when it offers to run the Windows commands.",
                    ],
                    rl.LAN,
                    details,
                )
    return ok(
        f"listening on all interfaces; others use http://<LAN address>:{s.web_port}",
        details,
    )


RUNTIME_CHECKS = (
    Check(
        "db-container",
        "Database container",
        check_db_container,
        ("docker-daemon", "compose-file"),
    ),
    Check(
        "db-connect",
        "Database connection",
        check_db_connect,
        ("db-container", "settings"),
    ),
    Check("migrations", "Database migrations", check_migrations, ("db-connect",)),
    Check("seed", "Seed data", check_seed, ("migrations",)),
    Check("api", "API answers", check_api, ("migrations", "py-deps")),
    Check("web", "Website and /api proxy", check_web, ("web-deps", "api")),
    Check("e2e", "Sign-up and sign-in", check_e2e, ("api", "seed")),
    Check(
        "game-session", "Game-server sign-in", check_game_session, ("e2e", "game-keys")
    ),
    Check("lan", "Other computers", check_lan, ("api",)),
)
