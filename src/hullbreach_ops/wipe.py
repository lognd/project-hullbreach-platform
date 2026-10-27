"""`demo-wipe`: remove every trace of earlier demo runs this checkout can reach.

`reset-db` only recreates the database; the API log in `.hullbreach/logs`
survives it, and `console` replays that log, so old usernames reappear. This
goes further: it stops the stack, deletes the compose project's volumes and
clears the local log and support-bundle files, then lists what only the
person can clear (browser state, the game's saved name, other checkouts).
"""

from __future__ import annotations

from pathlib import Path

from typani import Err, Ok, Result, propagate

from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import DOCKER_FIX, compose_argv, run_ok, stop_service
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# The log this very command writes to stays open, so it is emptied, not deleted.
_OPEN_LOG = "ops.log"
_BUNDLE_GLOB = "hullbreach-support-*.zip"

# What no command here can reach; printed after every wipe.
MANUAL_STEPS = (
    "Browser: for the site (e.g. localhost:5173) clear cookies, localStorage "
    "and saved form data. Chrome/Edge: lock icon > Site settings > Clear data; "
    "autofill is separate (Settings > Autofill > Passwords / Addresses).",
    "Game: delete the saved name (Unity PlayerPrefs: Edit > Clear All "
    "PlayerPrefs in the editor, or the registry key under HKCU\\Software\\"
    "<company>\\<product> on Windows) and unset any HULLBREACH_PLATFORM_* "
    "variable, e.g. HULLBREACH_PLATFORM_USERNAME, in the shell or system "
    "environment that launches the game.",
    "Other checkouts: each folder has its own compose project, volumes, "
    ".env and .hullbreach/logs. Run `uv run hullbreach_server demo-wipe` "
    "inside every copy you have ever demoed from (for instance one on a "
    "Windows drive under /mnt).",
)


# noqa: E501  # frob:tests tests/unit/test_ops_wipe.py::test_other_pgdata_volumes_skips_ours_and_tolerates_docker_errors
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def other_pgdata_volumes(ctx: OpsContext) -> list[str]:
    """Database volumes of other compose projects on this docker host ([] if unknown)."""  # noqa: E501
    result = ctx.runner.run(
        ["docker", "volume", "ls", "--format", "{{.Name}}", "--filter", "name=pgdata"],
        cwd=ctx.settings.root,
        env=ctx.environ,
        timeout=30,
    )
    if result.is_err or not result.danger_ok.succeeded:
        _log.info("wipe: could not list docker volumes")
        return []
    names = result.danger_ok.stdout.split()
    return sorted(n for n in names if n != ctx.settings.db_volume)


# frob:tests tests/unit/test_ops_wipe.py::test_wipe_demo_removes_volumes_and_local_files
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def clear_local_files(ctx: OpsContext) -> list[Path]:
    """Delete logs, pid records and support zips; return what was removed."""
    s = ctx.settings
    removed: list[Path] = []
    for directory in (s.logs_dir, s.run_dir):
        for path in sorted(directory.glob("*")) if directory.is_dir() else []:
            if not path.is_file():
                continue
            if path.name == _OPEN_LOG and directory == s.logs_dir:
                path.write_text("", encoding="utf-8")
            else:
                path.unlink(missing_ok=True)
            removed.append(path)
    for bundle in sorted(s.root.glob(_BUNDLE_GLOB)):
        bundle.unlink(missing_ok=True)
        removed.append(bundle)
    _log.warning("wipe: removed %d local files", len(removed))
    return removed


def _print_plan(ctx: OpsContext) -> None:
    """Say what will be deleted, and warn about a hand-set compose project."""
    s = ctx.settings
    ctx.console.heading("Wipe the demo completely")
    ctx.console.line(
        "THIS DELETES EVERY ACCOUNT, MATCH AND SETTING, AND ALL LOCAL LOGS."
    )
    ctx.console.line(f"  Compose project: {s.compose_project}")
    ctx.console.line(f"  Docker volume:   {s.db_volume}")
    ctx.console.line(f"  Logs folder:     {s.logs_dir}")
    if s.compose_project != s.default_compose_project:
        ctx.console.line(
            f"WARNING: COMPOSE_PROJECT_NAME is set to {s.compose_project} (this "
            f"folder's default would be {s.default_compose_project}). Another "
            "checkout that uses the same name shares this volume and loses its "
            "data too; one with a different name keeps its own."
        )
    others = other_pgdata_volumes(ctx)
    if others:
        ctx.console.line(
            "Other database volumes on this docker host (NOT touched here): "
            + ", ".join(others)
        )
    ctx.console.line("It cannot be undone.")


# noqa: E501  # frob:tests tests/unit/test_ops_wipe.py::test_wipe_demo_needs_a_person_and_the_exact_volume_name
# noqa: E501  # frob:tests tests/unit/test_ops_wipe.py::test_wipe_demo_reports_a_docker_failure_without_touching_files
# noqa: E501  # frob:tests tests/unit/test_ops_wipe.py::test_wipe_demo_warns_when_the_project_name_is_overridden
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def wipe_demo(ctx: OpsContext) -> Result[None, OpsError]:
    """Stop the stack, delete its volumes and local logs, then list manual steps."""
    s = ctx.settings
    _print_plan(ctx)
    if not ctx.console.interactive:
        return Err(
            OpsError(
                message="demo-wipe needs a person at the keyboard to confirm",
                fix=["Run it in a terminal: uv run hullbreach_server demo-wipe"],
            )
        )
    typed = ctx.console.ask_text(f"Type the volume name ({s.db_volume}) to continue: ")
    if typed != s.db_volume:
        ctx.console.line("Not confirmed; nothing was deleted.")
        _log.info("demo-wipe: not confirmed")
        return Ok(None)
    _log.warning("demo-wipe: wiping project %s", s.compose_project)
    for service in ("web", "api"):
        if stop_service(ctx, service):
            ctx.console.line(f"  Stopped the {service}")
    run_ok(
        ctx,
        compose_argv(ctx, "down", "-v", "--remove-orphans"),
        "docker compose down -v",
        DOCKER_FIX,
    ).unwrap()
    ctx.console.line(f"  Deleted the database container and volume {s.db_volume}")
    removed = clear_local_files(ctx)
    ctx.console.line(f"  Cleared {len(removed)} local log, record and support files")
    ctx.console.line()
    ctx.console.line("Still yours to clear by hand (no command can reach these):")
    ctx.console.steps(list(MANUAL_STEPS), "  ")
    ctx.console.line()
    ctx.console.line("Then start fresh with: uv run hullbreach_server demo")
    return Ok(None)
