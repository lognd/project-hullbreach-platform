"""Unit tests for the doctor's tool checks (fake commands, fake checkout)."""

from __future__ import annotations

import json
from pathlib import Path

from ops_fakes import FakeRunner, make_ctx, ok

from hullbreach_ops import checks_tools as ct
from hullbreach_ops import readme_links as rl
from hullbreach_ops.checkbase import DoctorRun, Status
from hullbreach_ops.settings import PlatformInfo


def _run(tmp_path: Path, runner: FakeRunner, **kw: object) -> DoctorRun:
    return DoctorRun(ctx=make_ctx(tmp_path, runner=runner, **kw))  # type: ignore[arg-type]


def test_satisfies_engines_handles_caret_and_ranges() -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::satisfies kind="unit"
    spec = "^20.19.0 || >=22.12.0"
    assert ct.satisfies((20, 19, 1), spec)
    assert not ct.satisfies((20, 18, 0), spec)
    assert not ct.satisfies((21, 0, 0), spec)
    assert ct.satisfies((22, 12), spec)
    assert ct.satisfies((24, 1, 0), spec)
    assert not ct.satisfies((22, 11, 9), spec)
    assert ct.satisfies((3, 12, 1), ">=3.11")
    assert not ct.satisfies((3, 10, 0), ">=3.11")
    assert not ct.satisfies((1, 0, 0), "latest")


def test_os_check_refuses_windows_and_wsl1(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_os kind="unit"
    native = PlatformInfo(system="Windows", release="10")
    result = ct.check_os(_run(tmp_path, FakeRunner(), platform=native))
    assert result.status == Status.FAIL
    assert "doctor.cmd" in result.fix[0]
    wsl1 = PlatformInfo(
        system="Linux", release="4.4-Microsoft", wsl=True, wsl_version=1
    )
    assert "WSL 1" in ct.check_os(_run(tmp_path, FakeRunner(), platform=wsl1)).summary
    assert ct.check_os(_run(tmp_path, FakeRunner())).status == Status.PASS


def test_missing_tools_fail_with_the_wrapper_as_the_fix(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_git kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_uv kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_node kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_docker kind="unit"
    run = _run(tmp_path, FakeRunner(programs=set()))
    for check, section in (
        (ct.check_git, rl.GIT),
        (ct.check_uv, rl.UV),
        (ct.check_node, rl.NODE),
        (ct.check_docker, rl.DOCKER),
    ):
        result = check(run)
        assert result.status == Status.FAIL
        assert result.readme == section
        assert "./doctor.sh" in result.fix[0]


def test_node_version_must_match_package_json(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_node kind="unit"
    runner = FakeRunner(replies={("node", "--version"): ok("v18.19.0\n")})
    run = _run(tmp_path, runner)
    (run.ctx.settings.root / "package.json").write_text(
        json.dumps({"engines": {"node": "^20.19.0 || >=22.12.0"}})
    )
    result = ct.check_node(run)
    assert result.status == Status.FAIL
    assert "v18.19.0 is not supported" in result.summary
    assert "nvm install" in result.fix[0]
    runner.replies[("node", "--version")] = ok("v22.12.0\n")
    assert ct.check_node(run).status == Status.PASS


def test_docker_daemon_permission_denied_and_stopped(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_docker_daemon kind="unit"
    info = ("docker", "info")
    denied = FakeRunner(
        replies={
            info: ok(stderr="permission denied while trying to connect", returncode=1)
        }
    )
    result = ct.check_docker_daemon(_run(tmp_path, denied))
    assert result.summary == "Docker is running but this user may not use it"
    assert "usermod -aG docker" in result.fix[0]

    stopped = FakeRunner(replies={info: ok(stderr="Cannot connect", returncode=1)})
    linux = ct.check_docker_daemon(_run(tmp_path, stopped))
    assert linux.summary == "the Docker engine is not running"
    assert "systemctl start docker" in linux.fix[0]
    mac = PlatformInfo(system="Darwin", release="24")
    assert (
        "Docker Desktop"
        in ct.check_docker_daemon(_run(tmp_path, stopped, platform=mac)).fix[0]
    )

    running = FakeRunner(replies={info: ok("27.3.1\n")})
    assert ct.check_docker_daemon(_run(tmp_path, running)).status == Status.PASS


def test_repo_check_warns_when_behind(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_repo kind="unit"
    runner = FakeRunner()
    run = _run(tmp_path, runner)
    git = ("git", "-C", str(run.ctx.settings.root))
    runner.replies.update(
        {
            (*git, "rev-parse", "--is-inside-work-tree"): ok("true\n"),
            (*git, "remote"): ok(
                "https://github.com/lognd/project-hullbreach-platform.git\n"
            ),
            (*git, "rev-parse", "--abbrev-ref"): ok("main\n"),
            (*git, "rev-list"): ok("0\t3\n"),
        }
    )
    result = ct.check_repo(run)
    assert result.status == Status.WARN
    assert result.summary == "branch main is 3 commit(s) behind origin/main"
    assert result.fix[0] == "Get the latest code: git pull"
    runner.replies[(*git, "rev-list")] = ok("0\t0\n")
    assert ct.check_repo(run).status == Status.PASS
    runner.replies[(*git, "rev-parse", "--is-inside-work-tree")] = ok(returncode=128)
    assert "not a git clone" in ct.check_repo(run).summary


def test_package_and_compose_checks_name_the_command_to_run(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/checks_tools.py::check_py_deps kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_web_deps kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_compose_file kind="unit"
    # frob:tests src/hullbreach_ops/checks_tools.py::check_python kind="unit"
    runner = FakeRunner(
        replies={
            ("uv", "sync"): ok(returncode=1),
            ("docker", "compose", "-p", "platform", "config"): ok(
                stderr="required variable POSTGRES_PASSWORD is missing a value",
                returncode=1,
            ),
        }
    )
    run = _run(tmp_path, runner)
    assert ct.check_python(run).status == Status.PASS
    assert ct.check_py_deps(run).fix[0] == "Run: uv sync"
    web = ct.check_web_deps(run)
    assert web.summary == "the website's packages are not installed"
    assert web.fix[0] == "Run: npm ci"
    compose = ct.check_compose_file(run)
    assert compose.summary.startswith("POSTGRES_PASSWORD is not set")
    assert compose.readme == rl.SETTINGS
