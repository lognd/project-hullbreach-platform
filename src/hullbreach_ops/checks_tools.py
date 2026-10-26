"""Doctor checks for the computer and its tools: OS, git, uv, Python, Node, Docker."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

from hullbreach_ops import readme_links as rl
from hullbreach_ops.checkbase import Check, CheckResult, DoctorRun, fail, ok, warn
from hullbreach_ops.lifecycle import compose_argv
from hullbreach_ops.settings import REPO_URL
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_RERUN = "Run ./doctor.sh again."
_WRAPPER = "Run ./doctor.sh (not uv run ...): it offers to install missing tools."
_DOCKER_DESKTOP_EXE = Path("/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe")


def _version(text: str) -> tuple[int, ...] | None:
    """The first dotted version number in `text`, e.g. (22, 18, 0)."""
    found = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text)
    if not found:
        return None
    return tuple(int(part) for part in found.groups() if part is not None)


# noqa: E501  # frob:tests tests/unit/test_ops_checks_tools.py::test_satisfies_engines_handles_caret_and_ranges
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def satisfies(version: tuple[int, ...], spec: str) -> bool:
    """Whether `version` meets an npm-style spec using `^x.y.z`, `>=x.y.z` and `||`."""
    for clause in spec.split("||"):
        clause = clause.strip()
        wanted = _version(clause)
        if wanted is None:
            continue
        padded = (*version, 0, 0)[:3]
        floor = (*wanted, 0, 0)[:3]
        if clause.startswith("^") and padded[0] == floor[0] and padded >= floor:
            return True
        if clause.startswith(">=") and padded >= floor:
            return True
    return False


def check_os(run: DoctorRun) -> CheckResult:
    """Name the OS; refuse native Windows (the platform runs under WSL there)."""
    info = run.ctx.platform
    if info.system == "Windows":
        return fail(
            "native Windows is not supported; use WSL (Ubuntu inside Windows)",
            [
                "Double-click doctor.cmd in this folder: it explains how to "
                "install WSL step by step.",
                "Then open Ubuntu and clone the code again inside it.",
            ],
            rl.TERMINAL,
        )
    if info.wsl and info.wsl_version == 1:
        return fail(
            "this is WSL 1; Docker needs WSL 2",
            [
                "In Windows PowerShell run: wsl --set-version Ubuntu 2",
                "Open Ubuntu again and run ./doctor.sh.",
            ],
            rl.TOOLS,
        )
    location = run.ctx.settings.root
    if info.wsl and str(location).startswith("/mnt/"):
        return warn(
            f"{info.describe()}, but the code is on the Windows drive ({location})",
            [
                "Clone the code inside Linux instead (much faster, fewer "
                "permission problems): cd ~ && git clone " + REPO_URL + ".git",
            ],
            rl.DOCTOR,
        )
    return ok(info.describe())


def check_git(run: DoctorRun) -> CheckResult:
    """git is installed."""
    ctx = run.ctx
    if ctx.runner.which("git") is None:
        return fail("git is not installed", [_WRAPPER, _RERUN], rl.GIT)
    result = ctx.runner.run(["git", "--version"])
    version = result.danger_ok.stdout.strip() if result.is_ok else "git"
    return ok(version)


def check_repo(run: DoctorRun) -> CheckResult:
    """This folder is a git clone of the platform and not behind origin/main."""
    ctx = run.ctx
    root = ctx.settings.root

    def git(*args: str, timeout: float = 30) -> str | None:
        result = ctx.runner.run(["git", "-C", str(root), *args], timeout=timeout)
        if result.is_ok and result.danger_ok.succeeded:
            return result.danger_ok.stdout.strip()
        return None

    if git("rev-parse", "--is-inside-work-tree") != "true":
        return warn(
            "this folder is not a git clone (downloaded as a zip?), so it cannot "
            "be updated",
            [f"Get it with git instead: git clone {REPO_URL}.git"],
            rl.DOCTOR,
        )
    origin = git("remote", "get-url", "origin") or ""
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    if "project-hullbreach-platform" not in origin:
        return warn(
            f"git clone on branch {branch}, but 'origin' is not the platform repo",
            [f"Check with: git remote -v (expected {REPO_URL})"],
            rl.DOCTOR,
        )
    if git("fetch", "--quiet", "origin", "main", timeout=60) is None:
        return warn(
            f"git clone on branch {branch}; could not reach GitHub to check "
            "for updates",
            ["Check your internet connection, then run ./doctor.sh again."],
            rl.DOCTOR,
        )
    counts = git("rev-list", "--left-right", "--count", "HEAD...origin/main")
    if counts is None:
        return ok(f"git clone on branch {branch}")
    ahead, behind = (int(n) for n in counts.split())
    _log.info("repo: branch=%s ahead=%d behind=%d", branch, ahead, behind)
    if behind:
        fix = (
            ["Get the latest code: git pull"]
            if branch == "main"
            else ["Switch to the main code and update it: git switch main && git pull"]
        )
        return warn(
            f"branch {branch} is {behind} commit(s) behind origin/main",
            [*fix, "Then run ./doctor.sh again (new code may need new packages)."],
            rl.DOCTOR,
        )
    extra = f", {ahead} commit(s) ahead" if ahead else ""
    return ok(f"git clone on branch {branch}, up to date with origin/main{extra}")


def check_uv(run: DoctorRun) -> CheckResult:
    """uv (the Python package manager) is installed."""
    ctx = run.ctx
    if ctx.runner.which("uv") is None:
        return fail("uv is not installed", [_WRAPPER, _RERUN], rl.UV)
    result = ctx.runner.run(["uv", "--version"])
    return ok(result.danger_ok.stdout.strip() if result.is_ok else "uv")


def check_python(run: DoctorRun) -> CheckResult:
    """The Python running the platform meets pyproject's requires-python."""
    pyproject = run.ctx.settings.root / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    spec = data.get("project", {}).get("requires-python", ">=3.11")
    have = sys.version_info[:3]
    shown = ".".join(str(n) for n in have)
    if not satisfies(have, spec):
        return fail(
            f"Python {shown} is too old (needs {spec})",
            ["Let uv install the right Python: uv python install 3.12", _RERUN],
            rl.UV,
        )
    return ok(f"Python {shown} (needs {spec})")


