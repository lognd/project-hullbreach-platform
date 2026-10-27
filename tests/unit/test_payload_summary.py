"""Unit tests for the request-payload summary the console shows (redaction first)."""

from __future__ import annotations

import json

import pytest

from hullbreach_server.logging.payload import (
    REDACTED,
    is_secret_key,
    sanitize_payload,
    summarize_body,
)

SECRET_KEYS = [
    "password",
    "Password",
    "new_password",
    "current_password",
    "passwd",
    "token",
    "access_token",
    "refresh-token",
    "accessToken",
    "Authorization",
    "authorization",
    "secret",
    "client_secret",
    "api_key",
    "apiKey",
    "x-server-key",
    "X_Server_Key",
    "key",
    "password_hash",
    "hash",
    "salt",
    "cookie",
    "set-cookie",
    "session_id",
    "csrf",
    "credentials",
    "private_key",
]
PLAIN_KEYS = ["username", "email", "item_id", "slug", "match_id", "amount", "name"]


@pytest.mark.parametrize("name", SECRET_KEYS)
def test_secret_key_names_are_recognised(name: str) -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::is_secret_key kind="unit"
    assert is_secret_key(name)


@pytest.mark.parametrize("name", PLAIN_KEYS)
def test_ordinary_key_names_are_not_secret(name: str) -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::is_secret_key kind="unit"
    assert not is_secret_key(name)


def test_sanitize_redacts_by_key_name_and_keeps_the_rest() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::sanitize_payload kind="unit"
    clean = sanitize_payload({"username": "ann", "password": "hunter2hunter2"})
    assert clean == {"username": "ann", "password": REDACTED}


def test_sanitize_redacts_deeply_nested_and_listed_secrets() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::sanitize_payload kind="unit"
    payload = {
        "profile": {
            "name": "ann",
            "auth": {"token": "tok-abc-123", "refresh_token": "ref-xyz"},
            "devices": [
                {"id": 1, "api_key": "k-111"},
                {"id": 2, "meta": {"Authorization": "Bearer zzz"}},
            ],
        }
    }
    text = json.dumps(sanitize_payload(payload))
    for leaked in ("tok-abc-123", "ref-xyz", "k-111", "Bearer zzz"):
        assert leaked not in text
    assert '"name": "ann"' in text


def test_sanitize_redacts_whole_subtree_under_a_secret_key() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::sanitize_payload kind="unit"
    clean = sanitize_payload({"secrets": {"a": "one", "b": ["two"]}, "ok": 1})
    assert clean == {"secrets": REDACTED, "ok": 1}


def test_sanitize_bounds_long_strings_lists_and_depth() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::sanitize_payload kind="unit"
    clean = sanitize_payload(
        {
            "bio": "x" * 500,
            "items": list(range(50)),
            "deep": {"a": {"b": {"c": {"d": 1}}}},
        }
    )
    assert isinstance(clean, dict)
    assert len(clean["bio"]) < 100
    assert len(clean["items"]) < 10
    assert '"d"' not in json.dumps(clean["deep"])


def test_summarize_is_one_line_and_never_leaks_secrets() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::summarize_body kind="unit"
    body = json.dumps(
        {"username": "ann\nforged [access] line", "password": "hunter2hunter2"}
    ).encode()

    summary = summarize_body(body).danger_ok

    assert "\n" not in summary and "\r" not in summary
    assert "hunter2hunter2" not in summary
    assert '"username":"ann' in summary
    assert REDACTED in summary


def test_summarize_caps_the_total_length() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::summarize_body kind="unit"
    body = json.dumps({f"field{i}": "v" * 30 for i in range(30)}).encode()
    assert len(summarize_body(body).danger_ok) <= 320


@pytest.mark.parametrize("body", [b"", b"not json", b"\xff\xfe", b'{"a": '])
def test_summarize_reports_unreadable_bodies_as_err(body: bytes) -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::summarize_body kind="unit"
    assert summarize_body(body).is_err


def test_summarize_handles_non_object_json() -> None:
    # frob:tests src/hullbreach_server/logging/payload.py::summarize_body kind="unit"
    assert summarize_body(b"[1, 2, 3]").danger_ok == "[1,2,3]"
    assert summarize_body(b'"just text"').danger_ok == '"just text"'
