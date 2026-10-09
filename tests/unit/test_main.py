"""Unit test for the CLI entry point."""

import argparse
import sys
from pathlib import Path

import pytest

from hullbreach_server.__main__ import _db_upgrade, main


def test_main_prints_help_and_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/hullbreach_server/__main__.py::main kind="unit"
    monkeypatch.setattr(sys, "argv", ["hullbreach_server", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0


def test_db_upgrade_runs_from_any_directory_and_reports_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    # frob:tests src/hullbreach_server/db/migrate.py::upgrade_to_head kind="unit"
    # frob:tests src/hullbreach_server/db/migrate.py::build_alembic_config kind="unit"
    from sqlalchemy import create_engine, inspect

    workdir = tmp_path / "elsewhere"
    workdir.mkdir()
    monkeypatch.chdir(workdir)  # no alembic.ini here
    db_file = tmp_path / "up.db"
    monkeypatch.setenv("HULLBREACH_DATABASE_URL", f"sqlite:///{db_file}")

    _db_upgrade(argparse.Namespace())

    assert "users" in inspect(create_engine(f"sqlite:///{db_file}")).get_table_names()

    monkeypatch.setenv(
        "HULLBREACH_DATABASE_URL", f"sqlite:///{tmp_path / 'no_such_dir' / 'x.db'}"
    )
    with pytest.raises(SystemExit) as exc:
        _db_upgrade(argparse.Namespace())
    assert exc.value.code == 1
    assert "db upgrade failed" in capsys.readouterr().err


def test_main_exits_with_a_clear_message_when_database_url_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    # frob:tests src/hullbreach_server/__main__.py::main kind="unit"
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HULLBREACH_DATABASE_URL", raising=False)
    monkeypatch.delenv("HULLBREACH_CONFIG", raising=False)
    monkeypatch.setattr(sys, "argv", ["hullbreach_server", "db", "upgrade"])
    monkeypatch.setattr("hullbreach_server.__main__.load_dotenv", lambda: None)

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    assert "database_url" in capsys.readouterr().err
