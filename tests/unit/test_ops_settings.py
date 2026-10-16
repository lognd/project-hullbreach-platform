"""Unit tests for operator settings: ports, checkout root, WSL detection."""

from __future__ import annotations

from pathlib import Path

import pytest
from ops_fakes import make_root

from hullbreach_ops.settings import (
    OpsSettings,
    PlatformInfo,
    find_root,
    load_app_config,
)


def test_settings_read_ports_from_the_environment(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/settings.py::OpsSettings kind="unit"
    root = make_root(tmp_path)
    defaults = OpsSettings.from_environ({}, root).danger_ok
    assert (defaults.api_port, defaults.web_port, defaults.db_port) == (
        8000,
        5173,
        5432,
    )
    assert defaults.compose_project == "platform"
    assert defaults.api_url == "http://127.0.0.1:8000"
    assert defaults.web_url == "http://localhost:5173"
    assert defaults.db_volume == "platform_pgdata"
    assert defaults.state_dir == root / ".hullbreach"

    custom = OpsSettings.from_environ(
        {
            "HULLBREACH_PORT": "8004",
            "HULLBREACH_WEB_PORT": "5175",
            "HULLBREACH_DB_PORT": "5434",
            "HULLBREACH_HOST": "0.0.0.0",
            "COMPOSE_PROJECT_NAME": "hbtrial",
        },
        root,
    ).danger_ok
    assert (custom.api_port, custom.web_port, custom.db_port) == (8004, 5175, 5434)
    assert custom.api_host == "0.0.0.0"
    assert custom.db_volume == "hbtrial_pgdata"

    for bad in ("abc", "0", "70000"):
        err = OpsSettings.from_environ({"HULLBREACH_PORT": bad}, root).danger_err
        assert (
            err.message == "HULLBREACH_PORT must be a port number between 1 and 65535"
        )
        assert "HULLBREACH_PORT" in err.fix[0]


def test_find_root_walks_up_to_the_checkout(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/settings.py::find_root kind="unit"
    root = make_root(tmp_path)
    deep = root / "src" / "pkg"
    deep.mkdir(parents=True)
    assert find_root(deep) == root
    assert find_root(tmp_path) is None
    other = tmp_path / "other"
    other.mkdir()
    (other / "docker-compose.yml").write_text("", encoding="utf-8")
    (other / "pyproject.toml").write_text('name = "something_else"\n', encoding="utf-8")
    assert find_root(other) is None


def test_platform_info_detects_wsl2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/settings.py::PlatformInfo kind="unit"
    # frob:tests src/hullbreach_ops/settings.py::PlatformInfo.describe kind="unit"
    kernel = tmp_path / "sys" / "kernel"
    kernel.mkdir(parents=True)
    monkeypatch.setattr("hullbreach_ops.settings.platform.system", lambda: "Linux")

    (kernel / "osrelease").write_text("6.6.87.1-microsoft-standard-WSL2\n")
    wsl2 = PlatformInfo.detect(tmp_path)
    assert (wsl2.wsl, wsl2.wsl_version) == (True, 2)
    assert wsl2.describe() == "Windows Subsystem for Linux (WSL2)"

    (kernel / "osrelease").write_text("4.4.0-19041-Microsoft\n")
    assert PlatformInfo.detect(tmp_path).wsl_version == 1

    (kernel / "osrelease").write_text("6.8.0-45-generic\n")
    assert PlatformInfo.detect(tmp_path).wsl is False

    monkeypatch.setattr("hullbreach_ops.settings.platform.system", lambda: "Darwin")
    mac = PlatformInfo.detect(tmp_path / "missing")
    assert mac.wsl is False
    assert mac.describe() == "macOS"


def test_load_app_config_names_the_missing_setting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/settings.py::load_app_config kind="unit"
    settings = OpsSettings.from_environ({}, make_root(tmp_path)).danger_ok
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    err = load_app_config(settings).danger_err
    assert "HULLBREACH_DATABASE_URL" in err.message
    assert any(".env" in step for step in err.fix)

    url = f"sqlite:///{tmp_path / 'x.db'}"
    monkeypatch.setenv("HULLBREACH_DATABASE_URL", url)
    assert load_app_config(settings).danger_ok.database_url == url
