# Contributing

This repository is private to Company of Theseus. These are the working
rules for the team.

## Branching

`main` is protected: it only moves by pull request, and the pull request
must be green. Nobody pushes to `main` directly, including the Scrum
Master. Branch protection is configured in the GitHub repository settings
(require a pull request and the `All checks pass` status check).

Branch from `main` for every piece of work, one concern per branch:

```
git switch main && git pull
git switch -c <type>/<short-description>      # feat/login-form, fix/elo-rounding
```

Rebase onto `main` before opening the PR so the merge is linear. Squash or
rebase merges only; no merge commits.

## What "green" means

The CI workflow runs three jobs on every pull request -- `server`
(ruff, ty, pytest), `web` (eslint, prettier, crunk, tsc, vitest, vite
build), and `frob check` -- and a final `All checks pass` job that fails
if any of them did not succeed. That last job is the single required
status check.

Within pytest, an `xfail` counts as a pass and a strict `xpass` counts as a
failure; use `@pytest.mark.xfail(strict=True, reason=...)` for a known,
tracked defect rather than skipping or deleting the test. There is no
equivalent escape hatch for lint, types, or the frob gates: fix them.

Run the same gate locally before pushing:

```
frob check
```

## Commits

Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`,
`refactor:`. Subject line under 72 characters, imperative mood. The body
explains why, not what -- the diff already says what.

## Layout

```
src/hullbreach_server/   FastAPI app (Python, uv, ruff, ty, pytest)
tests/                   unit/ per module, system/ for build smoke tests
web/                     React + Tailwind frontend (Vite, vitest, eslint)
docs/                    frob-linked documentation
frob.toml                the one config for the polyglot quality gate
```

The Python package sits at the repo root, and the web app under `web/`,
because frob treats one git root as one project and dispatches every
language stage it detects there (`pyproject.toml`, `package.json`). Keep
it that way rather than nesting a second `pyproject.toml` or
`package.json`.

## Tests

Every new module gets a unit test file of the same name under
`tests/unit/`. Anything that wires modules together gets a case in
`tests/system/test_build.py`, which is the "did I build?" smoke test and
must pass on a fresh `uv sync`. Annotate tests with `# frob:tests
<path>::<symbol> kind="unit"|"integration"` so the frob coverage gate can
map them.

## Styling

Never hand-edit `web/src/styles/tokens.css` or `web/tailwind.theme.json`;
change `crunk.toml` and run `uv run crunk tokens`. New CSS goes in the
matching `web/src/styles/<bucket>/` directory, and `className` strings
use only the namespaced token utilities -- `crunk check` fails the build
on a stock Tailwind color or spacing step.

## Secrets

Never commit `.env`. Add new settings to `.env.example` with a
placeholder value and to `AppConfig` with a safe default.
