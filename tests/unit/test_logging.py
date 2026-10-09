"""Unit tests for the logging setup."""

import logging
import os
import subprocess
import sys

import pytest

from hullbreach_server.logging.filter import BelowLevelFilter
from hullbreach_server.logging.formatter import SimpleFormatter
from hullbreach_server.logging.logger import get_logger


def _record(level: int) -> logging.LogRecord:
    return logging.LogRecord("x", level, __file__, 1, "hello", None, None)


def test_below_level_filter_passes_records_below_threshold() -> None:
    # frob:tests src/hullbreach_server/logging/filter.py::BelowLevelFilter.filter kind="unit"
    below = BelowLevelFilter(below="WARNING")
    assert below.filter(_record(logging.INFO)) is True
    assert below.filter(_record(logging.WARNING)) is False


def test_simple_formatter_prefixes_level_at_warning_and_above() -> None:
    # frob:tests src/hullbreach_server/logging/formatter.py::SimpleFormatter.format kind="unit"
    fmt = SimpleFormatter()
    assert fmt.format(_record(logging.INFO)) == "hello"
    assert fmt.format(_record(logging.WARNING)) == "WARNING: hello"


def test_get_logger_returns_a_configured_logger() -> None:
    # frob:tests src/hullbreach_server/logging/logger.py::get_logger kind="unit"
    log = get_logger(__name__)
    assert isinstance(log, logging.Logger)


def test_simple_formatter_appends_traceback_for_exception_records() -> None:
    # frob:tests src/hullbreach_server/logging/formatter.py::SimpleFormatter.format kind="unit"
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        import sys

        record = logging.LogRecord(
            "x", logging.ERROR, __file__, 1, "failed", None, sys.exc_info()
        )
    out = SimpleFormatter().format(record)
    assert out.startswith("ERROR: failed\nTraceback")
    assert "RuntimeError: boom" in out


def test_simple_formatter_appends_stack_info() -> None:
    # frob:tests src/hullbreach_server/logging/formatter.py::SimpleFormatter.format kind="unit"
    record = logging.LogRecord(
        "x", logging.INFO, __file__, 1, "here", None, None, sinfo="Stack (most recent)"
    )
    assert SimpleFormatter().format(record) == "here\nStack (most recent)"


def test_below_level_filter_rejects_an_unknown_level_name() -> None:
    # frob:tests src/hullbreach_server/logging/filter.py::BelowLevelFilter kind="unit"
    with pytest.raises(ValueError, match="WARN1NG"):
        BelowLevelFilter(below="WARN1NG")


def test_below_level_filter_accepts_level_names_case_insensitively() -> None:
    # frob:tests src/hullbreach_server/logging/filter.py::BelowLevelFilter kind="unit"
    assert BelowLevelFilter(below="error").filter(_record(logging.WARNING)) is True


# Runs in a fresh interpreter because logging.config binds ext://sys.stdout at
# dictConfig time, which pytest's per-test capture would otherwise swap out.
_ROUTING_SCRIPT = """
from hullbreach_server.logging import get_logger
from hullbreach_server.logging.logger import _init

log = get_logger("routing.check")
_init()  # a second init must stay a no-op: no duplicate handlers
log.info("info-line")
log.warning("warn-line")
try:
    raise RuntimeError("boom")
except RuntimeError:
    log.exception("exc-line")
"""


def test_config_toml_routes_info_to_stdout_and_warnings_to_stderr() -> None:
    # frob:tests src/hullbreach_server/logging/logger.py::get_logger kind="integration"
    proc = subprocess.run(
        [sys.executable, "-c", _ROUTING_SCRIPT],
        capture_output=True,
        text=True,
        check=True,
        # Mirror this interpreter's import path so the child finds the package
        # however pytest was launched (uv run, frob test's own runner).
        env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)},
    )
    assert proc.stdout == "info-line\n"
    assert proc.stderr.splitlines()[0] == "WARNING: warn-line"
    assert proc.stderr.count("warn-line") == 1
    assert "ERROR: exc-line" in proc.stderr
    assert "RuntimeError: boom" in proc.stderr
