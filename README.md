# Project Hullbreach: Platform

This is the non-game half of Hullbreach: the REST API, the website, and the
Postgres database behind accounts, sessions, ELO, match history, and the
cosmetic store. The Unity game and its realtime server are in the other
repo and talk to this one over HTTPS.

Company of Theseus, UF CEN3031, Fall 2026. All rights reserved, see
[LICENSE](LICENSE).

I wrote this so you can go from a blank laptop to a merged PR without
pinging me every ten minutes. Skim the first two sections, then follow the
rest in order. If something breaks, look for the collapsed "if that broke"
bits. If those do not help, paste the command and the last 20 lines of
output in the team chat.

## What is here

- **API** (Python, FastAPI): registration, login, sessions, profiles, ELO,
  match history, the catalog and store, admin moderation. The website and
  the game client both log in against it; the game server posts match
  results to it.
- **Website** (TypeScript, React, Tailwind): landing page, cookie notice
  and data policy, register/login, profile, store.
- **Database** (Postgres): users with Player/Admin roles, sessions,
  matches, stats, ELO history, items, inventory. Runs in Docker locally.
  The API only knows a connection string, so pointing it at a hosted DB is
  a config change.

How it hangs together: the browser hits the vite dev server on 5173,
which proxies `/api` to uvicorn on 8000, which talks SQL to Postgres on 5432. The game client and game server hit the API directly.

Three tools sit on top and are not optional:

- **uv** installs Python and all Python packages into `.venv/` in the repo.
- **frob** is the quality gate. One command runs every linter, type
  checker, and test for both languages. CI runs the same thing and a PR
  cannot merge until it is green.
- **crunk** lints the website design system. Colors, spacing, and type
  scales are declared once in `crunk.toml` and every stylesheet and
  `className` is checked against them.

frob and crunk are mine (they are on PyPI). If either does something weird,
that is on me, tell me.

## Where things live

```
src/hullbreach_server/   the FastAPI app
  __main__.py            entry point: flags, .env, runs the server
  app/                   AppConfig (pyproject -> env -> CLI), create_app, App
  api/                   one file per resource, mounted at /api/v1
  logging/               logging setup
tests/
  unit/                  one file per module
  system/test_build.py   "did I build?" smoke test
web/
  index.html             vite entry
  src/main.tsx           mounts web/src/App.tsx
  src/index.css          stylesheet entry: tokens, reset, Tailwind
  src/styles/            crunk-organized CSS (tokens.css is GENERATED)
  tailwind.config.ts     hands crunk's generated theme to Tailwind
  tests/unit/            vitest
crunk.toml               the design system
frob.toml                the quality gate config
pyproject.toml           Python deps + settings defaults
uv.lock                  pinned Python versions (do not edit)
package.json             JS deps + scripts
package-lock.json        pinned JS versions (do not edit)
docker-compose.yml       local Postgres
docs/index.md            frob-linked docs for the public API
.github/workflows/ci.yml what runs on every PR
```

Python sits at the repo root and the web app under `web/` because frob
treats one git root as one project. Do not add a second `pyproject.toml`
or `package.json`; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Setup (once)

Everything below is typed into a terminal. On Windows that means the
Ubuntu window from WSL, not PowerShell. On a Mac it is Terminal. Commands
in grey boxes get pasted in and run with Enter. A command that prints
nothing usually worked.

### WSL (Windows only)

PowerShell as admin, `wsl --install`, restart, pick a username and
password in the Ubuntu window that pops up. From here on every command
goes in that window. Keep the repo under your Linux home
(`~/projects/...`), not `/mnt/c/...`, it is painfully slow there. If WSL
refuses to install, ask me.

### Git

- Ubuntu/WSL: `sudo apt update && sudo apt install -y git`
- macOS: run `git --version` and accept the developer tools prompt.

```
git config --global user.name "Your Name"
git config --global user.email "you@ufl.edu"
git config --global init.defaultBranch main
git config --global pull.rebase true
```

### uv

uv is the only Python thing you install by hand. It fetches the right
Python itself, so do not install Python separately and do not use `pip`
or `python -m venv` in this repo.

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal, then `uv --version`.

<details>
<summary>if that broke: "uv: command not found"</summary>

