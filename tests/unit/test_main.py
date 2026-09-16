"""Unit test for the CLI entry point."""

import sys

import pytest

from hullbreach_server.__main__ import main


def test_main_prints_help_and_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    # frob:tests src/hullbreach_server/__main__.py::main kind="unit"
    monkeypatch.setattr(sys, "argv", ["hullbreach_server", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
