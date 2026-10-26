"""Fakes for the operator tooling tests: commands, HTTP, ports and the clock.

Every hullbreach_ops seam (OpsContext.runner/http/ports/sleep/monotonic) has a
fake here, so the doctor and scripts are tested without Docker, a network or a
real API.
"""

from __future__ import annotations

import io
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from typani import Err, Ok, Result

from hullbreach_ops.console import Console
from hullbreach_ops.context import OpsContext
from hullbreach_ops.probe import HttpError, HttpResponse
from hullbreach_ops.proc import CommandResult, ProcError
from hullbreach_ops.settings import OpsSettings, PlatformInfo

PYPROJECT = '[project]\nname = "hullbreach_server"\nversion = "0.1.0"\n'

Reply = CommandResult | ProcError


def ok(stdout: str = "", returncode: int = 0, stderr: str = "") -> CommandResult:
    """A finished command with this output (argv is filled in by FakeRunner)."""
    return CommandResult(argv=[], returncode=returncode, stdout=stdout, stderr=stderr)


@dataclass
class FakeRunner:
    """Answers commands from a table keyed by argv prefix (longest prefix wins)."""

    programs: set[str] = field(
        default_factory=lambda: {"docker", "git", "uv", "node", "npm"}
    )
    replies: dict[tuple[str, ...], Reply] = field(default_factory=dict)
    calls: list[list[str]] = field(default_factory=list)
    spawned: list[list[str]] = field(default_factory=list)
    spawn_envs: list[dict[str, str]] = field(default_factory=list)
    alive: set[int] = field(default_factory=set)
    terminated: list[int] = field(default_factory=list)
    next_pid: int = 4100

    def which(self, name: str) -> str | None:
        """The fake path of `name` when it is "installed"."""
        return f"/usr/bin/{name}" if name in self.programs else None

    def run(
        self,
        argv: list[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> Result[CommandResult, ProcError]:
        """Record the call and return the matching reply (default: exit 0)."""
        self.calls.append(list(argv))
        best: tuple[str, ...] = ()
        for prefix in self.replies:
            if tuple(argv[: len(prefix)]) == prefix and len(prefix) > len(best):
                best = prefix
        reply = self.replies.get(best, ok()) if best else ok()
        if isinstance(reply, ProcError):
            return Err(reply)
        return Ok(reply.model_copy(update={"argv": list(argv)}))

    def spawn(
        self,
        argv: list[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        log_path: Path,
    ) -> Result[int, ProcError]:
        """Pretend to start a background process; it stays alive until terminated."""
        self.spawned.append(list(argv))
        self.spawn_envs.append(dict(env))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch()
        self.next_pid += 1
        self.alive.add(self.next_pid)
        return Ok(self.next_pid)

    def pid_alive(self, pid: int) -> bool:
        """True for pids spawned and not yet terminated."""
        return pid in self.alive

    def terminate(self, pid: int, grace: float = 10.0) -> None:
        """End a fake process."""
        self.terminated.append(pid)
        self.alive.discard(pid)

    def ran(self, *prefix: str) -> bool:
        """True when some recorded call starts with `prefix`."""
        return any(tuple(call[: len(prefix)]) == prefix for call in self.calls)


@dataclass
class FakeHttp:
    """Answers HTTP requests from a table keyed by (method, url)."""

    routes: dict[tuple[str, str], HttpResponse] = field(default_factory=dict)
    requests: list[tuple[str, str, dict[str, str], object]] = field(
        default_factory=list
    )

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: object = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """The routed response, or a refused connection for unknown URLs."""
        self.requests.append((method, url, dict(headers or {}), json_body))
        response = self.routes.get((method, url))
        if response is None:
            return Err(HttpError(message=f"no answer from {url} (refused)"))
        return Ok(response)


@dataclass
class FakePorts:
    """Ports that are "open" on this fake machine."""

    open_ports: set[int] = field(default_factory=set)

    def port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """True when `port` is in the open set."""
        return port in self.open_ports


@dataclass
class FakeClock:
    """A monotonic clock that only moves when the code sleeps."""

    now_s: float = 1000.0
    slept: list[float] = field(default_factory=list)

    def monotonic(self) -> float:
        """Current fake time."""
        return self.now_s

    def sleep(self, seconds: float) -> None:
        """Advance the fake time instead of waiting."""
        self.slept.append(seconds)
        self.now_s += seconds


def make_root(tmp_path: Path) -> Path:
    """A minimal checkout: docker-compose.yml plus a hullbreach_server pyproject."""
    root = tmp_path / "platform"
    root.mkdir(exist_ok=True)
    (root / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    return root


def make_ctx(
    tmp_path: Path,
    environ: dict[str, str] | None = None,
    *,
    runner: FakeRunner | None = None,
    http: FakeHttp | None = None,
    ports: FakePorts | None = None,
    platform: PlatformInfo | None = None,
    console: Console | None = None,
    clock: FakeClock | None = None,
) -> OpsContext:
    """An OpsContext over a fake checkout with every seam replaced by a fake."""
    root = make_root(tmp_path)
    env = dict(environ or {})
    settings = OpsSettings.from_environ(env, root).danger_ok
    clock = clock or FakeClock()
    return OpsContext(
        settings=settings,
        console=console or Console(io.StringIO(), interactive=False),
        environ=env,
        runner=runner or FakeRunner(),
        http=http or FakeHttp(),
        ports=ports or FakePorts(),
        platform=platform or PlatformInfo(system="Linux", release="6.0"),
        sleep=clock.sleep,
        now=lambda: datetime(2026, 10, 15, 12, 30, 0, tzinfo=UTC),
        monotonic=clock.monotonic,
    )


def output(ctx: OpsContext) -> str:
    """Everything the console printed (the transcript, redacted)."""
    return ctx.console.transcript
