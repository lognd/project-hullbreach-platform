"""Sanitized, bounded summaries of JSON request bodies for the demo console.

Redaction is by key name (never by value): any key that looks like a password,
token, secret, credential, hash or key has its whole value replaced, at any
nesting depth. Everything else is bounded in size so a summary is one short line.
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

REDACTED = "<redacted>"
MAX_STRING = 48
MAX_LIST = 3
MAX_KEYS = 12
MAX_DEPTH = 3
MAX_SUMMARY = 300

_NON_ALNUM = re.compile(r"[^a-z0-9]")
_SECRET_PARTS = (
    "password",
    "passwd",
    "passphrase",
    "secret",
    "token",
    "authorization",
    "credential",
    "cookie",
    "hash",
    "salt",
    "apikey",
    "privatekey",
    "signature",
    "csrf",
    "session",
)
_SECRET_EXACT = frozenset({"auth", "jwt", "otp", "pin", "cvv", "ssn", "bearer"})


# frob:doc docs/index.md#demo-console
class PayloadError(BaseModel):
    """Why a request body could not be summarized."""

    message: str

    def __str__(self) -> str:
        return self.message


# frob:doc docs/index.md#demo-console
def is_secret_key(name: str) -> bool:
    """Return True if a field called `name` must never have its value logged."""
    norm = _NON_ALNUM.sub("", name.lower())
    return (
        norm in _SECRET_EXACT
        or norm.endswith("key")
        or any(p in norm for p in _SECRET_PARTS)
    )


def _clip(text: str) -> str:
    """Return `text` cut to the per-string limit."""
    return text if len(text) <= MAX_STRING else text[:MAX_STRING] + "..."


# frob:doc docs/index.md#demo-console
def sanitize_payload(value: Any, _depth: int = 0) -> Any:
    """Return a redacted, size-bounded copy of parsed JSON `value`."""
    if _depth > MAX_DEPTH:
        return "..."
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= MAX_KEYS:
                clean["..."] = f"+{len(value) - MAX_KEYS} more"
                break
            clean[str(key)] = (
                REDACTED
                if is_secret_key(str(key))
                else sanitize_payload(item, _depth + 1)
            )
        return clean
    if isinstance(value, list):
        items = [sanitize_payload(item, _depth + 1) for item in value[:MAX_LIST]]
        if len(value) > MAX_LIST:
            items.append(f"...(+{len(value) - MAX_LIST})")
        return items
    if isinstance(value, str):
        return _clip(value)
    return value


# frob:doc docs/index.md#demo-console
def summarize_body(body: bytes) -> Result[str, PayloadError]:
    """Return a compact one-line ASCII summary of a JSON body, or Err if unreadable."""
    try:
        parsed = json.loads(body)
    except (ValueError, RecursionError):
        _log.debug("request body is not readable JSON (%d bytes)", len(body))
        return Err(PayloadError(message="body is not valid JSON"))
    text = json.dumps(
        sanitize_payload(parsed), separators=(",", ":"), ensure_ascii=True
    )
    if len(text) > MAX_SUMMARY:
        text = text[:MAX_SUMMARY] + "..."
    return Ok(text)
