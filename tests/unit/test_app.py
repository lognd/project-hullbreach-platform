"""Unit tests for the App/AppConfig wiring."""

import argparse
from pathlib import Path

import pytest
from fastapi import FastAPI

from hullbreach_server.app import App, AppConfig, create_app


def test_app_config_from_external_with_no_config_file(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
    cfg = AppConfig.from_external(
        argparse.Namespace(host=None, port=None), config_file=tmp_path / "missing.toml"
    )
    assert cfg == AppConfig()


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
    )

    assert cfg.host == "file-host"
    assert cfg.port == 3
    assert cfg.database_url == "postgresql://file"
    assert cfg.cors_origins == ["http://a", "http://b"]


def test_create_app_returns_fastapi_with_config_attached() -> None:
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="unit"
    cfg = AppConfig(port=9)
    app = create_app(cfg)
    assert isinstance(app, FastAPI)
    assert app.state.cfg is cfg


def test_app_is_constructible_without_binding_a_socket() -> None:
    # frob:tests src/hullbreach_server/app/app.py::App kind="unit"
    assert callable(App(AppConfig()))
