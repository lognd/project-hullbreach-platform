"""Unit tests for the App/AppConfig wiring."""

import argparse
from pathlib import Path

import pytest
from fastapi import FastAPI

from hullbreach_server.app import App, AppConfig, create_app


def test_app_config_from_external_with_no_config_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    monkeypatch.setenv("HULLBREACH_DATABASE_URL", "postgresql://u:p@db/x")
    cfg = AppConfig.from_external(
        argparse.Namespace(host=None, port=None), config_file=tmp_path / "missing.toml"
    ).unwrap()
    assert cfg == AppConfig(database_url="postgresql://u:p@db/x")


def test_app_config_precedence_env_over_file_cli_over_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    cfg_file = tmp_path / "pyproject.toml"
    cfg_file.write_text(
        '[tool.hullbreach_server]\nhost = "file-host"\nport = 1\n'
        'database_url = "postgresql://file"\n'
    )
    monkeypatch.setenv("HULLBREACH_PORT", "2")
    monkeypatch.setenv("HULLBREACH_CORS_ORIGINS", "http://a,http://b")

    cfg = AppConfig.from_external(
        argparse.Namespace(host=None, port=3), config_file=cfg_file
    ).unwrap()

    assert cfg.host == "file-host"
    assert cfg.port == 3
    assert cfg.database_url == "postgresql://file"
    assert cfg.cors_origins == ["http://a", "http://b"]


def _external(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, **env: str):
    """from_external against an empty dir with `env` applied (DB url preset)."""
    monkeypatch.setenv("HULLBREACH_DATABASE_URL", "postgresql://u:secret@db/x")
    for key, value in env.items():
        monkeypatch.setenv(f"HULLBREACH_{key.upper()}", value)
    return AppConfig.from_external(
        argparse.Namespace(), config_file=tmp_path / "missing.toml"
    )


def test_from_external_returns_err_for_a_bad_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    result = _external(monkeypatch, tmp_path, port="abc")
    assert result.is_err
    assert "port" in str(result.danger_err)
    assert "secret" not in str(result.danger_err)


def test_from_external_returns_err_for_malformed_toml(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    bad = tmp_path / "pyproject.toml"
    bad.write_text("[tool.hullbreach_server\nport = ")
    result = AppConfig.from_external(argparse.Namespace(), config_file=bad)
    assert result.is_err
    assert "not valid TOML" in str(result.danger_err)


def test_from_external_returns_err_for_a_wrong_typed_file_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    cfg_file = tmp_path / "pyproject.toml"
    cfg_file.write_text(
        '[tool.hullbreach_server]\nport = "x"\ndatabase_url = "sqlite://"\n'
    )
    result = AppConfig.from_external(argparse.Namespace(), config_file=cfg_file)
    assert result.is_err
    assert "port" in str(result.danger_err)


def test_from_external_rejects_a_typo_key_in_the_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    cfg_file = tmp_path / "pyproject.toml"
    cfg_file.write_text('[tool.hullbreach_server]\ndatabse_url = "sqlite://"\n')
    result = AppConfig.from_external(argparse.Namespace(), config_file=cfg_file)
    assert result.is_err
    assert "databse_url" in str(result.danger_err)


def test_from_external_requires_a_database_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """INV-005: no default database credential exists."""
    # frob:tests src/hullbreach_server/app/config.py::AppConfig kind="unit"
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    result = AppConfig.from_external(
        argparse.Namespace(), config_file=tmp_path / "missing.toml"
    )
    assert result.is_err
    assert "database_url" in str(result.danger_err)


def test_from_external_finds_the_config_file_from_a_subdirectory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    (tmp_path / "pyproject.toml").write_text(
        '[tool.hullbreach_server]\nport = 4321\ndatabase_url = "sqlite://"\n'
    )
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    monkeypatch.delenv("HULLBREACH_PORT", raising=False)
    monkeypatch.delenv("HULLBREACH_CONFIG", raising=False)
    monkeypatch.chdir(sub)

    cfg = AppConfig.from_external(argparse.Namespace()).unwrap()

    assert cfg.port == 4321


def test_from_external_honours_hullbreach_config_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    cfg_file = tmp_path / "elsewhere.toml"
    cfg_file.write_text(
        '[tool.hullbreach_server]\nport = 777\ndatabase_url = "sqlite://"\n'
    )
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    monkeypatch.delenv("HULLBREACH_PORT", raising=False)
    monkeypatch.setenv("HULLBREACH_CONFIG", str(cfg_file))
    assert AppConfig.from_external(argparse.Namespace()).unwrap().port == 777


def test_cors_list_is_stripped_and_empty_entries_dropped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    cfg = _external(
        monkeypatch, tmp_path, cors_origins="http://a.test, http://b.test/ ,,"
    ).unwrap()
    assert cfg.cors_origins == ["http://a.test", "http://b.test"]
    empty = _external(monkeypatch, tmp_path, cors_origins="").unwrap()
    assert empty.cors_origins == []


@pytest.mark.parametrize(
    "bad", ["*", "null", "ftp://x.test", "http://x.test/path", "x.test", "http://"]
)
def test_wildcard_and_non_http_cors_origins_are_rejected(
    bad: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """INV-004: credentialed CORS never takes a wildcard or unvalidated origin."""
    # frob:tests src/hullbreach_server/app/config.py::AppConfig kind="unit"
    result = _external(monkeypatch, tmp_path, cors_origins=f"http://ok.test,{bad}")
    assert result.is_err
    assert "cors_origins" in str(result.danger_err)


def test_cors_allows_only_the_api_methods_and_headers() -> None:
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="unit"
    from fastapi.testclient import TestClient

    app = create_app(AppConfig(database_url="sqlite://"))
    with TestClient(app) as client:
        ok = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization",
            },
        )
        bad = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "DELETE",
                "Access-Control-Request-Headers": "x-evil",
            },
        )
        other = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://evil.test",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert ok.status_code == 200
    assert ok.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert ok.headers["access-control-allow-credentials"] == "true"
    assert bad.status_code == 400
    assert "access-control-allow-origin" not in other.headers