The installer put `uv` in `~/.local/bin` and your shell does not look
there. Run `export PATH="$HOME/.local/bin:$PATH"` and try again. If that
works, add that line to the end of `~/.bashrc` (or `~/.zshrc` on a Mac)
and open a new terminal. Same fix applies to `frob` later.

</details>

### Node 22

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

New terminal, then:

```
nvm install 22
nvm alias default 22
```

`node --version` should start with `v22`. If `nvm` is not found in a new
terminal, `source ~/.nvm/nvm.sh` and add that to your `~/.bashrc`. If you
already have Node from somewhere else, 20+ is fine.

### Docker Desktop

Grab it from https://www.docker.com/ and open it once. On Windows keep
"Use WSL 2" checked during install, then Settings -> Resources -> WSL
integration -> turn on Ubuntu -> Apply, and reopen your Ubuntu terminal.
`docker compose version` should work in your normal terminal.

Docker Desktop has to be running whenever you want the database. If you
cannot install Docker at all (school laptop, no admin), you can still do
everything except run the DB locally; tell me and I will give you the
shared database string.

### frob

```
uv tool install frob
```

`frob --version` to check. `uv tool install` puts a program on your PATH
in its own little environment, separate from any project, which is what
you want for a tool you run on projects. crunk is different: it is a dev
dependency of this repo, so it lives in `.venv` and runs as `uv run crunk`.

### Editor

Whatever you like. If you have nothing, VS Code from
https://code.visualstudio.com/. On Windows also install its "WSL"
extension so it can open folders inside Ubuntu (`code .` from the Ubuntu
terminal). Useful extensions: Python, Ruff, ESLint, Prettier, Tailwind
CSS IntelliSense.

## Environments, briefly

Every project needs its own set of packages at its own versions, so each
project gets a folder holding its own Python and packages and nothing
else. Ours is `.venv/` at the repo root. `uv sync` builds it from
`pyproject.toml` (what we want) and `uv.lock` (exact versions, so you, me,
and CI get byte-for-byte the same thing). It is gitignored, about 200 MB,
and safe to delete and rebuild. Nothing you wrote lives in it.

You do not activate it. Put `uv run` in front of Python things:

```
uv run hullbreach_server        # the API
uv run pytest                   # the tests
uv run crunk check              # crunk
```

Adding a Python package is `uv add requests` (or `uv add --dev x` for
tooling), never `pip install`. That edits `pyproject.toml` and `uv.lock`;
commit both. When someone else pulls it, their next `uv sync` picks it
up. `ModuleNotFoundError` after a pull almost always means "run
`uv sync`".

The JS side is the same idea with different names: `package.json`,
`package-lock.json`, `node_modules/`, and `npm ci` to install from the
lock. Add packages with `npm install some-package` (or `-D`) and commit
both files. `npm ci` refuses to change the lock, which is what you want
when you are not adding anything.

## Get the code and install

You need to be a collaborator on the repo. Send me your GitHub username if
you have not been added.

```
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/lognd/project-hullbreach-platform.git platform
cd platform
uv sync
npm ci
```

Git will ask for a username and password. Your GitHub password will not
work; you need a personal access token: GitHub -> your avatar -> Settings
-> Developer settings -> Personal access tokens -> Tokens (classic) ->
Generate new token, tick `repo`, copy it, paste it as the password. Run
`git config --global credential.helper store` so you only do that once.

`uv run hullbreach_server --help` should print usage text.

<details>
<summary>if that broke: clone and install problems</summary>

- "Repository not found": typo, or you are not a collaborator yet.
- "Authentication failed": you used your password, or the token lacks
  `repo`. Make a new one.
- "No such file or directory: pyproject.toml": wrong folder,
  `cd ~/projects/platform`.
- `npm ci` dies with "Cannot read properties of null (reading
  'edgesOut')": your npm is too old for vitest 4. `npm install -g npm@latest`.
- Network / proxy / ETIMEDOUT: UF guest wifi blocks package downloads
  sometimes. Use eduroam or a hotspot.

</details>

## Run it

Settings come from `.env`, which is gitignored because it can hold
passwords. Make yours from the template; the defaults are right for local
dev:

```
cp .env.example .env
```

