"""Unit tests for register's structured per-field errors and failure logging."""

from __future__ import annotations

import pytest

from hullbreach_server.db.models.user import User  # noqa: F401

# frob:ticket 01M5XX28K491XN5RNGABW0Q5RP


def _payload(**overrides: object) -> dict:
    payload = {
        "username": "player_one",
        "email": "player_one@example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    return payload


def _post(client, **overrides: object):
    return client.post("/api/v1/auth/register", json=_payload(**overrides))


def _errors(response) -> dict[str, str]:
    return {item["field"]: item["detail"] for item in response.json()["errors"]}


@pytest.fixture
def logs(server_logs):
    """Server log capture for the whole test."""
    return server_logs


def _ours(logs) -> str:
    return "\n".join(
        r.getMessage() for r in logs.records if r.name.startswith("hullbreach_server")
    )


def test_short_password_states_the_rule_and_names_the_field(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = _post(client, password="1234")

    assert response.status_code == 422
    body = response.json()
    assert body["field"] == "password"
    assert body["detail"] == "password must be at least 8 characters"
    assert _errors(response) == {"password": "password must be at least 8 characters"}


def test_digits_only_password_is_weak(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    response = _post(client, password="12345678")

    assert response.status_code == 422
    assert response.json()["field"] == "password"
    assert "only digits" in _errors(response)["password"]


def test_password_equal_to_username_is_weak(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    response = _post(client, username="samename1", password="samename1")

    assert response.status_code == 422
    assert "must not match the username" in _errors(response)["password"]


def test_invalid_email_names_the_email_field(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = _post(client, email="not-an-email")

    assert response.status_code == 422
    assert _errors(response) == {"email": "enter a valid email address"}


def test_bad_username_states_the_allowed_characters(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = _post(client, username="has space")

    assert "letters, digits" in _errors(response)["username"]


def test_short_username_states_the_minimum(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = _post(client, username="ab")

    assert _errors(response)["username"] == "username must be at least 3 characters"


def test_every_bad_field_is_reported_at_once(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = _post(client, username="ab", email="nope", password="1234")

    assert set(_errors(response)) == {"username", "email", "password"}


def test_missing_field_is_reported_as_required(client) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::field_errors kind="unit"
    response = client.post("/api/v1/auth/register", json={"username": "player_one"})

    assert response.status_code == 422
    assert _errors(response)["email"] == "email is required"
    assert _errors(response)["password"] == "password is required"


def test_duplicate_conflicts_still_carry_a_field(client) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    _post(client)
    response = _post(client, email="other@example.com")

    assert response.status_code == 409
    assert response.json()["field"] == "username"


def test_non_register_validation_errors_keep_the_default_shape(client) -> None:
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="unit"
    response = client.post("/api/v1/auth/login", json={"username": "x"})

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_validation_failure_is_logged_with_field_and_reason_never_the_password(
    client, logs
) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::log_failures kind="unit"
    secret = "hunter2-secret"[:7]
    _post(client, password=secret)

    text = _ours(logs)
    assert "register: rejected field=password" in text
    assert "at least 8 characters" in text
    assert secret not in text


def test_weak_password_failure_log_does_not_echo_the_password(client, logs) -> None:
    # frob:tests src/hullbreach_server/auth/register_errors.py::log_failures kind="unit"
    _post(client, password="87654321")

    text = _ours(logs)
    assert "register: rejected field=password" in text
    assert "87654321" not in text


def test_duplicate_failure_is_logged_with_its_field(client, logs) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    _post(client)
    _post(client, username="another_one")

    assert "register: duplicate email" in _ours(logs)
