"""Unit tests for the doctor's database probes (SQLite file databases)."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from hullbreach_ops import dbstate


def _admin_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """The settings the seed needs to create the first admin."""
    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "placeholder-admin-pw")


def test_connect_explains_why_it_failed() -> None:
    # frob:tests src/hullbreach_ops/dbstate.py::connect kind="unit"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"postgresql+psycopg://hullbreach:placeholder-pw@127.0.0.1:{port}/hullbreach"
    err = dbstate.connect(url).danger_err
    assert err.message.endswith(": nothing is listening on that port")
    assert "placeholder-pw" not in err.message


def test_dbstate_reports_connect_migration_and_seed_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/dbstate.py::connect kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::migration_state kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::MigrationState kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::migrate kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::seed_state kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::SeedState kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::run_seed kind="unit"
    # frob:tests src/hullbreach_ops/dbstate.py::delete_user kind="unit"
    _admin_env(monkeypatch)
    url = f"sqlite:///{tmp_path / 'doctor.db'}"
    assert dbstate.connect(url).is_ok

    before = dbstate.migration_state(url).danger_ok
    assert before.current == []
    assert before.heads
    assert not before.at_head
    assert dbstate.seed_state(url).is_err  # no tables yet

    assert dbstate.migrate(url).is_ok
    assert dbstate.migration_state(url).danger_ok.at_head
    assert dbstate.seed_state(url).danger_ok.items == 0

    assert dbstate.run_seed(url).is_ok
    seeded = dbstate.seed_state(url).danger_ok
    assert seeded.items >= 100
    assert seeded.admins == 1

    assert dbstate.delete_user(url, "admin").danger_ok is True
    assert dbstate.delete_user(url, "admin").danger_ok is False
    assert dbstate.seed_state(url).danger_ok.admins == 0


def test_run_seed_explains_a_missing_admin_password(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/dbstate.py::run_seed kind="unit"
    _admin_env(monkeypatch)
    monkeypatch.delenv("HULLBREACH_ADMIN_PASSWORD")
    url = f"sqlite:///{tmp_path / 'doctor.db'}"
    assert dbstate.migrate(url).is_ok
    err = dbstate.run_seed(url).danger_err
    assert err.message.startswith("seeding failed:")
    assert any("HULLBREACH_ADMIN_PASSWORD" in step for step in err.fix)
