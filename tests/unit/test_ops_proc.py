"""Unit tests for the real subprocess runner (uses the test's own Python)."""

from __future__ import annotations

import sys
from pathlib import Path

from hullbreach_ops.proc import SubprocessRunner


def test_run_captures_output_and_exit_code() -> None:
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::CommandResult kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner.run kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::Runner.run kind="unit"
    code = "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)"
    done = SubprocessRunner().run([sys.executable, "-c", code]).danger_ok
    assert (done.returncode, done.stdout.strip(), done.stderr.strip()) == (
        3,
        "out",
        "err",
    )
    assert not done.succeeded


def test_run_reports_a_missing_program() -> None:
    # frob:tests src/hullbreach_ops/proc.py::ProcError kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner.which kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::Runner.which kind="unit"
    runner = SubprocessRunner()
    err = runner.run(["hullbreach-no-such-program"]).danger_err
    assert err.kind == "not_found"
    assert str(err) == "hullbreach-no-such-program not found"
    assert runner.which("hullbreach-no-such-program") is None
    slow = runner.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2)
    assert slow.danger_err.kind == "timeout"


def test_spawn_and_terminate_a_background_process(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner.spawn kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner.pid_alive kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::SubprocessRunner.terminate kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::Runner.spawn kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::Runner.pid_alive kind="unit"
    # frob:tests src/hullbreach_ops/proc.py::Runner.terminate kind="unit"
    runner = SubprocessRunner()
    log = tmp_path / "logs" / "child.log"
    code = "import time; print('started', flush=True); time.sleep(60)"
    pid = runner.spawn(
        [sys.executable, "-c", code], cwd=tmp_path, env={}, log_path=log
    ).danger_ok
    assert runner.pid_alive(pid)
    runner.terminate(pid, grace=5.0)
    assert not runner.pid_alive(pid)
    missing = runner.spawn(
        ["hullbreach-no-such-program"], cwd=tmp_path, env={}, log_path=log
    )
    assert missing.danger_err.kind == "not_found"
