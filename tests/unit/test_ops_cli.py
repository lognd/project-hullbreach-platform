"""Unit tests for the operator subcommand wiring."""

from __future__ import annotations

import argparse
import io
import logging
from collections.abc import Iterator

import pytest

from hullbreach_ops import cli
from hullbreach_ops.console import Console
from hullbreach_server.__main__ import _build_parser


@pytest.fixture
def keep_root_logging() -> Iterator[None]:
    """run_ops sends logs to a file; put the test's own handlers back afterwards."""
    root = logging.getLogger()
    saved = list(root.handlers)
    yield
    for handler in list(root.handlers):
        root.removeHandler(handler)
        if handler not in saved:
            handler.close()
    for handler in saved:
        root.addHandler(handler)


def test_every_command_is_wired() -> None:
    # frob:tests src/hullbreach_ops/cli.py::add_ops_commands kind="unit"
    parser = _build_parser()
    for name in cli.COMMANDS:
        extra = ["someone", "5"] if name == "grant-credits" else []
        assert parser.parse_args([name, *extra]).command == name
    granted = parser.parse_args(["grant-credits", "demo_pilot", "500"])
    assert (granted.user, granted.amount) == ("demo_pilot", 500)
    with pytest.raises(SystemExit):
        parser.parse_args(["grant-credits", "demo_pilot", "lots"])
    args = parser.parse_args(["doctor", "--demo", "platform", "--only", "api"])
    assert (args.demo, args.only, args.collect) == ("platform", "api", False)
    assert parser.parse_args(["start", "--host", "0.0.0.0"]).bind_host == "0.0.0.0"
    assert parser.parse_args(["demo", "--host", "0.0.0.0"]).bind_host == "0.0.0.0"
    with pytest.raises(SystemExit):
        parser.parse_args(["doctor", "--demo", "nonsense"])


def test_run_ops_outside_a_checkout_explains_where_to_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # frob:tests src/hullbreach_ops/cli.py::run_ops kind="unit"
    monkeypatch.setattr("hullbreach_ops.cli.find_root", lambda _p: None)
    console = Console(io.StringIO(), interactive=False)
    assert cli.run_ops(argparse.Namespace(command="status"), console) == 1
    assert (
        "Problem: this is not inside a copy of the Hullbreach platform code"
        in console.transcript
    )
    assert "cd project-hullbreach-platform" in console.transcript


def test_run_ops_reports_a_bad_port_setting(
    monkeypatch: pytest.MonkeyPatch, keep_root_logging: None
) -> None:
    # frob:tests src/hullbreach_ops/cli.py::run_ops kind="unit"
    monkeypatch.setenv("HULLBREACH_PORT", "abc")
    console = Console(io.StringIO(), interactive=False)
    assert cli.run_ops(argparse.Namespace(command="status"), console) == 1
    assert "HULLBREACH_PORT must be a port number" in console.transcript


def test_dispatch_passes_grant_arguments_and_reports_a_refusal(tmp_path) -> None:
    # frob:tests src/hullbreach_ops/cli.py::add_ops_commands kind="unit"
    from tests.unit.ops_fakes import make_ctx, output

    ctx = make_ctx(tmp_path, {})  # demo mode is off: the command must refuse
    args = _build_parser().parse_args(["grant-credits", "demo_pilot", "500"])

    assert cli._dispatch(ctx, args) == 1
    assert "HULLBREACH_DEMO_MODE" in output(ctx)
