"""Structured access and event log lines, shared by the API and the demo console.

The API writes two kinds of line to its log: `[access]` (one per HTTP request)
and `[event]` (one per database state change, in plain words). The operator
console parses them back. Lines never carry passwords, tokens, keys, headers,
bodies or query strings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import quote

from pydantic import BaseModel
from typani import Err, Ok, Result

ACCESS_TAG = "[access]"
EVENT_TAG = "[event]"
_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_PATH_SAFE = "/:@!$&'()*+,;=-._~%"


# frob:doc docs/index.md#demo-console
class AccessEntry(BaseModel):
    """One parsed `[access]` line: a single HTTP request."""

    time: datetime
    method: str
    path: str
    status: int
    ms: float
    user: str
    server_key: bool


# frob:doc docs/index.md#demo-console
class EventEntry(BaseModel):
    """One parsed `[event]` line: a human-readable database state change."""

    time: datetime
    text: str


# frob:doc docs/index.md#demo-console
class LineError(BaseModel):
    """Why a log line is not an access or event line."""

    message: str

    def __str__(self) -> str:
        return self.message


def _stamp(when: datetime) -> str:
    """Return `when` as a UTC second-resolution timestamp."""
    return when.astimezone(timezone.utc).strftime(_TIME_FORMAT)


def _parse_stamp(text: str) -> datetime | None:
    """Return the UTC datetime for `text`, or None if it is not our format."""
    try:
        return datetime.strptime(text, _TIME_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


# frob:doc docs/index.md#demo-console
def format_access(
    when: datetime,
    method: str,
    path: str,
    status: int,
    ms: float,
    *,
    user_id: str | None,
    server_key: bool = False,
) -> str:
    """Return the one-line `[access]` text (path percent-quoted: no forged lines)."""
    safe_path = quote(path, safe=_PATH_SAFE)
    return (
        f"{ACCESS_TAG} {_stamp(when)} {method} {safe_path} {status} {ms:.1f}ms "
        f"user={user_id or '-'} key={'yes' if server_key else 'no'}"
    )


# frob:doc docs/index.md#demo-console
def format_event(when: datetime, text: str) -> str:
    """Return the one-line `[event]` text, with any line breaks in `text` flattened."""
    return f"{EVENT_TAG} {_stamp(when)} {' '.join(text.split())}"


# frob:doc docs/index.md#demo-console
def log_event(log: logging.Logger, text: str, *args: object) -> None:
    """Log a database state change as an INFO `[event]` line (`text` is %-formatted)."""
    log.info(format_event(datetime.now(timezone.utc), text % args if args else text))


def _parse_access(rest: str) -> Result[AccessEntry, LineError]:
    """Parse the fields after the `[access]` tag."""
    parts = rest.split(" ")
    if len(parts) != 7:
        return Err(LineError(message="access line has the wrong field count"))
    stamp, method, path, status, ms, user, key = parts
    when = _parse_stamp(stamp)
    if when is None or not status.isdigit() or not ms.endswith("ms"):
        return Err(LineError(message="access line has a malformed field"))
    if not (user.startswith("user=") and key in ("key=yes", "key=no")):
        return Err(LineError(message="access line has a malformed field"))
    try:
        millis = float(ms[:-2])
    except ValueError:
        return Err(LineError(message="access line has a malformed duration"))
    return Ok(
        AccessEntry(
            time=when,
            method=method,
            path=path,
            status=int(status),
            ms=millis,
            user=user[len("user=") :],
            server_key=key == "key=yes",
        )
    )


def _parse_event(rest: str) -> Result[EventEntry, LineError]:
    """Parse the fields after the `[event]` tag."""
    stamp, _sep, text = rest.partition(" ")
    when = _parse_stamp(stamp)
    if when is None or not text:
        return Err(LineError(message="event line has a malformed field"))
    return Ok(EventEntry(time=when, text=text))


# frob:doc docs/index.md#demo-console
def parse_line(line: str) -> Result[AccessEntry | EventEntry, LineError]:
    """Parse a log line into an entry, or Err if it is not an access/event line."""
    text = line.rstrip("\r\n")
    if text.startswith(ACCESS_TAG + " "):
        return _parse_access(text[len(ACCESS_TAG) + 1 :])
    if text.startswith(EVENT_TAG + " "):
        return _parse_event(text[len(EVENT_TAG) + 1 :])
    return Err(LineError(message="not an access or event line"))
