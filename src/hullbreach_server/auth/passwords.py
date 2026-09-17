"""Argon2id password hashing (T-0015), per docs/design/sprint-1.md section 5 (D4)."""

from __future__ import annotations

from pwdlib import PasswordHash

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
def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against a stored Argon2id hash."""
    return _hasher.verify(plain, hashed)
