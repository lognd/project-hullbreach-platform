"""doctor.sh on a machine with none of the tools: explains each, installs nothing.

The wrapper runs before Python exists, so it is tested as a real bash run
with a PATH that holds only the shell basics and a fake curl that records
whether any installer was started.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASICS = ("bash", "uname", "grep", "dirname", "cat", "sh")


@pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")
def test_wrapper_explains_missing_tools_and_never_installs_without_a_yes(
    tmp_path: Path,
) -> None:
    """No keyboard means no prompt, so no installer runs; uv missing stops the run."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in BASICS:
        found = shutil.which(name)
        assert found is not None
        (bin_dir / name).symlink_to(found)
    ran = tmp_path / "curl-ran"
    curl = bin_dir / "curl"
    curl.write_text(f"#!/bin/sh\ntouch {ran}\nexit 1\n", encoding="utf-8")
    curl.chmod(0o755)
    home = tmp_path / "home"
    home.mkdir()
    env = {"PATH": str(bin_dir), "HOME": str(home), "LANG": "C"}

    done = subprocess.run(
        [str(bin_dir / "bash"), str(ROOT / "doctor.sh")],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )

    out = done.stdout
    assert done.returncode == 1
    for tool in ("uv:", "git:", "Docker:", "Node.js:"):
        assert tool in out
    assert out.count("NOT FOUND") == 4
    assert "not asking: no keyboard attached" in out
    assert "Stopped: uv is needed" in out
    assert not ran.exists()
    assert out.isascii()
