"""README sections the doctor points at, with links that are tested to exist.

Every doctor failure names the README section that explains it. The anchors
are GitHub's heading slugs; tests/unit/test_ops_readme_links.py fails when a
heading is renamed without updating this table.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict

from hullbreach_ops.settings import REPO_URL


# noqa: E501  # frob:tests tests/unit/test_ops_readme_links.py::test_every_readme_link_points_at_a_real_heading
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class ReadmeSection(BaseModel):
    """One README heading: its title as shown and its GitHub anchor."""

    model_config = ConfigDict(frozen=True)

    title: str
    anchor: str

    @property
    def url(self) -> str:
        """Link to the section on GitHub."""
        return f"{REPO_URL}#{self.anchor}"

    def describe(self) -> str:
        """How the report names the section: title plus link."""
        return f"README '{self.title}': {self.url}"


def _section(title: str) -> ReadmeSection:
    """A section whose anchor is GitHub's slug of `title`."""
    return ReadmeSection(title=title, anchor=github_slug(title))


# frob:tests tests/unit/test_ops_readme_links.py::test_github_slug_matches_githubs_rules
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def github_slug(title: str) -> str:
    """GitHub's heading anchor: lowercase, punctuation dropped, spaces to dashes."""
    slug = title.strip().lower()
    slug = re.sub(r"[^\w\- ]", "", slug)
    return slug.replace(" ", "-")


TERMINAL = _section("Step 0: What a terminal is, and how to open one")
DOCTOR = _section("Step 1: Get the code and run the doctor")
TOOLS = _section("Step 2: Install the tools (one time)")
GIT = _section("2a. Git")
DOCKER = _section("2b. Docker")
UV = _section("2c. uv")
NODE = _section("2d. Node.js")
PACKAGES = _section("Step 3: Install the project's packages")
SETTINGS = _section("Step 4: Create your settings file")
START = _section("Step 5: Start everything")
BY_HAND = _section("Starting each part by hand")
TRY_IT = _section("Step 6: Try it")
GAME = _section("Connecting the game to the platform")
LAN = _section("Hosting a demo for other computers")
TROUBLE_INSTALL = _section("Installing and downloading")
TROUBLE_DB = _section("Database problems")
TROUBLE_API = _section("API problems")
TROUBLE_WEB = _section("Website problems")
TROUBLE_SIGNIN = _section("Signing in on the website")
TROUBLE_GAME = _section("Game cannot reach the platform")

ALL_SECTIONS = (
    TERMINAL,
    DOCTOR,
    TOOLS,
    GIT,
    DOCKER,
    UV,
    NODE,
    PACKAGES,
    SETTINGS,
    START,
    BY_HAND,
    TRY_IT,
    GAME,
    LAN,
    TROUBLE_INSTALL,
    TROUBLE_DB,
    TROUBLE_API,
    TROUBLE_WEB,
    TROUBLE_SIGNIN,
    TROUBLE_GAME,
)