Every setting has a default in `pyproject.toml` under
`[tool.hullbreach_server]`; `.env` overrides that, and CLI flags override
`.env`. If you are on the shared database, set `HULLBREACH_DATABASE_URL=`
in `.env` to the string I gave you.

Database, API, website, each in its own terminal:

```
docker compose up -d db          # first run downloads Postgres; rerun after reboots
uv run hullbreach_server         # http://127.0.0.1:8000/api/docs
npm run dev                      # http://localhost:5173
```

`docker compose ps` should show `db` as `running (healthy)`. The API docs
page has a `/api/v1/health` entry; "Try it out" -> "Execute" should give
you `{"status": "ok", ...}`. The website is a dark page saying "Project
Hullbreach"; edit `web/src/App.tsx` and it live-reloads. The site proxies
`/api` to port 8000, so the API has to be up for anything that loads data.

`Ctrl+C` stops any of them. `docker compose down` stops the DB and keeps
data; `down -v` wipes it.

<details>
<summary>if that broke: runtime problems</summary>

- "Cannot connect to the Docker daemon": Docker Desktop is not running.
- "port is already allocated" on 5432: another Postgres is on your
  machine. Stop it, or change `"5432:5432"` to `"5433:5432"` in
  `docker-compose.yml` and match the port in your `.env`.
- `unhealthy`: `docker compose logs db`, read the tail, paste it in chat.
- "Address already in use" on 8000: an old API is still running. Kill
  it, or `uv run hullbreach_server --port 8001`.
- "This site can't be reached": use exactly `127.0.0.1:8000`, not
  `localhost`.
- "vite: not found": `npm ci` did not finish.
- Blank page: F12 -> Console, read the red text. The `npm run dev`
  terminal has the same error with a line number.
- A Tailwind class does nothing: we do not use stock Tailwind colors and
  sizes. See Styling below.

</details>

## Checks

Before pushing, run what CI runs, from the repo root:

```
frob check
uv run crunk check
uv run crunk tokens --check
```

`frob check` covers ruff, ty, pytest, tsc, eslint, prettier, vitest, and
frob's own structural gates. The last line is `[OK]` or `[FAIL]` with a
count, and the `## Errors` block above it says what to fix. Most
formatting noise goes away with `frob format` and
`npx prettier --write .`.

Things frob says that look scary and are not:

- "no coverage stamp found": `frob coverage --full --fail-on-degraded`,
  then `frob check` again. Happens on a fresh clone.
- "PRE001 / SCOPE001 ... no active ticket is derivable": you have
  uncommitted changes on a branch frob cannot tie to a ticket. It clears
  once you are on a `T-####-name` branch or pass `--ticket`. See
  [CONTRIBUTING.md](CONTRIBUTING.md).
- A test you did not touch fails: pull `main` and rerun. If it still
  fails somebody broke it; say so in chat instead of working around it.

## Making a change

`main` is protected. Nobody pushes to it, me included. Every change is a
branch, then a PR, green CI (all three checks -- `server (python)`,
`web (typescript)`, `frob check`), one approval, merge. Every time. The
Scrum Master is on the branch ruleset's bypass list, for an urgent fix
when nobody is around to review, but does not push to `main` outside
that case.

```
git switch main && git pull
git switch -c feat/login-form         # feat/ fix/ docs/ chore/
# ...do the work, add a test, frob check until green...
git add -A
git commit -m "feat: add login form with client-side validation"
git push -u origin feat/login-form
```

