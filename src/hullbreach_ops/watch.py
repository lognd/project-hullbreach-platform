"""`console`: tail the API log as a live view of requests and database changes."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

from typani import Err, Ok, Result

from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import log_path
from hullbreach_server.logging import get_logger
from hullbreach_server.logging.events import AccessEntry, EventEntry, parse_line

_log = get_logger(__name__)

_POLL_SECONDS = 0.5
_LEVEL_PREFIXES = ("WARNING:", "ERROR:", "CRITICAL:")
_GREEN, _YELLOW, _RED = "32", "33", "31"


def _status_color(status: int) -> str | None:
    """The ANSI code for an HTTP status: green 2xx/3xx, yellow 4xx, red 5xx."""
    if status >= 500:
        return _RED
    if status >= 400:
        return _YELLOW
    return _GREEN


def _show(ctx: OpsContext, raw: str, show_events: bool) -> bool:
    """Print `raw` in console form if worth showing; True when something printed."""
    parsed = parse_line(raw)
    if parsed.is_ok:
        entry = parsed.danger_ok
        stamp = entry.time.strftime("%H:%M:%S")
        if isinstance(entry, AccessEntry):
            flag = "  [server-key]" if entry.server_key else ""
            status = str(entry.status)
            ctx.console.highlight(
                f"{stamp}  {entry.method:<6} {entry.path:<30} {status}  "
                f"{entry.ms:>6.0f}ms  user={entry.user}{flag}",
                status,
                _status_color(entry.status) or _GREEN,
            )
            return True
        if isinstance(entry, EventEntry) and show_events:
            ctx.console.highlight(f"{stamp}  DB      {entry.text}", "DB", _GREEN)
            return True
        return False
    if raw.startswith(_LEVEL_PREFIXES):
        ctx.console.highlight(raw.rstrip(), raw.split(":", 1)[0], _YELLOW)
        return True
    return False


def _follow(ctx: OpsContext, path: Path, handle: TextIO, show_events: bool) -> None:
    """Print new lines as they arrive until interrupted; survives log truncation."""
    pending = ""
    while True:
        chunk = handle.readline()
        if chunk:
            pending += chunk
            if pending.endswith("\n"):
                _show(ctx, pending, show_events)
                pending = ""
            continue
        if (
            path.stat().st_size < handle.tell()
        ):  # the log was reset (make reset, restart)
            handle.seek(0)
            pending = ""
        ctx.sleep(_POLL_SECONDS)


# frob:ticket 01M5V5TXXWPT81BGF67BNZNJJN
# frob:doc docs/index.md#demo-console
def watch(
    ctx: OpsContext, *, show_events: bool, lines: int, follow: bool
) -> Result[None, OpsError]:
    """Show the last `lines` requests (and DB events if `show_events`), then follow.

    Reads the log `make demo` / `make start` writes; Err if the API has not been
    started yet. Ctrl+C ends a follow cleanly.
    """
    path = log_path(ctx, "api")
    if not path.exists():
        return Err(
            OpsError(
                message=f"no API log yet at {path}",
                fix=["Start the stack first: make demo", "Then run: make console"],
            )
        )
    ctx.console.line("Live API console (times are UTC). Press Ctrl+C to stop.")
    ctx.console.line(
        "Showing requests and database changes."
        if show_events
        else "Showing requests. Add --db (make console-db) to show database changes."
    )
    _log.info("console: watching %s (events=%s, follow=%s)", path, show_events, follow)
    with path.open(encoding="utf-8", errors="replace") as handle:
        recent = handle.read().splitlines()
        shown = [r for r in recent if _is_shown(r, show_events)]
        shown = shown[max(len(shown) - lines, 0) :]
        for raw in shown:
            _show(ctx, raw, show_events)
        if follow:
            try:
                _follow(ctx, path, handle, show_events)
            except KeyboardInterrupt:
                ctx.console.line()
                ctx.console.line("Console stopped.")
    return Ok(None)


def _is_shown(raw: str, show_events: bool) -> bool:
    """True when `raw` would print: access line, event (if `show_events`) or warning."""
    parsed = parse_line(raw)
    if parsed.is_ok:
        return isinstance(parsed.danger_ok, AccessEntry) or show_events
    return raw.startswith(_LEVEL_PREFIXES)