def check_py_deps(run: DoctorRun) -> CheckResult:
    """The Python packages match uv.lock (`uv sync` was run)."""
    ctx = run.ctx
    result = ctx.runner.run(
        ["uv", "sync", "--locked", "--check"],
        cwd=ctx.settings.root,
        env=ctx.environ,
        timeout=120,
    )
    if result.is_ok and result.danger_ok.succeeded:
        return ok("Python packages installed and up to date")
    return fail(
        "the Python packages are missing or out of date",
        ["Run: uv sync", _RERUN],
        rl.PACKAGES,
    )


def _node_spec(root: Path) -> str:
    """The Node versions package.json accepts (its `engines.node`)."""
    try:
        data = json.loads((root / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    engines = data.get("engines") or {}
    return str(engines.get("node", ""))


def check_node(run: DoctorRun) -> CheckResult:
    """Node.js and npm are installed, at a version package.json accepts."""
    ctx = run.ctx
    if ctx.runner.which("node") is None or ctx.runner.which("npm") is None:
        return fail(
            "Node.js (node and npm) is not installed", [_WRAPPER, _RERUN], rl.NODE
        )
    result = ctx.runner.run(["node", "--version"])
    text = result.danger_ok.stdout.strip() if result.is_ok else ""
    version = _version(text)
    spec = _node_spec(ctx.settings.root)
    if version is None:
        return fail("could not read the Node.js version", [_WRAPPER], rl.NODE)
    if spec and not satisfies(version, spec):
        return fail(
            f"Node.js {text} is not supported (package.json needs {spec})",
            [
                "Install the version in .nvmrc: nvm install && nvm use",
                "(no nvm? run ./doctor.sh, it offers to install it)",
                _RERUN,
            ],
            rl.NODE,
        )
    return ok(f"Node.js {text} (needs {spec or 'any'})")


def check_web_deps(run: DoctorRun) -> CheckResult:
    """The website's packages are installed (`npm ci` was run)."""
    ctx = run.ctx
    root = ctx.settings.root
    fix = ["Run: npm ci", _RERUN]
    if not (root / "node_modules").is_dir():
        return fail("the website's packages are not installed", fix, rl.PACKAGES)
    result = ctx.runner.run(
        ["npm", "ls", "--depth=0"], cwd=root, env=ctx.environ, timeout=120
    )
    if result.is_ok and result.danger_ok.succeeded:
        return ok("website packages installed")
    return fail(
        "the website's packages are incomplete or out of date", fix, rl.PACKAGES
    )


def check_docker(run: DoctorRun) -> CheckResult:
    """The docker command and its compose plugin are installed."""
    ctx = run.ctx
    if ctx.runner.which("docker") is None:
        fix = [_WRAPPER]
        if ctx.platform.wsl:
            fix = [
                "Install Docker Desktop for Windows: https://docs.docker.com/desktop/setup/install/windows-install/",
                "In Docker Desktop: Settings > Resources > WSL integration > turn on "
                "your Ubuntu, then Apply & restart.",
                "Close and reopen Ubuntu, then run ./doctor.sh again.",
            ]
        return fail("docker is not installed (or not on PATH)", fix, rl.DOCKER)
    compose = ctx.runner.run(["docker", "compose", "version", "--short"])
    if compose.is_err or not compose.danger_ok.succeeded:
        return fail(
            "docker is installed but 'docker compose' is missing",
            [
                "Install the Compose plugin: https://docs.docker.com/compose/install/",
                _RERUN,
            ],
            rl.DOCKER,
        )
    return ok(f"docker with compose {compose.danger_ok.stdout.strip()}")


def check_docker_daemon(run: DoctorRun) -> CheckResult:
    """The Docker engine is running and this user may talk to it."""
    ctx = run.ctx
    result = ctx.runner.run(
        ["docker", "info", "--format", "{{.ServerVersion}}"], timeout=30
    )
    if result.is_ok and result.danger_ok.succeeded:
        return ok(f"Docker engine {result.danger_ok.stdout.strip()} is running")
    text = ""
    if result.is_ok:
        text = (result.danger_ok.stderr + result.danger_ok.stdout).lower()
    if "permission denied" in text:
        return fail(
            "Docker is running but this user may not use it",
            [
                "Add yourself to the docker group: sudo usermod -aG docker $USER",
                "Close the terminal, open a new one (or run: newgrp docker).",
                _RERUN,
            ],
            rl.DOCKER,
        )
    if ctx.platform.wsl:
        if _DOCKER_DESKTOP_EXE.exists():
            fix = [
                "Start Docker Desktop from the Windows Start menu and wait until "
                "it says 'Engine running'.",
                "In Docker Desktop: Settings > Resources > WSL integration > turn on "
                "your Ubuntu distribution, then Apply & restart.",
                _RERUN,
            ]
        else:
            fix = ["Start the Docker engine: sudo service docker start", _RERUN]
    elif ctx.platform.system == "Darwin":
        fix = [
            "Open Docker Desktop from Applications and wait for it to start.",
            _RERUN,
        ]
    else:
        fix = ["Start the Docker engine: sudo systemctl start docker", _RERUN]
    return fail("the Docker engine is not running", fix, rl.DOCKER)


def check_compose_file(run: DoctorRun) -> CheckResult:
    """docker-compose.yml is valid with the current settings."""
    ctx = run.ctx
    result = ctx.runner.run(
        compose_argv(ctx, "config", "--quiet"),
        cwd=ctx.settings.root,
        env=ctx.environ,
        timeout=30,
    )
    if result.is_ok and result.danger_ok.succeeded:
        return ok(
            f"docker-compose.yml is valid (project {ctx.settings.compose_project}, "
            f"database port {ctx.settings.db_port})"
        )
    text = result.danger_ok.stderr if result.is_ok else str(result.danger_err)
    if "POSTGRES_PASSWORD" in text:
        return fail(
            "POSTGRES_PASSWORD is not set, so the database cannot be created",
            [
                "Create .env if you have not: cp .env.example .env",
                "Set POSTGRES_PASSWORD in .env (and the same password inside "
                "HULLBREACH_DATABASE_URL).",
                _RERUN,
            ],
            rl.SETTINGS,
        )
    last = text.strip().splitlines()[-1:] or ["unknown error"]
    return fail(
        f"docker-compose.yml is not valid: {last[0]}",
        ["Undo local edits to it: git checkout docker-compose.yml", _RERUN],
        rl.TROUBLE_DB,
    )


TOOL_CHECKS = (
    Check("os", "Operating system", check_os),
    Check("git", "git installed", check_git),
    Check("repo", "Code is a clone and up to date", check_repo, ("git",)),
    Check("uv", "uv installed", check_uv),
    Check("python", "Python version", check_python, ("uv",)),
    Check("py-deps", "Python packages (uv sync)", check_py_deps, ("python",)),
    Check("node", "Node.js and npm", check_node),
    Check("web-deps", "Website packages (npm ci)", check_web_deps, ("node",)),
    Check("docker", "Docker installed", check_docker),
    Check("docker-daemon", "Docker engine running", check_docker_daemon, ("docker",)),
)
