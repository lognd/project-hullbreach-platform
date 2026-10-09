"""The auth package's `__all__` is the boundary the api layer imports from."""

from __future__ import annotations

import hullbreach_server.auth as auth


def test_every_name_in_all_resolves() -> None:
    # frob:tests src/hullbreach_server/auth/__init__.py kind="unit"
    assert all(hasattr(auth, name) for name in auth.__all__)


def test_all_exposes_the_symbols_api_consumes() -> None:
    # frob:tests src/hullbreach_server/auth/__init__.py kind="unit"
    consumed = {
        "require_admin",
        "RegisterRequest",
        "LoginRequest",
        "LoginResponse",
        "UserProfile",
        "SessionInfo",
        "reserve_login_attempt",
        "clear_failed_logins",
        "current_time",
        "require_game_server",
    }
    assert consumed <= set(auth.__all__)


def test_api_auth_imports_only_from_the_package_surface() -> None:
    # frob:tests src/hullbreach_server/api/auth.py kind="unit"
    import inspect

    import hullbreach_server.api.auth as api_auth

    source = inspect.getsource(api_auth)
    assert "hullbreach_server.auth." not in source
