"""The doctor: run every check in order and say exactly how to fix what fails.

Checks name the checks they need; when one FAILs, the checks that need it
are shown as PENDING instead of producing confusing follow-on errors, but
the whole checklist is always printed. `--demo` narrows the run to what one
demo needs and ends with the exact next commands.
"""

from __future__ import annotations

from typani import Err, Ok, Result, propagate

from hullbreach_ops import lan
from hullbreach_ops.accounts import GAME_KEYS_VAR, GAME_SIDE_KEY_VAR
from hullbreach_ops.checkbase import DEMOS, Check, CheckResult, DoctorRun, Status
from hullbreach_ops.checks_config import CONFIG_CHECKS
from hullbreach_ops.checks_runtime import RUNTIME_CHECKS
from hullbreach_ops.checks_tools import TOOL_CHECKS
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# noqa: E501  # frob:tests tests/unit/test_ops_doctor.py::test_registry_ids_are_unique_and_needs_come_first
# frob:doc docs/index.md#operator-scripts-and-the-doctor
REGISTRY: tuple[Check, ...] = TOOL_CHECKS + CONFIG_CHECKS + RUNTIME_CHECKS

_GAME_ONLY = ("guest", "online")
_NOT_FOR_WEBSITE = ("game-keys", "game-session", "lan")
_INDENT = "            "
_GAME_DOCTOR = "https://github.com/lognd/project-hullbreach-game#readme"


# frob:tests tests/unit/test_ops_doctor.py::test_select_adds_what_a_check_needs
# frob:tests tests/unit/test_ops_doctor.py::test_demo_profiles_pick_their_checks
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def select(profile: str, only: str | None = None) -> Result[list[Check], OpsError]:
    """The checks to run, in order: a demo's checks, or one check and what it needs."""
    by_id = {check.id: check for check in REGISTRY}
    if only is not None:
        if only not in by_id:
            return Err(
                OpsError(
                    message=f"there is no check called {only!r}",
                    fix=[f"Pick one of: {', '.join(by_id)}"],
                )
            )
        wanted = {only}
        for check in reversed(REGISTRY):
            if check.id in wanted:
                wanted.update(check.needs)
        return Ok([check for check in REGISTRY if check.id in wanted])
    if profile in _GAME_ONLY:
        return Ok([])
    if profile == "website":
        return Ok([c for c in REGISTRY if c.id not in _NOT_FOR_WEBSITE])
    return Ok(list(REGISTRY))


def _show(run: DoctorRun, check: Check, result: CheckResult) -> None:
    """Print one checklist row with its details, fix steps and README link."""
    console = run.ctx.console
    console.status(result.status.value, check.id, result.summary)
    for detail in result.details:
        console.line(f"{_INDENT}{detail}")
    if result.fix:
        console.line(f"{_INDENT}How to fix:")
        console.steps(result.fix, _INDENT + "  ")
    if result.readme is not None and result.status != Status.PASS:
        console.line(f"{_INDENT}More help: {result.readme.describe()}")


def _run_one(run: DoctorRun, check: Check) -> CheckResult:
    """Run `check` unless a check it needs did not pass."""
    blocked = [
        need
        for need in check.needs
        if need in run.results and not run.results[need].usable
    ]
    if blocked:
        return CheckResult(
            status=Status.PENDING,
            summary=f"waiting for: {', '.join(blocked)} (fix that first)",
        )
    _log.info("doctor: running %s", check.id)
    result = check.run(run)
    _log.info("doctor: %s -> %s", check.id, result.status.value)
    return result


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def run_checks(run: DoctorRun, checks: list[Check]) -> None:
    """Run `checks` in order, printing each row as it finishes, then clean up."""
    try:
        for check in checks:
            result = _run_one(run, check)
            run.results[check.id] = result
            _show(run, check, result)
    finally:
        for cleanup in reversed(run.cleanups):
            cleanup()
        run.cleanups.clear()


def _first_failure(run: DoctorRun) -> str | None:
    """Id of the first FAIL, the one to fix first."""
    for check_id, result in run.results.items():
        if result.status == Status.FAIL:
            return check_id
    return None


