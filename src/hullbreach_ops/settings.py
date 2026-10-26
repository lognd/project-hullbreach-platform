"""Where the local stack runs: repo root, ports, compose project, platform facts.

Ports come from `HULLBREACH_PORT` (API, also read by the server itself),
`HULLBREACH_WEB_PORT` (vite) and `HULLBREACH_DB_PORT` (the host side of the
compose port mapping), so a second copy of the stack can run beside the
first. The compose project follows docker's own `COMPOSE_PROJECT_NAME`.
"""

from __future__ import annotations

import argparse
import platform
import re
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from typani import Err, Ok, Result

from hullbreach_ops.errors import OpsError
from hullbreach_server.app.config import AppConfig
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# Settings the operator tooling reads, with their defaults.
API_PORT_VAR = "HULLBREACH_PORT"
WEB_PORT_VAR = "HULLBREACH_WEB_PORT"
DB_PORT_VAR = "HULLBREACH_DB_PORT"
API_HOST_VAR = "HULLBREACH_HOST"
COMPOSE_PROJECT_VAR = "COMPOSE_PROJECT_NAME"
_DEFAULT_PORTS = {API_PORT_VAR: 8000, WEB_PORT_VAR: 5173, DB_PORT_VAR: 5432}

# The repo this tooling belongs to; used in links printed for the operator.
REPO_URL = "https://github.com/lognd/project-hullbreach-platform"
GAME_REPO_URL = "https://github.com/lognd/project-hullbreach-game#readme"


# frob:tests tests/unit/test_ops_settings.py::test_platform_info_detects_wsl2
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class PlatformInfo(BaseModel):
    """Which operating system the doctor runs on, and whether that is WSL."""

    model_config = ConfigDict(frozen=True)

    system: str
    release: str
    wsl: bool = False
    wsl_version: int | None = None

    @classmethod
    def detect(cls, proc_root: Path = Path("/proc")) -> PlatformInfo:
        """Read the running system; WSL shows up in the kernel release string."""
        system = platform.system()
        release = platform.release()
        osrelease = proc_root / "sys" / "kernel" / "osrelease"
        try:
            kernel = osrelease.read_text(encoding="utf-8").strip().lower()
        except OSError:
            kernel = release.lower()
        wsl = system == "Linux" and "microsoft" in kernel
        version = None
        if wsl:
            version = 2 if ("wsl2" in kernel or "microsoft-standard" in kernel) else 1
        _log.debug("platform: %s %s wsl=%s version=%s", system, release, wsl, version)
        return cls(system=system, release=release, wsl=wsl, wsl_version=version)

    def describe(self) -> str:
        """Plain-English name of the platform for the report."""
        if self.wsl:
            return f"Windows Subsystem for Linux (WSL{self.wsl_version})"
        if self.system == "Darwin":
            return "macOS"
        return self.system


# noqa: E501  # frob:tests tests/unit/test_ops_settings.py::test_settings_read_ports_from_the_environment
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class OpsSettings(BaseModel):
    """Ports, bind host and compose project for this checkout of the platform."""

    model_config = ConfigDict(frozen=True)

    root: Path
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    web_port: int = 5173
    db_port: int = 5432
    compose_project: str

    @classmethod
    def from_environ(
        cls, environ: Mapping[str, str], root: Path
    ) -> Result[OpsSettings, OpsError]:
        """Read the settings; a non-numeric or out-of-range port is an Err naming it."""
        ports: dict[str, int] = {}
        for var, default in _DEFAULT_PORTS.items():
            raw = environ.get(var, "").strip()
            if not raw:
                ports[var] = default
                continue
            if not raw.isdigit() or not 1 <= int(raw) <= 65535:
                _log.error("settings: %s is not a port number", var)
                return Err(
                    OpsError(
                        message=f"{var} must be a port number between 1 and 65535",
                        fix=[f"Edit .env and set {var} to a number such as {default}."],
                    )
                )
            ports[var] = int(raw)
        project = environ.get(COMPOSE_PROJECT_VAR, "").strip() or _default_project(root)
        return Ok(
            cls(
                root=root,
                api_host=environ.get(API_HOST_VAR, "").strip() or "127.0.0.1",
                api_port=ports[API_PORT_VAR],
                web_port=ports[WEB_PORT_VAR],
                db_port=ports[DB_PORT_VAR],
                compose_project=project,
            )
        )

    @property
    def state_dir(self) -> Path:
        """Ignored directory for pid files, logs and support bundles."""
        return self.root / ".hullbreach"

    @property
    def logs_dir(self) -> Path:
        """Where the API, web and tooling logs are written."""
        return self.state_dir / "logs"

    @property
    def run_dir(self) -> Path:
        """Where pid records of background processes live."""
        return self.state_dir / "run"

    @property
    def db_volume(self) -> str:
        """The docker volume holding this project's database files."""
        return f"{self.compose_project}_pgdata"

    @property
    def api_url(self) -> str:
        """Base URL of the local API as seen from this machine."""
        return f"http://127.0.0.1:{self.api_port}"

    @property
    def web_url(self) -> str:
        """URL of the local website as seen from this machine."""
        return f"http://localhost:{self.web_port}"


def _default_project(root: Path) -> str:
    """Docker compose's own default: the directory name, lowercased and cleaned."""
    return re.sub(r"[^a-z0-9_-]", "", root.name.lower()) or "default"


# frob:tests tests/unit/test_ops_settings.py::test_find_root_walks_up_to_the_checkout
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def find_root(start: Path) -> Path | None:
    """The checkout root at or above `start`: it holds docker-compose.yml and pyproject.toml naming hullbreach_server."""  # noqa: E501
    for directory in (start, *start.parents):
        pyproject = directory / "pyproject.toml"
        if not (directory / "docker-compose.yml").is_file() or not pyproject.is_file():
            continue
        try:
            text = pyproject.read_text(encoding="utf-8")
        except OSError:
            continue
        if 'name = "hullbreach_server"' in text:
            return directory
    return None


def _name_settings(message: str) -> str:
    """Rename config fields (`database_url: ...`) to the variables people set."""
    for name in AppConfig.model_fields:
        message = re.sub(
            rf"(?<![\w.]){name}(?=[.:])", f"HULLBREACH_{name.upper()}", message
        )
    return message


# noqa: E501  # frob:tests tests/unit/test_ops_settings.py::test_load_app_config_names_the_missing_setting
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def load_app_config(settings: OpsSettings) -> Result[AppConfig, OpsError]:
    """The server's own settings, loaded exactly as the server loads them.

    Reads `HULLBREACH_*` from the process environment (where `.env` was
    loaded) and this checkout's pyproject.toml. The error names the setting,
    never its value.
    """
    result = AppConfig.from_external(
        argparse.Namespace(), config_file=settings.root / "pyproject.toml"
    )
    return result.map_err(
        lambda err: OpsError(
            message=_name_settings(str(err)),
            fix=[
                "Open .env (copy .env.example to .env first if it does not exist).",
                "Set the setting named above, for example "
                "HULLBREACH_DATABASE_URL=postgresql://hullbreach:<password>@localhost:5432/hullbreach",
                "Run ./doctor.sh again.",
            ],
        )
    )
