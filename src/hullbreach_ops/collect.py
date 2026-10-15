"""`doctor --collect`: a redacted support bundle to send to the team.

The zip holds what the doctor printed (already redacted), the redacted ends
of the logs under .hullbreach/logs, and a few facts about the computer. It
never includes .env or any setting value.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

from typani import Err, Ok, Result

from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import log_tail
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_LOG_LINES = 400


def _system_facts(ctx: OpsContext) -> str:
    """Operating system, Python and ports; no setting values."""
    s = ctx.settings
    return "\n".join(
        [
            f"generated: {ctx.now():%Y-%m-%d %H:%M:%S %Z}",
            f"platform: {ctx.platform.describe()} ({ctx.platform.system} "
            f"{ctx.platform.release})",
            f"python: {sys.version.split()[0]}",
            f"compose project: {s.compose_project}",
            f"ports: database {s.db_port}, API {s.api_port}, website {s.web_port}",
            f".env present: {(s.root / '.env').is_file()}",
            "",
        ]
    )


# noqa: E501  # frob:tests tests/unit/test_ops_collect.py::test_collect_bundles_redacted_output_and_logs_but_never_env
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def collect(ctx: OpsContext) -> Result[Path, OpsError]:
    """Write hullbreach-support-<time>.zip in the checkout and return its path."""
    s = ctx.settings
    target = s.root / f"hullbreach-support-{ctx.now():%Y%m%d-%H%M%S}.zip"
    logs = sorted(s.logs_dir.glob("*.log")) if s.logs_dir.is_dir() else []
    try:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr("doctor-output.txt", ctx.console.transcript)
            bundle.writestr("system.txt", _system_facts(ctx))
            for log in logs:
                tail = log_tail(log, _LOG_LINES)
                text = "\n".join(ctx.console.redact(line, log=True) for line in tail)
                bundle.writestr(f"logs/{log.name}", text + "\n")
    except OSError as exc:
        _log.error("collect: could not write %s: %s", target, exc)
        return Err(
            OpsError(
                message=f"could not write the support file {target.name}: {exc}",
                fix=["Check there is free disk space and the folder is writable."],
            )
        )
    _log.info("collect: wrote %s with %d log(s)", target, len(logs))
    ctx.console.line()
    ctx.console.line(f"Support file written: {target}")
    ctx.console.line(
        "It contains the doctor output above and the ends of the logs, with "
        "passwords, keys and tokens replaced by <redacted>. .env is not included."
    )
    ctx.console.line("Send it to the team with a sentence about what you were doing.")
    return Ok(target)
