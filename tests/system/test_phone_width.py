"""System test: the signed-in profile page fits a 390px phone in a real browser (S09).

Needs a running stack and Chromium via playwright-core, so it is opt-in: set
E2E_URL, E2E_USER, E2E_PASSWORD and PLAYWRIGHT_CORE (e.g. after `make demo`,
with the demo account) and it measures the page; otherwise it skips.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parent / "phone_width.mjs"
_NEEDED = ("E2E_URL", "E2E_USER", "E2E_PASSWORD", "PLAYWRIGHT_CORE")
_PHONE_WIDTH = 390


# frob:ticket 01M2H5T10YFV60H1CQDEEH5164
def test_profile_page_fits_a_phone_width_screen_in_a_real_browser() -> None:
    """Given a 390px viewport, when /me renders signed in, then nothing scrolls sideways."""
    missing = [name for name in _NEEDED if not os.environ.get(name)]
    if missing:
        pytest.skip(f"real-browser run needs {', '.join(missing)}")

    done = subprocess.run(  # noqa: S603
        ["node", str(_SCRIPT)],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
        timeout=90,
    )
    measured = json.loads(done.stdout.strip().splitlines()[-1])

    assert measured["viewport"] == _PHONE_WIDTH
    assert measured["scrollWidth"] <= _PHONE_WIDTH
    assert measured["offenders"] == []