Commit messages are [Conventional Commits](https://www.conventionalcommits.org/):
type, colon, short imperative sentence. Git prints a link to open the PR;
fill in the template, wait for all three checks to go green, ask someone
in chat for a review, address comments by pushing more commits, then
"Merge pull request" (a merge commit, not squash or rebase) and delete
the branch. Back home: `git switch main && git pull`.

<details>
<summary>if that broke: git and PR problems</summary>

- "Your branch is behind" / conflicts: `main` moved.
  `git switch main && git pull && git switch feat/x && git rebase main`.
  On CONFLICT open the files it names, fix the `<<<<<<<` blocks,
  `git add -A && git rebase --continue`. Lost? `git rebase --abort` and
  ask.
- Push rejected because the remote has work you do not: rebase as above,
  then `git push --force-with-lease`.
- "Permission denied": not a collaborator, or your token expired.
- You committed to `main` by accident: it cannot be pushed, so no harm.
  `git switch -c feat/whatever` takes the commit with you, then
  `git switch main && git reset --hard origin/main`.
- CI red but green locally: "Details" on the failing job, read the last
  30 lines. Usually a file you forgot to `git add`.
- A check stuck yellow for 10+ minutes: GitHub being slow.

</details>

### Tests

Every new Python module gets `tests/unit/test_<name>.py`. Anything that
wires modules together gets a case in `tests/system/test_build.py`, the
smoke test that has to pass on a fresh `uv sync`. Each test carries a
`# frob:tests src/hullbreach_server/<file>.py::<symbol> kind="unit"`
comment so frob can map it; copy an existing one. Website components get
`web/tests/unit/<Name>.test.tsx`.

A test for a known, tracked bug is marked
`@pytest.mark.xfail(strict=True, reason="...")`; CI counts xfail as a
pass. Do not delete or skip a failing test to get green.

### Styling

The design system lives in `crunk.toml`. `uv run crunk tokens` generates
`web/src/styles/tokens.css` and `web/tailwind.theme.json` from it; never
edit those by hand. Utilities use our names, not Tailwind's: `bg-paper`,
`text-ink`, `text-muted`, `bg-accent`, `gap-space-8`, `p-space-16`,
`text-font-size-20`, `rounded-radius-8`, `font-base`. A stock
`bg-zinc-900` or `gap-2` does nothing and fails `crunk check`. Need a new
color or size? Add it to `crunk.toml`, run `uv run crunk tokens`, commit
all three files. Hand-written CSS goes in `web/src/styles/<bucket>/`.

## Cheat sheet

```bash
docker compose up -d db          # database (after every reboot)
uv run hullbreach_server         # API      http://127.0.0.1:8000/api/docs
npm run dev                      # website  http://localhost:5173

frob check                       # the full gate
frob format                      # fix Python formatting + frob directives
frob test                        # tests for what you touched (or --all)
frob coverage --full             # refresh the coverage stamp
uv run pytest                    # just Python tests
npm run test                     # just website tests
uv run crunk check               # design-system lint
uv run crunk tokens              # regenerate tokens after editing crunk.toml
uv run crunk check --contrast    # contrast report

uv sync && npm ci                # after pulling dependency changes
make install                     # same thing, stamp-guarded
make clean                       # delete build output and caches
```

## When it all goes wrong

1. Read the last 20 lines of the error. The useful part is at the bottom.
2. `pwd` should end in `/platform`.
3. New terminal, try again (PATH stuff).
4. Docker Desktop running?
5. `uv sync && npm ci`.
6. Nuke it, nothing in these folders is yours:
   `rm -rf .venv node_modules dist && uv sync && npm ci`
7. Paste the command and output in chat.

<details>
<summary>errors we have hit before</summary>

- `ModuleNotFoundError: No module named 'hullbreach_server'`: stale
  `.venv`, often after moving the folder. Step 6.
- `pytest: error: unrecognized arguments: -n`: same, step 6.
- `error TS2307: Cannot find module '@/App'`: stale `node_modules`, step 6.
- `TW004 ... resolves to Tailwind's default color`: stock Tailwind color.
  See Styling.
- `ORG005 ... is a CSS file outside web/src/styles`: new CSS goes in
  `web/src/styles/<bucket>/`.
- `REF001 ... has no inbound references`: frob found a file nothing
  points at. Import it, or for config files add a `[[refs.entrypoint]]`
  entry in `frob.toml` like the existing ones.
- `^M` in diffs and prettier mad at every line: Windows line endings.
  `git config --global core.autocrlf input` and re-clone.
- VS Code red squiggles but `frob check` green: VS Code picked the wrong
  Python. `Ctrl+Shift+P` -> "Python: Select Interpreter" -> the one in
  `.venv`.

</details>

[CONTRIBUTING.md](CONTRIBUTING.md) has the branch and ticket rules,
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) the expectations, and
[SECURITY.md](SECURITY.md) how to report a vulnerability.
