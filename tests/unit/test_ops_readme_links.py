"""The README anchors the doctor prints must exist in README.md."""

from __future__ import annotations

import re
from pathlib import Path

from hullbreach_ops import readme_links as rl

README = Path(__file__).resolve().parents[2] / "README.md"


def test_github_slug_matches_githubs_rules() -> None:
    # frob:tests src/hullbreach_ops/readme_links.py::github_slug kind="unit"
    assert rl.github_slug("Step 1: Get the code and run the doctor") == (
        "step-1-get-the-code-and-run-the-doctor"
    )
    assert rl.github_slug("2d. Node.js") == "2d-nodejs"
    assert rl.github_slug("Step 3: Install the project's packages") == (
        "step-3-install-the-projects-packages"
    )
    assert rl.github_slug("Step 0: What a terminal is, and how to open one") == (
        "step-0-what-a-terminal-is-and-how-to-open-one"
    )


def test_every_readme_link_points_at_a_real_heading() -> None:
    # frob:tests src/hullbreach_ops/readme_links.py::ReadmeSection kind="unit"
    text = README.read_text(encoding="utf-8")
    headings = {
        rl.github_slug(m.group(1))
        for m in re.finditer(r"^#{1,6} +(.+?)\s*$", text, re.MULTILINE)
    }
    missing = [s.title for s in rl.ALL_SECTIONS if s.anchor not in headings]
    assert missing == []
    assert rl.DOCTOR.url.endswith("#step-1-get-the-code-and-run-the-doctor")
