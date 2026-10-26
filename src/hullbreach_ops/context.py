"""Everything an operator command touches, bundled so tests can swap each part."""

from __future__ import annotations

import os
import time
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from hullbreach_ops.console import Console
from hullbreach_ops.probe import HttpClient, PortProbe, SocketPortProbe, UrllibClient
from hullbreach_ops.proc import Runner, SubprocessRunner
from hullbreach_ops.settings import OpsSettings, PlatformInfo


def _utc_now() -> datetime:
    """The current time in UTC (the real clock)."""
    return datetime.now(UTC)


# noqa: E501  # frob:tests tests/unit/test_ops_lifecycle.py::test_start_reports_a_compose_failure_with_fix_steps
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@dataclass
class OpsContext:
    """The settings, environment and I/O seams one operator command runs with.

    `environ` is the process environment (after `.env` was loaded) and is
    what child processes inherit; the platform's own settings loader reads
    `os.environ` directly, so production passes `os.environ` here.
    """

    settings: OpsSettings
    console: Console
    environ: MutableMapping[str, str] = field(default_factory=lambda: os.environ)
    runner: Runner = field(default_factory=SubprocessRunner)
    http: HttpClient = field(default_factory=UrllibClient)
    ports: PortProbe = field(default_factory=SocketPortProbe)
    platform: PlatformInfo = field(default_factory=PlatformInfo.detect)
    sleep: Callable[[float], None] = time.sleep
    now: Callable[[], datetime] = _utc_now
    monotonic: Callable[[], float] = time.monotonic
