"""Argon2id password hashing (T-0015), per docs/design/sprint-1.md section 5 (D4)."""

from __future__ import annotations

import functools
import secrets

from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_hasher = PasswordHash.recommended()  # Argon2id


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_passwords.py::test_hash_password_verifies_and_does_not_store_plaintext  # noqa: E501
# frob:tests tests/unit/test_passwords.py::test_hash_password_uses_argon2id_scheme
# frob:tests tests/unit/test_passwords.py::test_hash_password_is_salted_so_two_hashes_of_the_same_password_differ  # noqa: E501
# frob:tests tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin
def hash_password(plain: str) -> str:
    """Hash a plaintext password with Argon2id; the result is safe to store."""
    return _hasher.hash(plain)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_passwords.py::test_hash_password_verifies_and_does_not_store_plaintext  # noqa: E501
# frob:tests tests/unit/test_passwords.py::test_verify_password_rejects_wrong_password
# frob:tests tests/unit/test_passwords.py::test_verify_password_returns_false_for_a_malformed_stored_hash  # noqa: E501
def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored Argon2id hash.

    Never raises for bad stored data: an unrecognised or corrupt `hashed`
    (legacy row, truncated value) is logged at ERROR and answers False, so a
    login against such a row is an ordinary 401, not a 500.
    """
    try:
        return _hasher.verify(plain, hashed)
    except PwdlibError as exc:
        _log.error("verify_password: stored hash is unusable (%s)", type(exc).__name__)
        return False


@functools.cache
def _dummy_hash() -> str:
    """A throwaway valid Argon2id hash, built once, used to equalise login timing."""
    return _hasher.hash(secrets.token_urlsafe(16))


# frob:invariant INV-001
# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_passwords.py::test_verify_against_dummy_hash_always_returns_false  # noqa: E501
def verify_against_dummy_hash(plain: str) -> bool:
    """Run one full Argon2 verify against a dummy hash and return False.

    Called on the unknown-username login path so it costs the same as a real
    verification and response time cannot enumerate accounts.
    """
    _hasher.verify(plain, _dummy_hash())
    return False