def test_create_app_returns_fastapi_with_config_attached() -> None:
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="unit"
    cfg = AppConfig(database_url="sqlite://", port=9)
    app = create_app(cfg)
    assert isinstance(app, FastAPI)
    assert app.state.cfg is cfg


def test_app_is_constructible_without_binding_a_socket() -> None:
    # frob:tests src/hullbreach_server/app/app.py::App kind="unit"
    assert callable(App(AppConfig(database_url="sqlite://")))


# frob:ticket T-0099
def test_app_call_exits_nonzero_naming_host_when_database_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """App.__call__ exits non-zero (naming the host in the ERROR log) instead
    of calling uvicorn.run when the configured database is unreachable."""
    from typani import Err

    from hullbreach_server.app import app as app_module
    from hullbreach_server.db.engine import DatabaseError

    monkeypatch.setattr(
        app_module,
        "check_connectivity",
        lambda engine: Err(
            DatabaseError(
                message="Cannot reach database at bad-host:5432 (database=db): OperationalError"
            )
        ),
    )

    def _fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError(
            "uvicorn.run must not be called when the database is unreachable"
        )

    monkeypatch.setattr("uvicorn.run", _fail_if_called)

    application = App(AppConfig(database_url="sqlite:///:memory:"))

    with pytest.raises(SystemExit) as exc_info:
        application()

    assert exc_info.value.code == 1


def test_app_call_exits_nonzero_on_an_invalid_auth_env_var(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # frob:tests src/hullbreach_server/app/app.py::App kind="unit"
    monkeypatch.setenv("HULLBREACH_LOGIN_RATE_LIMIT_MAX", "zero")

    def _fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("must not serve with an invalid auth env var")

    monkeypatch.setattr("uvicorn.run", _fail_if_called)

    with pytest.raises(SystemExit) as exc_info:
        App(AppConfig(database_url="sqlite://"))()

    assert exc_info.value.code == 1


def test_app_serves_from_the_engine_it_health_checked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The engine checked at startup is the one get_engine hands to requests."""
    # frob:tests src/hullbreach_server/app/app.py::App kind="unit"
    from hullbreach_server.db import dispose_engine, get_engine

    seen: dict[str, object] = {}

    def _fake_run(app: object, **kwargs: object) -> None:
        seen["engine"] = get_engine()

    monkeypatch.setattr("uvicorn.run", _fake_run)
    try:
        App(AppConfig(database_url="sqlite://"))()
        assert str(seen["engine"].url) == "sqlite://"  # type: ignore[attr-defined]
    finally:
        dispose_engine()


def test_lifespan_initialises_and_disposes_the_engine() -> None:
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="unit"
    from fastapi.testclient import TestClient

    from hullbreach_server.db import get_engine

    with TestClient(create_app(AppConfig(database_url="sqlite://"))):
        assert str(get_engine().url) == "sqlite://"
    with pytest.raises(RuntimeError):
        get_engine()