def _game_side_values(run: DoctorRun) -> None:
    """Print what the game server and game clients must be told."""
    ctx = run.ctx
    s = ctx.settings
    console = ctx.console
    console.heading("Values for the game")
    console.line("On the computer that runs the GAME SERVER, set:")
    console.line(
        f"  HULLBREACH_PLATFORM_URL=http://127.0.0.1:{s.api_port}"
        "   (when the game server runs on THIS computer)"
    )
    ips = lan.lan_ips(ctx)
    for ip in ips:
        console.line(
            f"  HULLBREACH_PLATFORM_URL=http://{ip}:{s.api_port}"
            "   (from another computer, after: uv run hullbreach_server lan)"
        )
    console.line(
        f"  {GAME_SIDE_KEY_VAR}=<one of the keys in {GAME_KEYS_VAR} in this "
        "computer's .env>"
    )
    console.line("  HULLBREACH_REQUIRE_PLATFORM_AUTH=1")
    console.line(
        "Game clients only need the same HULLBREACH_PLATFORM_URL (or the "
        "-hullbreachPlatformUrl <url> launch option) to sign in."
    )
    if ctx.platform.wsl:
        console.line(
            "This is WSL: a game on this same Windows PC reaches the platform at "
            f"http://127.0.0.1:{s.api_port} (Windows forwards localhost into WSL)."
        )


def _next_steps(run: DoctorRun) -> None:
    """End with the exact commands to run next for the chosen demo."""
    ctx = run.ctx
    s = ctx.settings
    console = ctx.console
    console.heading("Next")
    if run.profile in _GAME_ONLY:
        console.line(
            f"The {run.profile} demo is {DEMOS[run.profile]}, so there is nothing "
            "to start here."
        )
        console.line(
            f"Run the game's own doctor; its README explains how: {_GAME_DOCTOR}"
        )
        if run.profile == "online":
            console.line(
                "To have players signed in as well, run: ./doctor.sh --demo platform"
            )
        return
    console.line(
        "1. Start everything:   uv run hullbreach_server start   (or: make start)"
    )
    console.line(f"2. Open the website:   {s.web_url}")
    console.line("3. Demo accounts:      uv run hullbreach_server demo-users")
    console.line("4. Stop everything:    uv run hullbreach_server stop")
    if run.profile == "platform":
        _game_side_values(run)
        console.line()
        console.line(f"Then run the game's doctor on the game computer: {_GAME_DOCTOR}")
    elif run.profile == "full":
        console.line(
            "For the game demos: ./doctor.sh --demo platform (signed-in players), "
            "--demo guest or --demo online."
        )


# noqa: E501  # frob:tests tests/unit/test_ops_doctor.py::test_doctor_prints_fix_steps_and_the_first_failure
# noqa: E501  # frob:tests tests/unit/test_ops_doctor.py::test_doctor_game_only_demo_points_to_the_game_doctor
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def doctor(
    ctx: OpsContext, profile: str = "full", only: str | None = None
) -> Result[DoctorRun, OpsError]:
    """Run the doctor; the DoctorRun says what passed. Err only for a bad check name."""
    checks = select(profile, only).unwrap()
    run = DoctorRun(ctx=ctx, profile=profile)
    console = ctx.console
    console.line("Hullbreach platform doctor")
    if only is not None:
        console.line(f"Checking: {only} (and what it needs)")
    else:
        what = DEMOS.get(profile, "everything")
        console.line(f"Checking: {what}")
    if checks:
        console.line(
            "Each row is PASS, WARN (works, but read it), FAIL (fix this) or "
            "PENDING (waits for a FAIL above)."
        )
    console.line()
    _log.info("doctor: profile=%s only=%s checks=%d", profile, only, len(checks))
    run_checks(run, checks)
    counts = {status: 0 for status in Status}
    for result in run.results.values():
        counts[result.status] += 1
    if not checks:
        _next_steps(run)
        return Ok(run)
    console.line()
    console.line(
        "Summary: " + ", ".join(f"{counts[status]} {status.value}" for status in Status)
    )
    failed = _first_failure(run)
    if failed is not None:
        console.line(
            f"Fix the first FAIL ({failed}) using its steps above, then run "
            "./doctor.sh again."
        )
        console.line(f"(Only that check: ./doctor.sh --only {failed})")
        console.line(
            "Stuck? ./doctor.sh --collect writes a support file to send to the team."
        )
        _log.info("doctor: first failure %s", failed)
        return Ok(run)
    if only is None:
        _next_steps(run)
    return Ok(run)


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def passed(run: DoctorRun) -> bool:
    """True when no check FAILed or stayed PENDING."""
    return all(r.status in (Status.PASS, Status.WARN) for r in run.results.values())
