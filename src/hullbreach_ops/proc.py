"""The only place operator tooling runs other programs.

INV-007 forbids `subprocess` under `src/hullbreach_server/**`; this module
lives outside that glob and is reachable only from the operator CLI. Every
call takes an argv list (never a shell string), so nothing is interpreted
by a shell.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:tests tests/unit/test_ops_proc.py::test_run_captures_output_and_exit_code
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class CommandResult(BaseModel):
    """What a finished command printed and how it exited."""

    argv: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def succeeded(self) -> bool:
        """True when the command exited 0."""
        return self.returncode == 0


# frob:tests tests/unit/test_ops_proc.py::test_run_reports_a_missing_program
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class ProcError(BaseModel):
    """Why a command could not run at all (a non-zero exit is not a ProcError)."""

    kind: Literal["not_found", "timeout", "os_error"]
    message: str

    def __str__(self) -> str:
        """The plain message, so f-strings and logs show it."""
        return self.message


# frob:tests tests/unit/test_ops_proc.py::test_run_captures_output_and_exit_code
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class Runner(Protocol):
    """Runs programs; tests swap in a fake so no real process is started."""

    def which(self, name: str) -> str | None:
        """Full path of `name` on PATH, or None when it is not installed."""
        ...

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> Result[CommandResult, ProcError]:
        """Run `argv` to completion and capture its output."""
        ...

    def spawn(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        log_path: Path,
    ) -> Result[int, ProcError]:
        """Start `argv` in the background with output appended to `log_path`."""
        ...

    def pid_alive(self, pid: int) -> bool:
        """True while process `pid` is still running."""
        ...

    def terminate(self, pid: int, grace: float = 10.0) -> None:
        """Stop the process group led by `pid`: TERM, then KILL after `grace`."""
        ...


# frob:tests tests/unit/test_ops_proc.py::test_run_captures_output_and_exit_code
# frob:tests tests/unit/test_ops_proc.py::test_spawn_and_terminate_a_background_process
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class SubprocessRunner:
    """The real Runner, backed by `subprocess`."""

    def __init__(self) -> None:
        self._children: dict[int, subprocess.Popen[bytes]] = {}

    def which(self, name: str) -> str | None:
        """Full path of `name` on PATH, or None when it is not installed."""
        return shutil.which(name)

    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> Result[CommandResult, ProcError]:
        """Run `argv` to completion and capture its output as text."""
        args = list(argv)
        _log.debug("run: %s", " ".join(args))
        try:
            done = subprocess.run(
                args,
                cwd=cwd,
                env=dict(env) if env is not None else None,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                stdin=subprocess.DEVNULL,
                check=False,
            )
        except FileNotFoundError:
            _log.info("run: %s is not installed", args[0])
            return Err(ProcError(kind="not_found", message=f"{args[0]} not found"))
        except subprocess.TimeoutExpired:
            _log.warning("run: %s timed out after %.0fs", args[0], timeout)
            return Err(
                ProcError(
                    kind="timeout",
                    message=f"{args[0]} did not finish within {timeout:.0f}s",
                )
            )
        except OSError as exc:
            _log.warning("run: %s failed to start (%s)", args[0], type(exc).__name__)
            return Err(ProcError(kind="os_error", message=f"{args[0]}: {exc}"))
        _log.debug("run: %s exited %d", args[0], done.returncode)
        return Ok(
            CommandResult(
                argv=args,
                returncode=done.returncode,
                stdout=done.stdout or "",
                stderr=done.stderr or "",
            )
        )

    def spawn(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        log_path: Path,
    ) -> Result[int, ProcError]:
        """Start `argv` in its own session so stop can end it and its children."""
        args = list(argv)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with log_path.open("ab") as log_file:
                child = subprocess.Popen(
                    args,
                    cwd=cwd,
                    env=dict(env),
                    stdin=subprocess.DEVNULL,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
        except FileNotFoundError:
            _log.info("spawn: %s is not installed", args[0])
            return Err(ProcError(kind="not_found", message=f"{args[0]} not found"))
        except OSError as exc:
            _log.warning("spawn: %s failed (%s)", args[0], type(exc).__name__)
            return Err(ProcError(kind="os_error", message=f"{args[0]}: {exc}"))
        self._children[child.pid] = child
        _log.info("spawn: started %s as pid %d", args[0], child.pid)
        return Ok(child.pid)

    def pid_alive(self, pid: int) -> bool:
        """True while `pid` runs; a child of this process is reaped, not a zombie."""
        child = self._children.get(pid)
        if child is not None:
            return child.poll() is None
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    def terminate(self, pid: int, grace: float = 10.0) -> None:
        """Stop the process group led by `pid`: TERM, then KILL after `grace`."""
        _log.info("terminate: stopping process group %d", pid)
        self._signal_group(pid, signal.SIGTERM)
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            if not self.pid_alive(pid):
                _log.info("terminate: pid %d stopped", pid)
                self._children.pop(pid, None)
                return
            time.sleep(0.2)
        _log.warning("terminate: pid %d ignored SIGTERM; sending SIGKILL", pid)
        self._signal_group(pid, signal.SIGKILL)
        child = self._children.pop(pid, None)
        if child is not None:
            child.wait(timeout=grace)

    @staticmethod
    def _signal_group(pid: int, sig: signal.Signals) -> None:
        """Signal the whole process group; the group may already be gone."""
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            _log.debug("terminate: process group %d already gone", pid)
        except PermissionError:
            _log.warning("terminate: not allowed to signal process group %d", pid)
