"""The shapes every doctor check shares: its result, its definition, the run state."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from pydantic import BaseModel

from hullbreach_ops.context import OpsContext
from hullbreach_ops.readme_links import ReadmeSection
from hullbreach_server.app.config import AppConfig

# Which demos `doctor --demo` knows, and what each one is, in the operator's
# words. Kept here (not in doctor.py) so building the CLI parser stays light.
# frob:tests tests/unit/test_ops_doctor.py::test_demo_profiles_pick_their_checks
# frob:doc docs/index.md#operator-scripts-and-the-doctor
DEMOS = {
    "website": "the website on this computer: sign up, sign in, edit your profile",
    "guest": "the game without a platform account (the platform is not used)",
    "online": "the game's online lobby through Unity Relay (the platform is not used)",
    "platform": "the game with players signed in to this platform",
}


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class Status(StrEnum):
    """Outcome of one check; PENDING means a check it needs did not pass."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    PENDING = "PENDING"


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class CheckResult(BaseModel):
    """What one check found, and for WARN/FAIL the numbered steps that fix it."""

    status: Status
    summary: str
    details: list[str] = []
    fix: list[str] = []
    readme: ReadmeSection | None = None

    @property
    def usable(self) -> bool:
        """True when checks that need this one may run (PASS or WARN)."""
        return self.status in (Status.PASS, Status.WARN)


def ok(summary: str, details: list[str] | None = None) -> CheckResult:
    """A passing result."""
    return CheckResult(status=Status.PASS, summary=summary, details=details or [])


def warn(
    summary: str,
    fix: list[str] | None = None,
    readme: ReadmeSection | None = None,
    details: list[str] | None = None,
) -> CheckResult:
    """A result that works but deserves attention."""
    return CheckResult(
        status=Status.WARN,
        summary=summary,
        fix=fix or [],
        readme=readme,
        details=details or [],
    )


def fail(
    summary: str,
    fix: list[str],
    readme: ReadmeSection | None = None,
    details: list[str] | None = None,
) -> CheckResult:
    """A blocking failure; checks that need this one are not run."""
    return CheckResult(
        status=Status.FAIL,
        summary=summary,
        fix=fix,
        readme=readme,
        details=details or [],
    )


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@dataclass
class DoctorRun:
    """State shared by the checks of one doctor run."""

    ctx: OpsContext
    profile: str = "full"
    app_config: AppConfig | None = None
    results: dict[str, CheckResult] = field(default_factory=dict)
    cleanups: list[Callable[[], None]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    session_token: str | None = None

    @property
    def needs_game(self) -> bool:
        """True when the chosen demo requires game-server sign-in to work."""
        return self.profile == "platform"


CheckFn = Callable[[DoctorRun], CheckResult]


# frob:tests tests/unit/test_ops_doctor.py::test_failed_check_marks_dependents_pending
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@dataclass(frozen=True)
class Check:
    """One doctor check: id, what it checks, which checks it needs, and its code."""

    id: str
    title: str
    run: CheckFn
    needs: tuple[str, ...] = ()
