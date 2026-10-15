# Project Hullbreach: Platform

This is the non-game half of Hullbreach: the website, the REST API behind
it, and the Postgres database that stores accounts, sessions, ELO and
match history. The Unity game lives in a separate repo,
[project-hullbreach-game](https://github.com/lognd/project-hullbreach-game#readme).

Company of Theseus, UF CEN3031, Fall 2026. All rights reserved, see
[LICENSE](LICENSE).

> **Read this first (current status).**
>
> - The profile, match history and account settings pages need two open
>   pull requests merged into `main`: **#38** (the `/api/v1/me` API those
>   pages call) and **#39** (keeps you signed in while you click between
>   pages). Until both are merged, `main` lets you register and log in,
>   but logging in drops you back on the home page already signed out,
>   and the Profile page shows "Not Found".
> - Even with both merged, **reloading the page (F5, or typing an address
>   into the address bar) signs you out.** The sign-in is kept only in
>   the open tab's memory, never on disk. Moving between pages by
>   clicking the links in the top bar keeps you signed in. Ticket
>   `~6TZCHZ0` tracks staying signed in across reloads.

Contents:

1. [What is this?](#what-is-this) -- game vs. platform, and how they talk
2. [Which guide do I need?](#which-guide-do-i-need)
3. [Step-by-step: run the platform on your computer](#step-by-step-run-the-platform-on-your-computer)
   -- written for someone who has never used a terminal
4. [Demo script for standup](#demo-script-for-standup)
5. [Connecting the game to the platform](#connecting-the-game-to-the-platform)
6. [Hosting a demo for other computers](#hosting-a-demo-for-other-computers)
7. [Troubleshooting](#troubleshooting) -- symptom, cause, fix
8. [Developer guide](#developer-guide) -- for people changing the code

## What is this?

Hullbreach is two programs that live in two separate GitHub repositories:

- **The game**
  ([project-hullbreach-game](https://github.com/lognd/project-hullbreach-game#readme)):
  the Unity game you actually play. One copy of it acts as the _game
  server_ (the "host" that runs the match), and every player runs a copy
  as a _game client_. Multiplayer happens entirely between game copies:
  clients talk to the game server directly, not through this repo.
- **The platform** (this repo): everything around the game. A **website**
  where players register, log in, and look at their profile and match
  history; an **API** (a program that answers requests from the website
  and from the game, over the network); and a **database** (Postgres)
  where the API keeps the accounts.

How they connect:

```
   YOUR BROWSER                         THE GAME (other repo)
 +----------------+          +-----------------+      +-----------------+
 | website pages  |          |   game client   |<---->|   game server   |
 | localhost:5173 |          |  (each player)  | play |(hosts the match)|
 +-------+--------+          +--------+--------+      +--------+--------+
         |                            |                        |
         | /api/... passed on         | "sign me in"           | "is this player's
         | by the website's           | POST /auth/login       |  sign-in real?"
         | dev server                 |                        | GET /auth/session
         v                            v                        v
 +-------------------------------------------------------------------------+
 |                 PLATFORM API    http://127.0.0.1:8000                    |
 |                 (this repo: `uv run hullbreach_server`)                  |
 +------------------------------------+------------------------------------+
                                      |
                                      v
                       +------------------------------+
                       | DATABASE (Postgres, Docker)  |
                       | 127.0.0.1:5432               |
                       +------------------------------+
```

The website and the game use the same accounts. Make an account on the
website, and you can sign in to the game with the same username and
password.

## Which guide do I need?

- **"I want to show the website"** (register, log in, profile, settings):
  this repo only. Follow the
  [step-by-step guide](#step-by-step-run-the-platform-on-your-computer),
  then the [demo script](#demo-script-for-standup).
- **"I want to show multiplayer"** (two players in one match): that is
  the game repo. The platform is optional, because players can join as
  guests. Follow the
  [game README](https://github.com/lognd/project-hullbreach-game#readme).
- **"I want to show signing in to the game with a website account"**:
  both. Do this repo's
  [step-by-step guide](#step-by-step-run-the-platform-on-your-computer)
  first, then [Connecting the game](#connecting-the-game-to-the-platform)
  and the game README's "Play with the platform" section.
- **"...and from a second computer on the same Wi-Fi"**: all of the
  above, plus
  [Hosting a demo for other computers](#hosting-a-demo-for-other-computers).

## Step-by-step: run the platform on your computer

This section assumes you have never used a terminal. Every step says what
to type, what it does, and what you should see. Text that looks like
`this` is something you type or something the computer prints. Grey
boxes hold commands: copy **one line at a time**, paste it into the
terminal, and press Enter.

The first time takes roughly 30-60 minutes, mostly downloads. Later
starts take about 2 minutes (see
[Starting again later](#starting-again-later)).

### Step 0: What a terminal is, and how to open one

A **terminal** is a window where you give the computer typed commands
instead of clicking. You type a line, press Enter, the computer runs it
and prints text back, then it shows the **prompt** again (a line ending
in `$` or `%`) to say it is ready for the next command.

Things that confuse everyone the first time:

- **Pasting**: in most terminals `Ctrl+V` does _not_ paste. Use
  right-click -> Paste, or `Ctrl+Shift+V` (Linux, Windows Terminal), or
  `Cmd+V` (Mac).
- **Passwords are invisible**: when a command asks for your password (for
  example after `sudo`), nothing appears while you type. That is normal.
  Type it and press Enter.
- **"Nothing happened"**: many commands print nothing when they succeed.
  If the prompt comes back with no red text and no word "error", it
  worked.
- **Stopping a running program**: click in its terminal and press
  `Ctrl+C` (hold Control, press C). On a Mac this is also Control, not
  Command.
- **Several terminals at once**: the platform is three programs running
  together, and two of them keep their terminal busy. You will open one
  extra terminal window (or tab) for each.

How to open one:

- **Windows**: we use **WSL**, a Linux system built into Windows, because
  every tool here is tested there. One-time setup:
  1. Click Start, type `PowerShell`, right-click "Windows PowerShell" ->
     "Run as administrator", click Yes.
  2. Type `wsl --install` and press Enter. It downloads Ubuntu (a kind of
     Linux). Restart the computer when it tells you to.
  3. After the restart an "Ubuntu" window opens by itself and asks for a
     new username and password. Pick ones you will remember (the
     password is invisible while typing). This is your _Linux_ password,
     which `sudo` asks for later.
  4. From now on, "open a terminal" means: Start -> type `Ubuntu` ->
     open it. **Every command in this guide goes in the Ubuntu window,
     not PowerShell**, unless it says otherwise.
- **macOS**: press `Cmd+Space`, type `Terminal`, press Enter.
- **Linux (Ubuntu)**: press `Ctrl+Alt+T`, or open "Terminal" from the
  app menu.

### Step 1: Install the tools (one time)

You need four programs. Each has a "check" command: if it prints a
version number, that tool is ready.

| Tool           | What it is for                                                      |
| -------------- | ------------------------------------------------------------------- |
| Git            | Downloads the code from GitHub.                                     |
| Docker         | Runs the database in a sealed box, so you never install Postgres.   |
| uv             | Installs the right Python and the API's packages, and runs the API. |
| Node.js (+npm) | Runs the website's development server.                              |

#### 1a. Git

- **Windows (in the Ubuntu window) and Linux**: type the line below. It
  asks for your password (invisible), then installs Git.
  ```
  sudo apt update && sudo apt install -y git
  ```
- **macOS**: type `git --version`. If a box offers to install "command
  line developer tools", click Install, wait, then run `git --version`
  again.

Check: `git --version` prints something like `git version 2.34.1` (any
version is fine).

#### 1b. Docker

- **Windows**: download Docker Desktop from
  https://www.docker.com/products/docker-desktop/ and install it, keeping
  "Use WSL 2" ticked. Open Docker Desktop, go to Settings -> Resources ->
  WSL integration, switch on "Ubuntu", click "Apply & restart". Close and
  reopen the Ubuntu window.
- **macOS**: download Docker Desktop from the same page ("Apple Silicon"
  for M1/M2/M3/M4 Macs, "Intel" otherwise), drag it into Applications,
  open it and accept the prompts.
- **Linux (Ubuntu)**: install Docker Desktop for Linux from the same
  page, or Ubuntu's own packages:
  ```
  sudo apt install -y docker.io docker-compose-v2
  sudo usermod -aG docker $USER
  ```
  The second line lets you use Docker without `sudo`. Log out and back in
  (or restart) for it to take effect.

Docker Desktop must be **open** (whale icon in the taskbar / menu bar)
whenever you use the database. You do not need a Docker account; skip
its sign-in screen.

Check: `docker compose version` prints something like
`Docker Compose version 2.40.3` (any 2.x is fine).

#### 1c. uv

Same on every system (on Windows, in the Ubuntu window):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

What this does: downloads uv's installer and runs it; uv lands in a
folder in your home directory. **Close the terminal and open a new one**
afterwards so it notices the new program.

Check: `uv --version` prints something like `uv 0.11.19`. Do **not**
install Python yourself; uv fetches the right version.

#### 1d. Node.js

Same on every system:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

What this does: installs `nvm`, a small tool that installs Node.js.
Close the terminal, open a new one, then:

```
nvm install 22
nvm alias default 22
```

What this does: downloads Node.js version 22 and makes it the default.

Check: `node --version` prints `v22.` and more digits (for example
`v22.18.0`), and `npm --version` prints a number such as `10.9.3`. Any
Node 20 or newer works.

### Step 2: Download the code

```
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/lognd/project-hullbreach-platform.git platform
cd platform
```

What each line does:

1. `mkdir -p ~/projects` makes a folder called `projects` in your home
   folder (`~` means "my home folder"). Prints nothing.
2. `cd ~/projects` moves the terminal _into_ that folder. `cd` means
   "change directory" (directory = folder).
3. `git clone ...` downloads this repo into a new folder called
   `platform`. You should see `Cloning into 'platform'...` and a few
   lines counting objects. The repo is public, so no login is needed.
4. `cd platform` moves into the downloaded code. **Every later command
   is run from here.** In a new terminal, first type
   `cd ~/projects/platform`.

Check: `ls` (list files) shows names including `README.md`,
`docker-compose.yml`, `package.json` and `pyproject.toml`.

Windows note: keep the code inside Ubuntu (`~/projects`), not under
`/mnt/c/...`, where everything is many times slower.

### Step 3: Install the project's packages

```
uv sync
```

What this does: creates a hidden `.venv` folder holding Python and every
package the API needs, at the exact versions the team uses. You should
see lines like `Using CPython 3.11.15`,
`Creating virtual environment at: .venv`, `Installed 52 packages`, and
then a list of package names starting with `+`.

```
npm ci
```

What this does: installs the website's packages into a `node_modules`
folder. It takes about a minute and ends like
`added 379 packages, and audited 380 packages in 6s`. A line saying
`1 high severity vulnerability` and suggesting `npm audit fix` may
follow: ignore it, and do **not** run `npm audit fix` (it rewrites files
the whole team shares).

### Step 4: Create your settings file

The platform reads its settings, including the database password, from a
file called `.env`. That file is private and never uploaded to GitHub.
Make yours from the provided example:

```
cp .env.example .env
```

What this does: copies the example settings to `.env`. Prints nothing.

Now choose a database password (letters, digits and dashes only, for
example `blue-ocean-4821`) and put it in the file:

1. Open the file in a simple editor: `nano .env`
2. With the arrow keys, go to the line
   `POSTGRES_PASSWORD=change-me-local-only` and replace
   `change-me-local-only` with your password.
3. Go to the line starting `HULLBREACH_DATABASE_URL=`. It contains
   `hullbreach:change-me-local-only@localhost`. Replace
   `change-me-local-only` there with **the same password**. The two must
   match exactly, or the API cannot get into the database.
4. Save and quit: `Ctrl+O`, Enter, then `Ctrl+X`.

Leave everything else as it is. (`HULLBREACH_GAME_SERVER_API_KEYS` is only
for the game; see
[Connecting the game](#connecting-the-game-to-the-platform).)

### Step 5: Start the database

Make sure Docker Desktop is open (Windows/Mac), then:

```
docker compose up -d db
```

What this does: starts Postgres in the background (`-d` = "detached":
you get the prompt back). The first time it downloads Postgres (about
100 MB). The output ends with lines like:

```
 Container platform-db-1  Created
 Container platform-db-1  Starting
 Container platform-db-1  Started
```

Wait about 10 seconds, then check it:

```
docker compose ps
```

You should see one row whose STATUS ends in `(healthy)`, like this:

```
NAME            IMAGE                COMMAND                  SERVICE   CREATED         STATUS                   PORTS
platform-db-1   postgres:17-alpine   "docker-entrypoint.s..."   db        7 seconds ago   Up 6 seconds (healthy)   127.0.0.1:5432->5432/tcp
```

If it says `(health: starting)`, wait a few seconds and run it again. If
you see `port is already allocated` or a `POSTGRES_PASSWORD` error, see
[Troubleshooting: database](#database-steps-5-6).

### Step 6: Create the database tables (do not skip)

```
uv run hullbreach_server db upgrade
```

What this does: creates the tables (users, sessions, matches and so on)
in the empty database. **If you skip it, the website still loads, but
registering fails with "request failed"**, because there is nowhere to
store the account. You will see many lines; the important ones are:

```
running alembic upgrade head
...
Running upgrade 0f6d70e4d209 -> 550676f68926, create sessions table
...
migrations are at head
```

Running it again is harmless (it just says `migrations are at head`).
Run it again whenever you download newer code with `git pull`.

### Step 7: Start the API (terminal 1)

```
uv run hullbreach_server
```

What this does: starts the API. **This terminal is now busy** as long as
the API runs; leave it open. Among the first lines you should see:

```
database connectivity check succeeded
serving on http://127.0.0.1:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

(The number in brackets differs every time.) Check: open a web browser
and go to http://127.0.0.1:8000/api/v1/health. The page shows
`{"status":"ok","version":"0.1.0"}`. The interactive API reference is at
http://127.0.0.1:8000/api/docs.

### Step 8: Start the website (terminal 2)

Open a **new** terminal window or tab (the first one is busy with the
API), go to the code, and start the website:

```
cd ~/projects/platform
npm run dev
```

What this does: starts the website's development server. This terminal
is now busy too. You should see this (your terminal draws the `->`
arrows as a single arrow character):

```
> hullbreach-web@0.1.0 dev
> vite

  VITE v8.3.0  ready in 656 ms

  ->  Local:   http://localhost:5173/
  ->  Network: use --host to expose
```

### Step 9: Try it

Open http://localhost:5173 in your browser. You should see a dark page
titled **Project Hullbreach** with "Build a ship. Breach a hull." and
**Register** and **Log in** links at the top.

1. Click **Register**. Enter a username (3-32 characters: letters,
   digits, `_`, `.` or `-`), an email, and a password (8 or more
   characters), and submit. You should see **Registration complete**.
2. Click **Log in** and sign in with the same username and password.
   With PRs #38 and #39 merged, the top bar now shows your username,
   **Profile**, **Matches**, **Settings** and **Log out**. On a `main`
   without them you land on the home page signed out again; that is the
   known issue [at the top](#project-hullbreach-platform).

That is the whole platform running. Next: the
[demo script](#demo-script-for-standup).

### Stopping everything

1. In the website terminal, press `Ctrl+C`. The prompt comes back.
2. In the API terminal, press `Ctrl+C`. It prints
   `INFO:     Application shutdown complete.` and the prompt comes back.
3. Stop the database (your accounts are kept):
   ```
   docker compose stop
   ```

`docker compose down` also stops it and also keeps your data.
`docker compose down -v` **deletes every account**; next time you start
from empty and must do Step 6 again.

### Starting again later

After a restart, open Docker Desktop (Windows/Mac), then in one
terminal:

```
cd ~/projects/platform
docker compose up -d db
uv run hullbreach_server
```

and in a second terminal:

```
cd ~/projects/platform
npm run dev
```

If you downloaded newer code with `git pull` since last time, run
`uv sync`, `npm ci` and `uv run hullbreach_server db upgrade` before
starting the API.

## Demo script for standup

Rehearse once before the meeting, then do it live. Have the API and
website running ([Steps 5-8](#step-5-start-the-database)). Use a
throwaway account such as `demo_pilot` / `demo-password-123`, with a new
name each time (names cannot be reused). Items 3-5 need PRs #38 and #39
on the code you run.

Move around **only by clicking the links in the top bar**. Do not reload
the page or type addresses during the demo; that signs you out (see
[the note at the top](#project-hullbreach-platform)).

- [ ] **1. Register.** http://localhost:5173 -> **Register** -> fill the
      form -> "Registration complete". Optionally register the same
      username again to show the field error "username already taken".
- [ ] **2. Sign in.** **Log in** -> first a wrong password to show
      "invalid username or password", then the right one. The top bar
      shows your username, **Profile**, **Matches**, **Settings** and
      **Log out**.
- [ ] **3. Profile.** Click **Profile**: your name, ELO **1200** (every
      new pilot starts there), Balance **0**, "No skins yet." and "No
      matches yet."
- [ ] **4. Edit account.** Click **Settings**. Change the **Display
      name** and save: "Settings saved." and the top bar updates. To
      change email or password you must also fill **Current password**:
      leaving it empty shows "Enter your current password to change your
      email or password.", and a wrong one shows "current password is
      incorrect".
- [ ] **5. Match history.** Click **Matches**: "No matches yet." The
      page and API are real, but nothing records matches yet (the game
      server's result upload, ticket T-0054, is not built), so every
      history is empty for now.
- [ ] **6. Log out**, then log back in with the changed details.
- [ ] **7. Game sign-in.** Start the game, sign in on its sign-in screen
      with the same account, and join a match. The steps, and what the
      game shows, are in the game README's
      [Play with the platform](https://github.com/lognd/project-hullbreach-game#readme)
      section. On the platform side, only the API (Step 7) must be
      running.

## Connecting the game to the platform

The game finds the platform by address. Its default is
`http://127.0.0.1:8000`, exactly where Step 7 starts the API, so **if
the game and the platform run on the same computer, there is nothing to
configure**: start the platform (Steps 5-7), then follow the game
README's "Play with the platform" section.

- **Windows + WSL**: a game running on Windows (for example in the Unity
  editor) reaches an API started in the Ubuntu window at
  `http://127.0.0.1:8000`; WSL forwards it automatically.
- **Plain `http://` only works in the Unity editor and development
  builds.** A release build of the game refuses non-HTTPS addresses, and
  this repo has no HTTPS setup. Demo from the editor or a development
  build.
- **Game on a different computer** from the platform: do
  [Hosting a demo for other computers](#hosting-a-demo-for-other-computers),
  then give the game the platform's address with its launch option
  `-hullbreachPlatformUrl http://<platform-ip>:8000` (or the
  `HULLBREACH_PLATFORM_URL` environment variable). The game README has
  the exact launch commands.
- **Requiring sign-in**: by default a game server lets guests in.
  Started with `-hullbreachRequirePlatformAuth`, it disconnects anyone
  not signed in with "This server requires a Hullbreach account. Sign in
  and reconnect."
- **Game server key** (`HULLBREACH_GAME_SERVER_API_KEYS` in `.env`): a
  shared secret meant to prove a game server is genuine. Make one with
  `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`, put it
  after `HULLBREACH_GAME_SERVER_API_KEYS=` in the platform's `.env`
  (then restart the API), and give the game server the same value as
  `HULLBREACH_PLATFORM_SERVER_KEY`. **The platform does not check it yet**
  when a game server verifies a player (ticket `~48H1VAK`), so a missing
  or wrong key changes nothing in a demo today. Setting it now keeps the
  demo working once that ticket lands.

## Hosting a demo for other computers

This is for a demo on one Wi-Fi network (for example laptops in the same
room). It is not internet hosting.

On the computer that runs the platform:

1. Start the API so other machines may connect (`0.0.0.0` means "accept
   connections from the network, not only from this computer"):
   ```
   uv run hullbreach_server --host 0.0.0.0
   ```
   The log now says `serving on http://0.0.0.0:8000`.
2. If other people should open the _website_ too, start it with:
   ```
   npm run dev -- --host
   ```
   It now prints a `Network:` line per network connection, for example
   `Network: http://192.168.1.23:5173/`. That is the address to share.
3. Find this computer's address on the Wi-Fi:
   - Windows: in PowerShell run `ipconfig` and read "IPv4 Address" under
     your Wi-Fi adapter (for example `192.168.1.23`).
   - macOS: `ipconfig getifaddr en0`
   - Linux: `hostname -I` (the first number)
4. Let the connections through the firewall:
   - Windows: a "Windows Defender Firewall" box may pop up the first
     time; tick **Private networks** and click Allow. Otherwise: Windows
     Security -> Firewall & network protection -> "Allow an app through
     firewall".
   - macOS: System Settings -> Network -> Firewall; if it is on, allow
     incoming connections for `python` and `node` when asked.
   - Linux with ufw: `sudo ufw allow 8000/tcp` and
     `sudo ufw allow 5173/tcp`.
5. **Windows + WSL extra step.** Other computers cannot reach programs
   inside WSL by default; only your own Windows can. On Windows 11 turn
   on _mirrored networking_: create the file `C:\Users\<you>\.wslconfig`
   with the two lines below, run `wsl --shutdown` in PowerShell, and
   reopen Ubuntu. The address to share is then the Windows one from
   `ipconfig`.
   ```
   [wsl2]
   networkingMode=mirrored
   ```
   On Windows 10, forward the ports instead, from an administrator
   PowerShell (`<wsl-ip>` is the first number `hostname -I` prints in
   Ubuntu; repeat with 5173 for the website):
   ```
   netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=<wsl-ip>
   ```
6. Test from the _other_ computer: open
   `http://<platform-ip>:8000/api/v1/health` in its browser. It must show
   `{"status":"ok","version":"0.1.0"}`. If it does not, the game cannot
   connect either; see [Troubleshooting](#game-cannot-reach-the-platform).

The database stays reachable only from the platform computer itself
(`127.0.0.1:5432`). That is correct: only the API talks to it.

### What is not production-ready

So nobody presents this as deployed:

- No HTTPS. Passwords cross the network unencrypted. Use throwaway
  passwords in demos.
- The website runs on its development server (`npm run dev`). This repo
  has no production web hosting setup.
- Reloading the page signs you out (ticket `~6TZCHZ0`).
- The game server key is not enforced on the session check (ticket
  `~48H1VAK`).
- Nothing records match results yet (T-0054), so ELO never changes and
  match history stays empty.
- The login attempt limit lives in the API's memory; restarting the API
  resets it.
- The database is a Docker container on one laptop, with no backups.

## Troubleshooting

Find your symptom, then read the cause and apply the fix. Text in quotes
is what the program actually prints.

### Installing and downloading

- **"command not found" for `uv`, `nvm`, `node` or `npm`**
  - Cause: the tool was installed after this terminal was opened, so the
    terminal does not know about it.
  - Fix: close the terminal, open a new one, try again. Still failing for
    uv: run `export PATH="$HOME/.local/bin:$PATH"`; if that helps, add
    the same line to the end of `~/.bashrc` (Mac: `~/.zshrc`). For nvm:
    `source ~/.nvm/nvm.sh`, and add that line too.
- **`npm ci` fails with "Cannot read properties of null (reading
  'edgesOut')"**
  - Cause: npm is too old.
  - Fix: `npm install -g npm@latest`, then `npm ci` again.
- **"No such file or directory: pyproject.toml", or npm cannot find
  `package.json`**
  - Cause: the terminal is not in the code folder.
  - Fix: `cd ~/projects/platform`, then retry.
- **Downloads time out (`ETIMEDOUT`, network errors)**
  - Cause: some guest Wi-Fi (UF guest included) blocks package
    downloads.
  - Fix: switch to eduroam or a phone hotspot.

### Database (Steps 5-6)

- **Something like "Cannot connect to the Docker daemon", or "The
  command 'docker' could not be found in this WSL 2 distro"**
  - Cause: Docker Desktop is not running, or (Windows) its WSL
    integration for Ubuntu is off.
  - Fix: open Docker Desktop and wait until it says it is running. On
    Windows check Settings -> Resources -> WSL integration -> Ubuntu is
    on, then reopen the Ubuntu window.
- **Something like "permission denied while trying to connect to the
  Docker daemon socket"** (Linux)
  - Cause: your user is not in the `docker` group yet.
  - Fix: `sudo usermod -aG docker $USER`, then log out and back in.
- **`required variable POSTGRES_PASSWORD is missing a value: set POSTGRES_PASSWORD in .env`**
  - Cause: there is no `.env`, or it has no `POSTGRES_PASSWORD`, or you
    are not in the `platform` folder.
  - Fix: [Step 4](#step-4-create-your-settings-file), from
    `~/projects/platform`.
- **`Bind for 0.0.0.0:5432 failed: port is already allocated`**
  - Cause: another database (another copy of this project, or a Postgres
    installed on your computer) already uses port 5432.
  - Fix, easiest: stop the other one (`docker ps` lists running
    containers; `docker stop <name>` stops one). Fix, if you need both:
    in `docker-compose.yml` change `"127.0.0.1:5432:5432"` to
    `"127.0.0.1:5433:5432"`, and in `.env` change `@localhost:5432/` to
    `@localhost:5433/` in `HULLBREACH_DATABASE_URL`, then
    `docker compose up -d db` again. Do not commit that
    `docker-compose.yml` change.
- **`docker compose ps` shows `unhealthy`, or shows nothing**
  - Fix: `docker compose logs db` and read the last lines. If you changed
    `POSTGRES_PASSWORD` _after_ the first start, the old password is
    still the real one (it is stored with the data): put the old one
    back, or wipe and recreate with `docker compose down -v`, then
    `docker compose up -d db` and Step 6 (this deletes all accounts).

### API (Step 7)

- **`configuration error: invalid configuration: database_url: Field required`**
  - Cause: no `.env`, or `HULLBREACH_DATABASE_URL` is missing from it.
  - Fix: [Step 4](#step-4-create-your-settings-file).
- **`ERROR: Cannot reach database at localhost:5432 (database=hullbreach): OperationalError`**
  - Cause: the database is not running, **or** the password in
    `HULLBREACH_DATABASE_URL` does not match `POSTGRES_PASSWORD` (both
    produce this same message), or the port is wrong.
  - Fix: `docker compose ps` must show `(healthy)`; then compare the two
    passwords in `.env` character by character.
- **`[Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): address already in use`**
  - Cause: an API is already running, probably in a terminal you forgot.
  - Fix: find that terminal and press `Ctrl+C`, or close it. (Starting
    on another port with `--port 8001` works for the API alone, but the
    website always sends requests to 8000.)
- **Registering fails: the page shows "request failed", and the API
  terminal prints a long error containing
  `relation "users" does not exist`**
  - Cause: Step 6 was skipped, so the database has no tables. (The
    `/api/v1/health` and `/api/v1/ready` pages still say ok, because the
    database itself is reachable.)
  - Fix: `uv run hullbreach_server db upgrade`, then register again. No
    restart needed.
- **http://127.0.0.1:8000/api/v1/health says "This site can't be
  reached"**
  - Cause: the API is not running, or the address is slightly different.
  - Fix: check the API terminal says `Uvicorn running`; type exactly
    `http://127.0.0.1:8000` (not `https`, and prefer `127.0.0.1` over
    `localhost`).

### Website (Steps 8-9)

- **The website terminal prints `http proxy error: /api/v1/...` and
  `Error: connect ECONNREFUSED 127.0.0.1:8000`; the page shows "request
  failed"**
  - Cause: the website is up but the API is not (or not on port 8000).
    The website passes every `/api/...` request to `127.0.0.1:8000`, set
    in `vite.config.ts`.
  - Fix: start the API (Step 7) on the default port.
- **`Port 5173 is in use, trying another one...`**
  - Cause: another website dev server is already running.
  - Fix: harmless. Use the `Local:` address it prints instead (for
    example `http://localhost:5174/`), or stop the old one with `Ctrl+C`
    in its terminal.
- **Something like `vite: not found`**
  - Cause: `npm ci` did not finish.
  - Fix: run `npm ci` again and read its last lines.
- **Blank white page**
  - Fix: press F12, open "Console", read the red text; the website
    terminal shows the same error.

### Signing in on the website

- **"invalid username or password"**
  - Cause: wrong username or password. Usernames ignore upper/lower
    case; passwords do not.
- **"too many attempts, try again later"**
  - Cause: 5 wrong passwords within 60 seconds for that username.
  - Fix: wait a minute (or restart the API, which resets the counter).
- **"username already taken" / "email already taken"** under a register
  field
  - Fix: pick another username or email.
- **"validation failed"** when registering
  - Cause: username shorter than 3 characters or with characters other
    than letters, digits, `_ . -`; password shorter than 8; or an email
    that does not look like a real address.
- **I logged in, then I was signed out**
  - Cause: the page was reloaded or an address was typed (sign-in lives
    only in the tab's memory), or you run a `main` without PR #39, where
    logging in itself reloads the page.
  - Fix: log in again and move around only by clicking links. Ticket
    `~6TZCHZ0` tracks fixing this.
- **The Profile page says "Not Found"**
  - Cause: PR #38 (the `/api/v1/me` API) is not in the code you run.
  - Fix: run a `main` that includes PR #38.

### Game cannot reach the platform

The quoted messages here are shown by the game (see the game README).

- **The game says "Cannot reach the Hullbreach servers (...)" when
  signing in**
  - Causes and fixes, most likely first:
    1. The API is not running: Step 7.
    2. The game is on another computer and still uses the default
       `http://127.0.0.1:8000`. `127.0.0.1` always means "this same
       computer", so it points at the player's own machine. Launch the
       game with `-hullbreachPlatformUrl http://<platform-ip>:8000`.
    3. The API only accepts connections from its own computer: start it
       with `--host 0.0.0.0`
       ([Hosting](#hosting-a-demo-for-other-computers), step 1).
    4. A firewall or WSL blocks it:
       [Hosting](#hosting-a-demo-for-other-computers), steps 4-5.
    5. A release build with an `http://` address: use the editor or a
       development build.
  - Check: on the game's computer, open
    `http://<platform-ip>:8000/api/v1/health` in a browser. If that page
    does not load, the game cannot connect either.
- **The game says "Wrong username or password."**
  - Cause: a typo, or the account does not exist on _this_ platform
    (every platform copy has its own database). Register on this
    platform's website first.
- **Disconnected from a match with "This server requires a Hullbreach
  account. Sign in and reconnect."**
  - Cause: the game server was started with
    `-hullbreachRequirePlatformAuth` and you joined without signing in.
  - Fix: sign in on the game's sign-in screen, then reconnect.
- **"Your platform session is invalid or expired. Sign in again."**
  - Cause: the platform told the game server your sign-in is not valid:
    you logged out, it expired (after 14 days), the platform database was
    wiped, or the game server uses a _different_ platform than the one
    you signed in to.
  - Fix: sign in again; make sure game client and game server use the
    same `-hullbreachPlatformUrl`.
- **"Could not verify your platform session (...)"**
  - Cause: the game server could not reach the platform at all. Same
    causes as "Cannot reach the Hullbreach servers" above, checked from
    the game server's computer.

## Developer guide

Everything below is for people changing the code. It assumes you have
done the [step-by-step guide](#step-by-step-run-the-platform-on-your-computer)
once, so the tools are installed and the platform runs.

I wrote this so you can go from a blank laptop to a merged PR without
pinging me every ten minutes. If something breaks, check
[Troubleshooting](#troubleshooting) and the collapsed "if that broke"
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
which proxies `/api` to uvicorn on 8000, which talks SQL to Postgres on
port 5432. The game client and game server hit the API directly (see the
[diagram](#what-is-this)).

Three tools sit on top and are not optional:

- **uv** installs Python and all Python packages into `.venv/` in the repo.
- **frob** (v2) is the structural gate and the ticket tracker: directives,
  doc links, coverage and the ticket ledger. CI runs `frob check` next to
  the ruff/ty/pytest and eslint/vitest jobs, and a PR cannot merge until
  all are green.
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

## Developer setup (once)

On top of the tools from [Step 1](#step-1-install-the-tools-one-time):

### Git identity

```
git config --global user.name "Your Name"
git config --global user.email "you@ufl.edu"
git config --global init.defaultBranch main
git config --global pull.rebase true
```

Cloning needs no login (the repo is public), but pushing does: you must
be a collaborator (send me your GitHub username), and Git asks for a
username and password the first time you push. Your GitHub password will
not work; you need a personal access token: GitHub -> your avatar ->
Settings -> Developer settings -> Personal access tokens -> Tokens
(classic) -> Generate new token, tick `repo`, copy it, paste it as the
password. Run `git config --global credential.helper store` so you only
do that once.

If you cannot install Docker at all (school laptop, no admin), you can
still do everything except run the DB locally; tell me and I will give
you the shared database string.

### frob

```
uv tool install frob==0.532.0
```

CI pins the same version. `frob --version` to check. `uv tool install` puts a program on your PATH
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

## Running it, for developers

The [step-by-step guide](#step-by-step-run-the-platform-on-your-computer)
covers the commands. The short version, each in its own terminal:

```
docker compose up -d db              # first run downloads Postgres; rerun after reboots
uv run hullbreach_server db upgrade  # after every pull that adds migrations
uv run hullbreach_server             # http://127.0.0.1:8000/api/docs
npm run dev                          # http://localhost:5173
```

`uv run hullbreach_server --help` prints the flags (`--host`, `--port`)
and the `db` subcommand.

There is deliberately no built-in database URL or password: the API
refuses to start without `HULLBREACH_DATABASE_URL`, and `docker compose`
refuses to start without `POSTGRES_PASSWORD`. The local database only
listens on `127.0.0.1`.

Other settings have defaults in `pyproject.toml` under
`[tool.hullbreach_server]`; `.env` (and real environment variables, as
`HULLBREACH_<FIELD>`) override that, and the `--host`/`--port` flags
override both. Unknown keys there are an error (a typo like
`databse_url` is reported, not ignored). If you are on the shared
database, set `HULLBREACH_DATABASE_URL=` in `.env` to the string I gave
you.

`docker compose ps` should show the `db` row with a STATUS ending in
`(healthy)`. The website is a dark page saying "Project Hullbreach";
edit anything under `web/src/` and it live-reloads. The site proxies
`/api` to port 8000, so the API has to be up for anything that loads
data. A Tailwind class that does nothing is almost always a stock
Tailwind color or size; see Styling below.

## Checks

Before pushing, run what CI runs, from the repo root:

```
frob check
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/
uv run ty check src/
npm run lint && npm run typecheck
uv run crunk check
uv run crunk tokens --check
```

`frob check` (frob v2) runs frob's own structural gates: directives, doc
links, COV001 coverage, ticket-ledger rules. It does not wrap ruff, ty, tsc,
eslint, prettier or vitest any more, so run those as above. It prints one
finding per line (`path:line:col: severity RULE message`) and exits 1 on an
error. Fix formatting with `uv run ruff format src/ tests/` and
`npx prettier --write .`.

Things frob says that look scary and are not:

- "SCOPE001 ...": only appears with `frob check --ticket`, when you
  edited a file outside the ticket's leased scope. Widen it with
  `frob ticket update <ticket> --add-scope GLOB`. See
  [CONTRIBUTING.md](CONTRIBUTING.md).
- A test you did not touch fails: pull `main` and rerun. If it still
  fails somebody broke it; say so in chat instead of working around it.

## Making a change

Looking for something to do? [docs/picking-up-work.md](docs/picking-up-work.md)
lists the open tickets by lane and which finished file to copy for each.

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
`text-font-size-20`, `rounded-radius-4`, `font-base`. A stock
`bg-zinc-900` or `gap-2` does nothing and fails `crunk check`. Need a new
color or size? Add it to `crunk.toml`, run `uv run crunk tokens`, commit
all three files. Hand-written CSS goes in `web/src/styles/<bucket>/`.

House look (enforced, details in docs/index.md "Visual design rules"):
square-ish corners (radius 0/2/4 only), no gradients, shadows, blur or
emojis, left-aligned pages, and the shared `Page`, `Button`, `TextField`,
`Notice` and `AppLink` components instead of one-off markup.

## Cheat sheet

```bash
docker compose up -d db          # database (after every reboot)
uv run hullbreach_server         # API      http://127.0.0.1:8000/api/docs
npm run dev                      # website  http://localhost:5173

frob check                       # the full gate
frob test --base main            # tests for what you touched (or --all)
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
- `^M` in diffs and prettier mad at every line: Windows line endings.
  `git config --global core.autocrlf input` and re-clone.
- VS Code red squiggles but `frob check` green: VS Code picked the wrong
  Python. `Ctrl+Shift+P` -> "Python: Select Interpreter" -> the one in
  `.venv`.

</details>

[CONTRIBUTING.md](CONTRIBUTING.md) has the branch and ticket rules,
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) the expectations, and
[SECURITY.md](SECURITY.md) how to report a vulnerability.
