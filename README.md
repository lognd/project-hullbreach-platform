# Project Hullbreach: Platform

The non-game half of Project Hullbreach: the REST API, the web frontend,
and the PostgreSQL database behind accounts, login sessions, ELO, match
history, and the cosmetic store. The game client and the authoritative
game server live in the separate game repository and talk to this one
over HTTPS.

Built by Company of Theseus for the University of Florida's Introduction
to Software Engineering (CEN3031), fall 2026. All rights reserved -- see
[LICENSE](LICENSE).

## How this README works

It is written so that a teammate who has never set up a software project
can go from a blank laptop to a running site, and then to a first merged
change, by following it top to bottom. Do not skip steps; each one
assumes the ones before it. When something goes wrong, look for the
**"If that didn't work"** boxes and click them to expand.

Sections 1 through 3 explain what the pieces are and how they fit. The
hands-on part starts at section 4.

## Contents

1. [What this repository is](#1-what-this-repository-is)
2. [How the pieces fit together](#2-how-the-pieces-fit-together)
3. [Where things live](#3-where-things-live)
4. [The terminal](#4-the-terminal)
5. [Set up your computer (once)](#5-set-up-your-computer-once)
6. [How environments work](#6-how-environments-work)
7. [Get the code](#7-get-the-code)
8. [Install the project's dependencies](#8-install-the-projects-dependencies)
9. [Local settings](#9-local-settings)
10. [Start the database](#10-start-the-database)
11. [Run the API](#11-run-the-api)
12. [Run the website](#12-run-the-website)
13. [Run the checks](#13-run-the-checks)
14. [Make a change the right way](#14-make-a-change-the-right-way)
15. [Everyday commands](#15-everyday-commands)
16. [When things break](#16-when-things-break)
17. [Glossary](#17-glossary)

## 1. What this repository is

Project Hullbreach is a 2D PvP game where players build a spaceship out
of blocks and try to breach each other's hull. The game itself (Unity)
and its real-time server live in the game repository. This repository is
everything around the game that is not time-critical:

- **The API** (Python, FastAPI). Registration, login, sessions, profiles,
  ELO, match history, the item catalog and cosmetic store, and admin
  moderation. The website and the game client both authenticate against
  it; the game server reports match results to it.
- **The website** (TypeScript, React, Tailwind). Landing page, cookie
  notice and data policy, registration and login, the profile page, and
  the store.
- **The database** (PostgreSQL). Users with Player and Administrator
  roles, sessions, matches, per-player stats, ELO history, items, and
  inventory. Locally it runs in Docker; the API only ever sees a
  connection string, so pointing it at a hosted database is a settings
  change, not a code change.

## 2. How the pieces fit together

```
browser ──HTTP──▶ website (vite, :5173) ──/api──▶ API (uvicorn, :8000) ──SQL──▶ PostgreSQL (docker, :5432)
game client ─────────────────────────HTTPS───────▶ API
game server ─────────────────────────HTTPS───────▶ API   (match results, ELO)
```

In development all four run on your own computer. The website's dev
server forwards anything under `/api` to the API, so the browser only
ever talks to one address.

Three tools sit on top of the code and are part of the project, not
optional extras:

- **uv** installs Python and every Python package, into a private folder
  inside the project.
- **frob** is the quality gate: one command that runs every linter, type
  checker, and test for both languages. CI runs the same command, and a
  pull request cannot be merged until it passes.
- **crunk** is the design-system linter for the website: colors, spacing
  and type scales are declared once in `crunk.toml`, and every stylesheet
  and `className` is checked against them.

## 3. Where things live

```
src/hullbreach_server/   the FastAPI application (Python)
  __main__.py            entry point: flags, .env, runs the server
  app/                   AppConfig (pyproject -> env -> CLI), create_app, App
  api/                   one file per resource, mounted at /api/v1
  logging/               house logging convention
tests/
  unit/                  one file per module
  system/test_build.py   the "did I build?" smoke test
web/
  index.html             vite entry
  src/main.tsx           mounts web/src/App.tsx, the root React component
  src/index.css          stylesheet entry: tokens, reset, Tailwind
  src/styles/            crunk-organized CSS (tokens.css is GENERATED)
  tailwind.config.ts     hands crunk's generated theme to Tailwind
  tests/unit/            vitest
crunk.toml               the design system: palette, scales, organization
frob.toml                the quality gate for both languages
pyproject.toml           Python project: dependencies + settings defaults
uv.lock                  exact Python package versions (do not edit)
package.json             JavaScript project: dependencies + scripts
package-lock.json        exact JavaScript package versions (do not edit)
docker-compose.yml       local PostgreSQL
docs/index.md            frob-linked documentation for the public API
.github/workflows/ci.yml what runs on every pull request
```

The Python package sits at the repo root and the web app under `web/`
because frob treats one git root as one project and runs every language
stage it detects there. See [CONTRIBUTING.md](CONTRIBUTING.md) before
adding a second `pyproject.toml` or `package.json`.

## 4. The terminal

Everything below happens in a **terminal**: a window where you type a
command, press Enter, and read what comes back. You will copy commands
from this page into it.

**Open a terminal:**

- **Windows:** we use **WSL** (Windows Subsystem for Linux), a real
  Linux terminal inside Windows. Section 5a installs it. Once it is
  installed, press the Windows key, type `Ubuntu`, press Enter. Do
  _not_ use PowerShell or Command Prompt for this project.
- **macOS:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** you already know.

**Things to know:**

- The terminal is always "inside" one folder. `pwd` prints which one.
  `cd some-folder` moves into a folder; `cd ..` moves up one; `ls` lists
  what is here. `~` means your home folder.
- Commands in this README are in grey boxes. Copy the whole line, paste
  it (right-click, or `Ctrl+Shift+V` on Windows/Linux, `Cmd+V` on Mac),
  press Enter. Pasting does not run it; Enter does.
- A command that prints nothing usually worked. Errors are loud.
- If the terminal seems stuck, it is probably still working. Wait. If
  it is really stuck, `Ctrl + C` stops the current command.
- `sudo` in front of a command means "as administrator" and asks for
  your computer password. The password does not show as you type.

<details>
<summary><strong>If that didn't work:</strong> "I pasted a command and nothing happened"</summary>

Press Enter.

If you see a `>` on its own line, the terminal thinks you opened a quote
or bracket and never closed it. Press `Ctrl + C` and paste the command
again, making sure you copied the entire line.
</details>

## 5. Set up your computer (once)

Six installs, in this order. After each, run the "check" command; it
should print a version number, not an error.

### 5a. WSL (Windows only)

Open **PowerShell as Administrator** (Windows key, type `PowerShell`,
right-click it, "Run as administrator") and run:

```
wsl --install
```

Restart when it asks. On the next boot an Ubuntu window opens and asks
for a username and password. Pick short ones with no spaces; the
password does not show as you type. From now on **every command in this
README goes in that Ubuntu window**, not PowerShell.

<details>
<summary><strong>If that didn't work:</strong> WSL problems</summary>

- **"WSL 2 requires an update to its kernel component"**: follow the
  link it prints, install the update, run `wsl --install` again.
- **No Ubuntu window after restart**: Windows key, type `Ubuntu`, open
  it. If it is not there, open the Microsoft Store, search "Ubuntu",
  install, open.
- **"Virtualization is not enabled"**: this is a one-time setting in
  your computer's BIOS/UEFI (a key like `F2` or `Del` while booting;
  look for "Intel VT-x", "AMD-V", or "SVM"). Ask Logan if unsure.
- **Where to put files**: inside Ubuntu, keep the project under your
  Linux home (`~/projects/...`), _not_ under `/mnt/c/...`. The Windows
  drive is very slow from WSL and some tools misbehave there.
- **Opening the Windows side from Ubuntu**: `explorer.exe .` opens the
  current Ubuntu folder in Windows Explorer, if you ever need to drag a
  file in.

</details>

### 5b. Git

Git tracks every change to the code and is how we share work through
GitHub.

- **WSL / Ubuntu:** `sudo apt update && sudo apt install -y git`
- **macOS:** run `git --version`; if it offers to install "command line
  developer tools", click Install and wait.

Then tell Git who you are (same email as your GitHub account):

```
git config --global user.name "Your Name"
git config --global user.email "you@ufl.edu"
git config --global init.defaultBranch main
git config --global pull.rebase true
```

Check: `git --version`

### 5c. uv (Python and Python packages)

uv is the only Python tool you install by hand. It downloads the right
Python version for this project by itself, so **do not install Python
separately**, and do not use `pip` or `python -m venv` in this repo.
Section 6 explains what it is doing.

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close the terminal and open a new one so the `uv` command is found.

Check: `uv --version`

<details>
<summary><strong>If that didn't work:</strong> "uv: command not found"</summary>

Either you did not open a new terminal, or the installer put `uv` in a
folder your terminal does not search (`~/.local/bin`). Run:

```
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

If that prints a version, make it permanent: open `~/.bashrc` (Ubuntu,
WSL, most Linux) or `~/.zshrc` (macOS) with `nano ~/.bashrc`, scroll to
the end with the arrow keys, add the line
`export PATH="$HOME/.local/bin:$PATH"`, then `Ctrl+O`, Enter, `Ctrl+X`.
Open a new terminal. The same fix applies to `frob` in 5f.

What PATH is: the list of folders the terminal searches when you type a
command name. A tool that installs to a folder not on that list exists
but cannot be found by name.
</details>

### 5d. Node.js 22 (the website tooling)

Install **nvm** (Node Version Manager), then use it to install Node:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

Close the terminal, open a new one, then:

```
nvm install 22
nvm alias default 22
```

Check: `node --version` (starts with `v22`) and `npm --version`.

<details>
<summary><strong>If that didn't work:</strong> Node problems</summary>

- **"nvm: command not found"** in a new terminal: run
  `source ~/.nvm/nvm.sh` and try again. If that works, add
  `source ~/.nvm/nvm.sh` to the end of `~/.bashrc` / `~/.zshrc` (see
  the uv box for how).
- **`node --version` is not 22**: `nvm use 22`, and make sure you ran
  `nvm alias default 22`.
- **You already have Node from somewhere else**: 20 or newer is fine.

</details>

### 5e. Docker Desktop (the database)

Download Docker Desktop from https://www.docker.com/ and install it.
Open it once so it finishes setting up.

- **Windows:** during setup keep "Use WSL 2" checked. After it opens,
  Settings → Resources → WSL integration → turn on the switch for
  Ubuntu → Apply. Close and reopen your Ubuntu terminal.
- **macOS:** drag to Applications, open, accept the prompts.

Check (in your normal terminal): `docker --version` and
`docker compose version`.

<details>
<summary><strong>If that didn't work:</strong> Docker problems</summary>

- **"docker: command not found" in WSL**: Docker Desktop is not
  integrated with Ubuntu. Settings → Resources → WSL integration →
  Ubuntu on → Apply. New Ubuntu terminal.
- **"Cannot connect to the Docker daemon"**: Docker Desktop is not
  running. Open it and wait for the whale icon to stop animating. It
  has to be running every time you want the database.
- **"permission denied ... docker.sock"** (Linux): run
  `sudo usermod -aG docker $USER`, log out and back in.
- **You cannot install Docker at all** (school laptop, no admin
  rights): you can still do everything except run the database
  locally. Tell Logan; there is a shared database to point at instead
  (section 9).

</details>

### 5f. frob (the quality gate)

```
uv tool install frob
```

Check: `frob --version`

`uv tool install` puts a command-line program on your PATH in its own
isolated environment, separate from any project. That is different from
`uv sync`, which installs a project's own packages into that project's
folder (section 6). frob is a tool you run _on_ projects, so it is
installed this way. If `frob` is "not found", the uv box in 5c has the
PATH fix.

### 5g. An editor

Any editor works. If you do not have one, install **Visual Studio
Code** from https://code.visualstudio.com/. On Windows, also install its
"WSL" extension (Extensions panel → search "WSL" → Install) so it can
open folders that live inside Ubuntu. From the Ubuntu terminal, `code .`
opens the current folder. Recommended extensions once you have the
project open: "Python" (Microsoft), "Ruff", "ESLint", "Prettier", and
"Tailwind CSS IntelliSense".

## 6. How environments work

Read this once. It is the thing most likely to confuse you later.

**The problem.** This project needs Python 3.11 or newer plus a
specific set of packages at specific versions (FastAPI, pydantic, and so
on). Another project on your computer might need different versions of
the same packages. If everything was installed globally, they would
fight, and "it works on my machine" would be a daily event.

**The solution: one environment per project.** An environment is a
folder that holds a copy of Python and exactly the packages one project
needs, and nothing else. This project's environment is the `.venv`
folder at the repo root. It is created by `uv sync`, it is ignored by
Git, it is about 200 MB, and you can delete it and recreate it any time.
Nothing you wrote lives in it.

**What `uv sync` does, step by step:**

1. Reads `pyproject.toml` to learn which Python version and which
   packages the project wants.
2. Reads `uv.lock`, which pins every package (including packages our
   packages depend on) to an exact version. This is why every teammate
   and CI get byte-for-byte the same set.
3. Downloads that Python version if you do not have it, into
   `~/.local/share/uv/python/`. You never touch that folder.
4. Creates `.venv/` and installs everything from the lock file into it.
5. Installs _our own_ package (`hullbreach_server`) into `.venv` in
   "editable" mode, meaning the environment points at `src/` rather than
   copying it, so edits take effect immediately.

**How you use the environment.** You do not "activate" it. Put `uv run`
in front of any Python command and uv runs it inside `.venv`:

```
uv run hullbreach_server        # the API
uv run pytest                   # the tests
uv run python                   # an interactive Python with our packages
uv run crunk check              # crunk, which is a Python package we depend on
```

If you have seen `source .venv/bin/activate` in tutorials, that also
works here, but `uv run` never forgets and never uses the wrong
environment, so the README uses it everywhere.

**Adding a package.** Do not use `pip install`. Run:

```
uv add requests             # a runtime dependency
uv add --dev some-linter    # a development-only dependency
```

That edits `pyproject.toml`, updates `uv.lock`, and installs it. Commit
both files. When a teammate pulls your change, their next `uv sync`
installs it for them; if they forget, they get `ModuleNotFoundError`
and the fix is `uv sync`.

**The JavaScript side works the same way** with different names:
`package.json` is the list of wanted packages, `package-lock.json` pins
exact versions, `node_modules/` is the environment folder, and `npm ci`
is the install-from-lock command. To add a JavaScript package, run
`npm install some-package` (or `npm install -D some-package` for
tooling), which updates both files; commit both. `npm ci` (what you
normally run) refuses to change the lock file, which is exactly what you
want when you are not adding anything.

**Two environments, one repo.** `.venv/` and `node_modules/` sit side by
side at the root. `frob check` knows about both.

<details>
<summary><strong>If you are curious:</strong> why not the system Python, and what is `uv tool`?</summary>

Your computer likely has a Python already (macOS ships one, Ubuntu needs
it for system tools). Installing packages into it can break the
operating system's own scripts, and it is rarely the version we want.
uv leaves it alone entirely.

`uv tool install X` is for programs you run from anywhere, not
per-project packages: it makes a tiny private environment just for `X`
under `~/.local/share/uv/tools/` and puts the `X` command on your PATH.
frob is installed that way. crunk is instead a normal development
dependency of this project (it is in `pyproject.toml`), so it lives in
`.venv` and you run it as `uv run crunk`.
</details>

## 7. Get the code

You need to be a collaborator on the GitHub repository. If you have not
been added, send Logan your GitHub username and accept the invitation
email.

```
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/<org-or-user>/project-hullbreach-platform.git platform
cd platform
```

Replace the URL with the one from the green **Code** button on the
repository page; Logan will post it in the team chat.

Git asks for your GitHub username and a password. **Your GitHub password
does not work here.** You need a _personal access token_:

1. On GitHub: your avatar → Settings → Developer settings → Personal
   access tokens → Tokens (classic) → Generate new token.
2. Name it, pick an expiry (90 days is fine), tick the `repo` box,
   generate.
3. Copy the token and paste it where Git asks for a password. It does
   not show as you type.

So you only do that once:

```
git config --global credential.helper store
```

Check: `ls` shows `README.md`, `pyproject.toml`, `web`, and more.

<details>
<summary><strong>If that didn't work:</strong> clone problems</summary>

- **"Repository not found"**: typo in the URL, or you are not a
  collaborator yet. Check the invitation email.
- **"Authentication failed"**: you used your GitHub password instead of
  a token, or the token lacks the `repo` permission. Make a new one.
- **"destination path 'platform' already exists"**: you already cloned
  it. `cd platform`.

</details>

## 8. Install the project's dependencies

From inside the `platform` folder (`pwd` to confirm):

```
uv sync
npm ci
```

Section 6 says what these do. Each takes a minute or two the first time.

Check: `uv run hullbreach_server --help` prints usage text, and
`ls node_modules | head` prints folder names.

<details>
<summary><strong>If that didn't work:</strong> install problems</summary>

- **"No such file or directory: pyproject.toml"** or
  **"package-lock.json not found"**: wrong folder.
  `cd ~/projects/platform`.
- **`npm ci` fails with "Cannot read properties of null (reading
  'edgesOut')"**: your npm is too old for one of our packages. Run
  `npm install -g npm@latest` and try again.
- **Anything mentioning network, proxy, or ETIMEDOUT**: UF's guest wifi
  sometimes blocks package downloads. Use eduroam or a phone hotspot.
- **`uv sync` sits at "Resolving dependencies"**: give it a full minute
  on a slow connection.

</details>

## 9. Local settings

The API reads settings from a file called `.env` that is _not_ in Git
(it can hold passwords). Create yours from the template:

```
cp .env.example .env
```

For local development the defaults are already correct; you do not need
to edit anything. `cat .env` to see what is there. Every setting has a
safe default in `pyproject.toml` under `[tool.hullbreach_server]`; `.env`
overrides those, and command-line flags override `.env`.

If you could not install Docker, ask Logan for the shared database's
connection string and set it as `HULLBREACH_DATABASE_URL=` in `.env`.

## 10. Start the database

```
docker compose up -d db
```

The first run downloads PostgreSQL (a minute or two). It then runs in
the background until you stop it or reboot; run the same command again
after a reboot.

Check: `docker compose ps` shows a `db` line with `running (healthy)`.

`docker compose down` stops it and keeps your data.
`docker compose down -v` stops it and wipes the data.

<details>
<summary><strong>If that didn't work:</strong> database problems</summary>

- **"Cannot connect to the Docker daemon"**: open Docker Desktop and
  wait for it to finish starting.
- **"port is already allocated" / "address already in use"**: something
  else on your computer is using port 5432, usually another PostgreSQL.
  Stop it, or edit `docker-compose.yml` and change `"5432:5432"` to
  `"5433:5432"`, then change the port in your `.env`
  `HULLBREACH_DATABASE_URL` to `5433` as well.
- **`unhealthy`**: `docker compose logs db` and read the last few lines;
  paste them in the team chat if they do not make sense.

</details>

## 11. Run the API

```
uv run hullbreach_server
```

You should see a line ending in `serving on http://127.0.0.1:8000`.
Leave this terminal running. In a browser open
**http://127.0.0.1:8000/api/docs**: the interactive API documentation,
with a `/api/v1/health` entry. Click it, "Try it out", "Execute", and
you get `{"status": "ok", ...}` back.

`Ctrl + C` in that terminal stops it.

<details>
<summary><strong>If that didn't work:</strong> API problems</summary>

- **"Address already in use"**: an old copy is still running. Find its
  terminal and `Ctrl + C`, or run `uv run hullbreach_server --port 8001`
  and use that port.
- **"ModuleNotFoundError"**: `uv sync` did not finish, or someone added a
  package. Run `uv sync` again.
- **"This site can't be reached"**: the API is not running, or you typed
  `localhost:8000` and your machine resolves that oddly. Use exactly
  `127.0.0.1:8000`.

</details>

## 12. Run the website

Open a **second** terminal (keep the API running in the first),
`cd ~/projects/platform`, then:

```
npm run dev
```

It prints a local address, normally **http://localhost:5173**. Open it.
You should see a dark page with "Project Hullbreach". Edit
`web/src/App.tsx`, save, and the page updates on its own.

The website reaches the API through the `/api` path, which the dev
server forwards to port 8000, so the API from section 11 must be running
for anything that loads data.

`Ctrl + C` stops it.

<details>
<summary><strong>If that didn't work:</strong> website problems</summary>

- **"vite: not found"**: `npm ci` did not finish. Run it again.
- **Port 5173 is taken**: vite picks the next free one and prints it.
- **A blank page**: open the browser's developer console (`F12` →
  Console) and read the red text. Usually a typo in a `.tsx` file; the
  `npm run dev` terminal shows the same error with a line number.
- **A Tailwind class does nothing**: we do not use Tailwind's stock
  colors and sizes. Section 14, "Styling".

</details>

## 13. Run the checks

Before you push anything, run the same gate CI runs, from the `platform`
folder:

```
frob check
```

That runs Python lint (`ruff`), Python types (`ty`), Python tests
(`pytest`), TypeScript types (`tsc`), JS lint (`eslint`), formatting
(`prettier`), website tests (`vitest`), and frob's own structural gates.
The last line is `[OK]` or `[FAIL]` with an error count; the `## Errors`
section above it says what to fix. Most formatting problems fix
themselves with:

```
frob format
npx prettier --write .
```

Two more that CI also runs, for the website's design system:

```
uv run crunk check           # every color/size in CSS and className must be declared in crunk.toml
uv run crunk tokens --check  # the generated token files match crunk.toml
```

<details>
<summary><strong>If that didn't work:</strong> check problems</summary>

- **"frob: command not found"**: section 5f and the PATH box in 5c.
- **"no coverage stamp found; run: frob coverage --full"**: do what it
  says, `frob coverage --full --fail-on-degraded`, then `frob check`
  again. Happens on a fresh clone.
- **"PRE001 / SCOPE001 ... no active ticket is derivable"**: you have
  uncommitted changes and frob wants to know what they belong to. Ignore
  these two while you are still working; they clear once the change is
  committed on a branch (section 14).
- **A test fails that you did not touch**: pull `main` and re-run. If it
  still fails it is a real bug someone introduced; say so in the team
  chat rather than working around it.

</details>

## 14. Make a change the right way

`main` is protected. Nobody can push to it directly, Logan included.
Every change goes on its own **branch**, becomes a **pull request** (PR),
must pass CI, must be approved by one teammate, and is then merged. This
is the whole workflow, every time.

**1. Start from the latest `main`.**

```
git switch main
git pull
```

**2. Make a branch named for the work.** `feat/` for a feature, `fix/`
for a bug, `docs/` for documentation, `chore/` for housekeeping.

```
git switch -c feat/login-form
```

**3. Do the work.** Edit files. Run the API and website to try it. Add
a test (see "Tests" below).

**4. Run the checks** (section 13) until `frob check` is green.

**5. Commit.** A commit is a named snapshot. The message follows
[Conventional Commits](https://www.conventionalcommits.org/): a type, a
colon, a short sentence in the imperative.

```
git add -A
git commit -m "feat: add login form with client-side validation"
```

**6. Push the branch to GitHub.**

```
git push -u origin feat/login-form
```

Git prints a link to open a pull request. Click it, or go to the repo on
GitHub, where a yellow banner offers "Compare & pull request".

**7. Open the PR.** Fill in the template: what you changed, how to try
it. "Create pull request". CI starts within a minute; the checks appear
at the bottom of the PR page. Wait for **"All checks pass"** to go green.

**8. Get a review.** Ask a teammate in chat. They read the diff and may
ask for changes; edit, commit, `git push` again, and the PR updates on
its own.

**9. Merge.** Green and approved: click **"Squash and merge"**. Delete
the branch when GitHub offers. Back in your terminal:
`git switch main && git pull`.

<details>
<summary><strong>If that didn't work:</strong> Git and PR problems</summary>

- **"Your branch is behind" / "This branch has conflicts"**: `main`
  moved while you worked. Run
  `git switch main && git pull && git switch feat/login-form && git rebase main`.
  If Git says CONFLICT, open the files it names, find the `<<<<<<<`
  markers, keep the right lines, delete the markers, then
  `git add -A && git rebase --continue`. Lost? `git rebase --abort`
  puts everything back; ask for help.
- **"Updates were rejected because the remote contains work that you do
  not have"** on push: same cause; rebase as above, then
  `git push --force-with-lease`.
- **"remote: Permission to ... denied"**: not a collaborator, or your
  token expired. Section 7.
- **You committed to `main` by accident**: it cannot be pushed, so no
  harm done. `git switch -c feat/whatever` (your commit comes along),
  then `git switch main && git reset --hard origin/main`.
- **CI is red but green on your computer**: click "Details" next to the
  failing job; the last 30 lines of the log usually say why. Common
  cause: you forgot to `git add` a new file.
- **"All checks pass" stuck yellow**: click through to the Actions tab.
  A job waiting more than 10 minutes is GitHub being slow, not you.

</details>

### Tests

Every new Python module gets `tests/unit/test_<name>.py`. Anything that
wires modules together gets a case in `tests/system/test_build.py`,
which is the "did I build?" smoke test and must pass on a fresh
`uv sync`. Put a
`# frob:tests src/hullbreach_server/<file>.py::<symbol> kind="unit"`
comment inside each test so frob can map it; copy an existing one.
Website components get `web/tests/unit/<Name>.test.tsx`.

A test that documents a known, tracked bug is marked
`@pytest.mark.xfail(strict=True, reason="...")`. CI treats xfail as a
pass. Never delete or skip a failing test to get green.

### Styling

The design system is declared once in `crunk.toml` (colors, spacing and
type scales, radii, z-index layers). From it, `uv run crunk tokens`
generates `web/src/styles/tokens.css` and `web/tailwind.theme.json`;
never edit those two by hand. Tailwind classes use the declared names,
not Tailwind's defaults: `bg-paper`, `text-ink`, `text-muted`,
`bg-accent`, `gap-space-8`, `p-space-16`, `text-font-size-20`,
`rounded-radius-8`, `font-base`. A stock `bg-zinc-900` or `gap-2` does
nothing in the browser and fails `crunk check`. Need a new color or
size? Add it to `crunk.toml`, run `uv run crunk tokens`, commit all
three files. Hand-written CSS goes in `web/src/styles/<bucket>/`.

## 15. Everyday commands

```bash
docker compose up -d db          # start the database (after every reboot)
uv run hullbreach_server         # run the API           http://127.0.0.1:8000/api/docs
npm run dev                      # run the website       http://localhost:5173

frob check                       # the full gate (what CI runs)
frob format                      # auto-fix Python formatting + frob directives
frob test                        # run the tests for what you touched (or --all)
frob coverage --full             # refresh the coverage stamp
uv run pytest                    # just the Python tests
npm run test                     # just the website tests
uv run crunk check               # design-system lint
uv run crunk tokens              # regenerate tokens after editing crunk.toml
uv run crunk check --contrast    # color-contrast report

uv sync && npm ci                # after pulling changes that touched dependencies
make install                     # the same, stamp-guarded
make clean                       # delete build output and caches
```

## 16. When things break

In order:

1. **Read the last 20 lines of the error.** The useful part is at the
   bottom and usually names a file and a line number.
2. **Right folder?** `pwd` should end in `/platform`.
3. **Tools on PATH?** Open a _new_ terminal and try again.
4. **Docker Desktop running?** (database errors)
5. **Dependencies changed?** `uv sync && npm ci`.
6. **Nuke and rebuild.** Safe; nothing in these folders is yours:
   ```
   rm -rf .venv node_modules dist
   uv sync && npm ci
   ```
7. **Still stuck?** Paste the command you ran and the last 20 lines of
   output in the team chat. "It doesn't work" with no output cannot be
   helped; the output is what we need.

<details>
<summary><strong>Errors we have seen before</strong></summary>

- **`ModuleNotFoundError: No module named 'hullbreach_server'`**: `.venv`
  is stale, often after moving the folder. Step 6 above.
- **`pytest: error: unrecognized arguments: -n`**: same cause; step 6.
- **`error TS2307: Cannot find module '@/App'`**: `node_modules` is
  stale; step 6.
- **`TW004 ... resolves to Tailwind's default color`**: you used a stock
  Tailwind color. Section 14, "Styling".
- **`ORG005 ... is a CSS file outside web/src/styles`**: new CSS goes in
  `web/src/styles/<bucket>/`.
- **`REF001 ... has no inbound references`**: frob found a file nothing
  points at. Either something should import it, or (for config files)
  it needs a `[[refs.entrypoint]]` entry in `frob.toml`; copy an
  existing one.
- **`^M` in diffs, prettier complaining about every line**: Windows
  line endings. `git config --global core.autocrlf input` and re-clone.
  `.editorconfig` tells VS Code to use LF.
- **VS Code shows red squiggles but `frob check` is green**: VS Code is
  using a different Python. `Ctrl+Shift+P` → "Python: Select
  Interpreter" → the one inside `.venv`.

</details>

## 17. Glossary

- **API**: the Python program the website and the game talk to. It
  answers HTTP requests with JSON.
- **branch**: a separate line of work in Git. `main` is the one we ship;
  yours is where you work.
- **CI**: Continuous Integration. GitHub runs our checks on every pull
  request so a broken change cannot be merged.
- **commit**: a saved snapshot of your changes with a message.
- **crunk**: our design-system linter. Colors and sizes are declared
  once in `crunk.toml` and everything else is checked against it.
- **Docker**: runs the database in an isolated box so nobody installs
  PostgreSQL by hand.
- **environment**: a folder holding one project's copy of Python (or
  Node) and its packages. `.venv/` and `node_modules/`. Section 6.
- **frob**: our quality gate. One command that runs every lint,
  type-check, and test.
- **lock file**: `uv.lock` / `package-lock.json`. Exact versions of
  every package, so everyone installs the same thing.
- **PATH**: the folders your terminal searches for commands.
- **PR (pull request)**: a request to merge your branch into `main`,
  reviewed on GitHub.
- **PostgreSQL**: the database.
- **uv**: installs Python and Python packages for this project.
- **vite**: the website dev server and bundler.
- **WSL**: a Linux environment inside Windows; the terminal we use.

Work happens on branches; `main` only moves by a green pull request.
[CONTRIBUTING.md](CONTRIBUTING.md) has the rules,
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) the expectations, and
[SECURITY.md](SECURITY.md) how to report a vulnerability.
