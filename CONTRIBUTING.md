# Contributing

This repository is private to Company of Theseus. These are the working
rules for the team.

## Branching

`main` is protected: it only moves by pull request, and the pull request
must be green. Nobody pushes to `main` directly. Branch protection is
configured in the GitHub repository settings (Settings -> Rules ->
Rulesets) and requires one approving review plus all three CI status
checks -- `server (python)`, `web (typescript)`, `frob check` -- before
merge; the Scrum Master is on the ruleset's bypass list, for an urgent fix
when no reviewer is available, but does not push to `main` outside that
case.

Branch from `main` for every piece of work, one concern per branch:

```
git switch main && git pull
git switch -c <type>/<short-description>      # feat/login-form, fix/elo-rounding
```

Rebase onto `main` before opening the PR so the merge is linear. Merge by
merge commit, as practiced so far -- not squash or rebase, so a ticket's
full commit history stays intact on `main`.

## What "green" means

The CI workflow runs three jobs on every pull request -- `server`
(ruff, ty, pytest), `web` (eslint, prettier, crunk, tsc, vitest, vite
build), and `frob check` -- and branch protection requires all three by
name, so a PR cannot merge while any one of them is red or still running.

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
