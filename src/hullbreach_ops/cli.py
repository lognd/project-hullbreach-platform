"""The operator subcommands of `hullbreach_server`: doctor, start, stop and friends.

`python -m hullbreach_server <command>` (or `uv run hullbreach_server ...`,
or the Makefile target of the same name) all land here, so there is one
implementation of each script. Operator output goes to the terminal through
the Console; log records go to .hullbreach/logs/ops.log so they never mix
with the instructions a beginner is reading.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path

from typani import Result

from hullbreach_ops.console import Console
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.settings import OpsSettings, find_root
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# frob:tests tests/unit/test_ops_cli.py::test_every_command_is_wired
# frob:doc docs/index.md#operator-scripts-and-the-doctor
COMMANDS = {
    "doctor": "check everything and explain how to fix what is wrong",
    "demo": "one command: settings, database, API, website and demo account",
    "smoke": "register, log in and read the profile against the running stack",
    "demo-match": "post a sample match as the game server (needs a server key)",
    "start": "start the database, API and website (prints the URLs)",
    "stop": "stop the website, API and database (keeps the data)",
    "status": "show what is running",
    "reset-db": "DELETE the local database and create it again (asks first)",
    "wipe-demo": "DELETE the database, logs and support zips a demo left (asks first)",
    "demo-users": "create two demo player accounts",
    "server-key": "make a game-server key and say where it goes",
    "console": "live view of API requests (add --db for database changes)",
    "lan": "start so other computers on the network can connect",
    "grant-credits": "DEMO ONLY: add credits to an account (needs demo mode)",
}
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


# frob:tests tests/unit/test_ops_cli.py::test_every_command_is_wired
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def add_ops_commands(sub: argparse._SubParsersAction) -> None:
    """Register the operator subcommands on the server's argument parser."""
    from hullbreach_ops.checkbase import DEMOS

    for name, help_text in COMMANDS.items():
        parser = sub.add_parser(name, help=help_text, description=help_text)
        if name == "doctor":
            parser.add_argument(
                "--demo",
                choices=sorted(DEMOS),
                help="check only what one demo needs, then print its next commands",
            )
            parser.add_argument(
                "--only", metavar="CHECK", help="run one check (and what it needs)"
            )
            parser.add_argument(
                "--collect",
                action="store_true",
                help="also write a redacted support zip to send to the team",
            )
        if name == "console":
            parser.add_argument(
                "--db",
                action="store_true",
                help="also show database changes (registered, match recorded, ...)",
            )
            parser.add_argument(
                "--no-payloads",
                action="store_true",
                help="hide the request payload summaries (shown by default)",
            )
            parser.add_argument(
                "-n",
                "--lines",
                type=int,
                default=10,
                help="how many recent lines to show first (default 10)",
            )
            parser.add_argument(
                "--no-follow",
                action="store_true",
                help="print the recent lines and exit instead of following",
            )
        if name == "grant-credits":
            parser.add_argument("user", help="username to credit, e.g. demo_pilot")
            parser.add_argument("amount", type=int, help="credits to add, above 0")
        if name in ("start", "demo"):
            parser.add_argument(
                "--host",
                dest="bind_host",
                help="address to listen on (default: HULLBREACH_HOST or 127.0.0.1)",
            )


def _log_to_file(logs_dir: Path) -> None:
    """Send log records to ops.log instead of the terminal the operator reads."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(logs_dir / "ops.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    for old in list(root.handlers):
        root.removeHandler(old)
    root.addHandler(handler)


def _report(console: Console, error: OpsError) -> None:
    """Print a failed command's message and numbered fix steps."""
    console.line()
    console.line(f"Problem: {error.message}")
    if error.fix:
        console.line("How to fix:")
        console.steps(error.fix, "  ")


def _dispatch(ctx: OpsContext, args: argparse.Namespace) -> int:
    """Run one operator command; the exit code is 0 on success."""
    from hullbreach_ops import (
        accounts,
        demo,
        demo_match,
        grant_credits,
        lan,
        lifecycle,
        smoke,
        watch,
        wipe,
    )
    from hullbreach_ops.collect import collect
    from hullbreach_ops.doctor import doctor, passed

    if args.command == "doctor":
        ran = doctor(ctx, args.demo or "full", args.only)
        if ran.is_err:
            _report(ctx.console, ran.danger_err)
            return 2
        if args.collect:
            written = collect(ctx)
            if written.is_err:
                _report(ctx.console, written.danger_err)
        return 0 if passed(ran.danger_ok) else 1
    simple: dict[str, Callable[[OpsContext], Result[object, OpsError]]] = {
        "stop": lifecycle.stop,
        "status": lifecycle.status,
        "reset-db": lifecycle.reset_db,
        "wipe-demo": wipe.wipe_demo,
        "demo-users": accounts.demo_users,
        "server-key": accounts.server_key,
        "lan": lan.lan,
        "smoke": smoke.smoke,
        "demo-match": demo_match.demo_match,
    }
    if args.command == "start":
        result: Result[object, OpsError] = lifecycle.start(ctx, args.bind_host)
    elif args.command == "demo":
        result = demo.demo(ctx, args.bind_host)
    elif args.command == "console":
        result = watch.watch(
            ctx,
            show_events=args.db,
            lines=args.lines,
            follow=not args.no_follow,
            show_payloads=not args.no_payloads,
        )
    elif args.command == "grant-credits":
        result = grant_credits.grant_credits(ctx, args.user, args.amount)
    else:
        result = simple[args.command](ctx)
    if result.is_err:
        _log.warning("%s failed: %s", args.command, result.danger_err.message)
        _report(ctx.console, result.danger_err)
        ctx.console.line("For a full diagnosis run: ./doctor.sh")
        return 1
    return 0


# noqa: E501  # frob:tests tests/unit/test_ops_cli.py::test_run_ops_outside_a_checkout_explains_where_to_run
# frob:tests tests/unit/test_ops_cli.py::test_run_ops_reports_a_bad_port_setting
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def run_ops(args: argparse.Namespace, console: Console | None = None) -> int:
    """Entry point for the operator subcommands; returns the process exit code."""
    console = console or Console(sys.stdout, color=sys.stdout.isatty())
    root = find_root(Path.cwd()) or find_root(Path(__file__).resolve().parent)
    if root is None:
        _report(
            console,
            OpsError(
                message="this is not inside a copy of the Hullbreach platform code",
                fix=[
                    "Go to the folder you cloned: cd project-hullbreach-platform",
                    "Run the command there again.",
                ],
            ),
        )
        return 1
    loaded = OpsSettings.from_environ(os.environ, root)
    if loaded.is_err:
        _report(console, loaded.danger_err)
        return 1
    settings = loaded.danger_ok
    _log_to_file(settings.logs_dir)
    _log.info("ops: command=%s root=%s", args.command, root)
    ctx = OpsContext(settings=settings, console=console)
    return _dispatch(ctx, args)
