"""Turn register's pydantic validation errors into friendly per-field messages.

The raw `input` of an error is never read or logged: for the password
field it is the password itself.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# frob:ticket 01M5XX28K491XN5RNGABW0Q5RP
REGISTER_PATH = "/api/v1/auth/register"
_USERNAME_RULE = "username may only contain letters, digits, '_', '.' and '-'"


class FieldError(BaseModel):
    """One rejected register field and the reason, safe to show and to log."""

    field: str
    detail: str


def _field_name(loc: Sequence[Any]) -> str:
    """The body field a pydantic `loc` points at ("body" when it is the whole body)."""
    parts = [str(p) for p in loc if p != "body"]
    return parts[0] if parts else "body"


def _message(field: str, error: dict[str, Any]) -> str:
    """Friendly one-line reason for a single pydantic error, naming the rule."""
    kind = error.get("type", "")
    ctx = error.get("ctx") or {}
    if kind == "missing":
        return f"{field} is required"
    if kind == "string_too_short":
        return f"{field} must be at least {ctx.get('min_length')} characters"
    if kind == "string_too_long":
        return f"{field} must be at most {ctx.get('max_length')} characters"
    if kind == "string_pattern_mismatch" and field == "username":
        return _USERNAME_RULE
    if kind == "value_error" and field == "email":
        return "enter a valid email address"
    if kind == "value_error" and "error" in ctx:
        return str(ctx["error"])
    return f"{field} is invalid"


# noqa: E501  # frob:tests tests/unit/test_register_errors.py::test_short_password_states_the_rule_and_names_the_field
def field_errors(errors: Sequence[dict[str, Any]]) -> list[FieldError]:
    """Map pydantic `errors()` to one `FieldError` per field, in order of appearance."""
    seen: dict[str, FieldError] = {}
    for error in errors:
        field = _field_name(error.get("loc", ()))
        if field not in seen:
            seen[field] = FieldError(field=field, detail=_message(field, error))
    return list(seen.values())


# noqa: E501  # frob:tests tests/unit/test_register_errors.py::test_weak_password_failure_log_does_not_echo_the_password
def log_failures(errors: Sequence[FieldError]) -> None:
    """Log each rejected register field with its reason; never any submitted value."""
    for item in errors:
        _log.warning("register: rejected field=%s reason=%s", item.field, item.detail)
