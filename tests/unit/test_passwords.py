"""Unit tests for the Argon2id password hashing helper (T-0015)."""

from __future__ import annotations

from hullbreach_server.auth.passwords import (
    hash_password,
    verify_against_dummy_hash,
    verify_password,
)


# frob:ticket T-0015
def test_hash_password_verifies_and_does_not_store_plaintext() -> None:
    """Given a password, hash_password's result verifies with verify_password and is not the plaintext."""
    plain = "correct horse battery staple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed)


# frob:ticket T-0015
def test_verify_password_rejects_wrong_password() -> None:
    """verify_password returns False for a password that does not match the stored hash."""
    hashed = hash_password("correct horse battery staple")

    assert verify_password("wrong password", hashed) is False


# frob:ticket T-0015
def test_hash_password_uses_argon2id_scheme() -> None:
    """hash_password's output identifies itself as an Argon2id hash (the pwdlib recommended scheme)."""
    hashed = hash_password("correct horse battery staple")

    assert hashed.startswith("$argon2id$")


# frob:ticket T-0015
def test_hash_password_is_salted_so_two_hashes_of_the_same_password_differ() -> None:
    """Hashing the same password twice yields two different hashes (per-hash random salt)."""
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")

    assert first != second


def test_verify_password_returns_false_for_a_malformed_stored_hash() -> None:
    # frob:tests src/hullbreach_server/auth/passwords.py::verify_password kind="unit"
    assert verify_password("anything", "not-a-hash") is False
    assert verify_password("anything", "") is False


def test_verify_against_dummy_hash_always_returns_false() -> None:
    # frob:tests src/hullbreach_server/auth/passwords.py::verify_against_dummy_hash kind="unit"
    assert verify_against_dummy_hash("anything") is False
