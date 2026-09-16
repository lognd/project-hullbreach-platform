"""Unit tests for the planned Argon2id password hashing helper (T-0015).
`hullbreach_server.auth.passwords` does not exist yet; imports are lazy
inside each test body so collection succeeds.
"""

from __future__ import annotations

import pytest


# frob:ticket T-0015
@pytest.mark.xfail(strict=True, reason="T-0015 not implemented")
def test_hash_password_verifies_and_does_not_store_plaintext() -> None:
    """Given a password, hash_password's result verifies with verify_password and is not the plaintext."""
    from hullbreach_server.auth.passwords import hash_password, verify_password

    plain = "correct horse battery staple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed)


# frob:ticket T-0015
@pytest.mark.xfail(strict=True, reason="T-0015 not implemented")
def test_verify_password_rejects_wrong_password() -> None:
    """verify_password returns False for a password that does not match the stored hash."""
    from hullbreach_server.auth.passwords import hash_password, verify_password

    hashed = hash_password("correct horse battery staple")

    assert verify_password("wrong password", hashed) is False


# frob:ticket T-0015
@pytest.mark.xfail(strict=True, reason="T-0015 not implemented")
def test_hash_password_uses_argon2id_scheme() -> None:
    """hash_password's output identifies itself as an Argon2id hash (the pwdlib recommended scheme)."""
    from hullbreach_server.auth.passwords import hash_password

    hashed = hash_password("correct horse battery staple")

    assert hashed.startswith("$argon2id$")


# frob:ticket T-0015
@pytest.mark.xfail(strict=True, reason="T-0015 not implemented")
def test_hash_password_is_salted_so_two_hashes_of_the_same_password_differ() -> None:
    """Hashing the same password twice yields two different hashes (per-hash random salt)."""
    from hullbreach_server.auth.passwords import hash_password

    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")

    assert first != second
