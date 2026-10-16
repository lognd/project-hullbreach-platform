#!/usr/bin/env bash
# Hullbreach platform doctor: run this first, on macOS, Linux or WSL.
#
#   ./doctor.sh                  check everything and explain any fix
#   ./doctor.sh --demo website   check only what one demo needs
#   ./doctor.sh --help           all options
#
# This wrapper only makes sure the four tools exist (git, uv, Docker,
# Node.js) and offers their official installers, asking first. Every real
# check lives in `uv run hullbreach_server doctor` (src/hullbreach_ops), so
# there is one implementation. See README.md "Step 1: Get the code and run
# the doctor".
set -u

cd "$(dirname "$0")" || exit 1

README="README.md, section"
missing_required=0

say() { printf '%s\n' "$*"; }

ask_yes() {
  # ask_yes "question" -> 0 only when a person typed y or yes.
  if [ ! -t 0 ]; then
    say "  (not asking: no keyboard attached; run ./doctor.sh in a terminal to be asked)"
    return 1
  fi
  printf '%s [y/N] ' "$1"
  read -r answer || return 1
  case "$answer" in
    y | Y | yes | YES | Yes) return 0 ;;
    *) return 1 ;;
  esac
}

have() { command -v "$1" >/dev/null 2>&1; }

kind="linux"
case "$(uname -s 2>/dev/null)" in
  Darwin) kind="mac" ;;
  Linux)
    if grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
      kind="wsl"
    fi
    ;;
  MINGW* | MSYS* | CYGWIN*)
    say "This is Git Bash (or a similar Windows shell), which the platform does not support."
    say "The platform runs inside WSL (Linux inside Windows). Do this instead:"
    say "  1. Double-click doctor.cmd in this folder (or run it from PowerShell)."
    say "     It explains how to install WSL and open an Ubuntu terminal."
    say "  2. In the Ubuntu terminal, clone the code again and run ./doctor.sh there."
    say "See $README \"Step 0: What a terminal is, and how to open one\"."
    exit 1
    ;;
esac

say "Hullbreach platform doctor (setup check)"
say "Checking the tools this project needs: git, uv, Docker, Node.js."
say ""

# ---------- uv (required: it runs the real doctor) ----------
if ! have uv && [ -x "$HOME/.local/bin/uv" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi
if have uv; then
  say "  uv:      found ($(uv --version 2>/dev/null))"
else
  say "  uv:      NOT FOUND. uv installs Python and this project's Python packages."
  say "           Official installer: curl -LsSf https://astral.sh/uv/install.sh | sh"
  if ask_yes "           Run the official uv installer now?"; then
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
      export PATH="$HOME/.local/bin:$PATH"
    fi
  fi
  if have uv; then
    say "  uv:      installed ($(uv --version 2>/dev/null))"
  else
    say "           Without uv the doctor cannot run. See $README \"2c. uv\"."
    missing_required=1
  fi
fi

# ---------- git ----------
if have git; then
  say "  git:     found ($(git --version 2>/dev/null))"
else
  say "  git:     NOT FOUND. git downloads and updates this code."
  case "$kind" in
    mac)
      say "           Install it with Apple's developer tools: xcode-select --install"
      if ask_yes "           Run xcode-select --install now?"; then
        xcode-select --install
        say "           Finish the window that opened, then run ./doctor.sh again."
      fi
      ;;
    *)
      if have apt-get; then
        say "           Install it with: sudo apt-get update && sudo apt-get install -y git"
        if ask_yes "           Run that now (it asks for your password)?"; then
          sudo apt-get update && sudo apt-get install -y git
        fi
      else
        say "           Install git with your system's package manager."
      fi
      ;;
  esac
  have git || say "           See $README \"2a. Git\"."
fi

# ---------- Docker ----------
if have docker; then
  say "  Docker:  found ($(docker --version 2>/dev/null))"
else
  say "  Docker:  NOT FOUND. Docker runs the project's database."
  case "$kind" in
    wsl)
      say "           On Windows, install Docker Desktop in WINDOWS (not inside WSL):"
      say "             https://docs.docker.com/desktop/setup/install/windows-install/"
      say "           Then in Docker Desktop: Settings > Resources > WSL integration,"
      say "           turn on your Ubuntu distribution, Apply, and reopen this terminal."
      ;;
    mac)
      say "           Install Docker Desktop for Mac:"
      say "             https://docs.docker.com/desktop/setup/install/mac-install/"
      say "           Open it once so it finishes setting up, then run ./doctor.sh again."
      ;;
    *)
      say "           Official convenience installer: curl -fsSL https://get.docker.com | sh"
      if ask_yes "           Run the official Docker installer now (it asks for your password)?"; then
        curl -fsSL https://get.docker.com -o "${TMPDIR:-/tmp}/get-docker.sh" &&
          sudo sh "${TMPDIR:-/tmp}/get-docker.sh"
        rm -f "${TMPDIR:-/tmp}/get-docker.sh"
        say "           Then let your user run docker: sudo usermod -aG docker \"$USER\""
        say "           and log out and back in."
      fi
      ;;
  esac
  have docker || say "           See $README \"2b. Docker\"."
fi

# ---------- Node.js ----------
if ! have node && [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/.nvm/nvm.sh"
fi
if have node; then
  say "  Node.js: found ($(node --version 2>/dev/null))"
else
  say "  Node.js: NOT FOUND. Node.js runs the website."
  say "           Official nvm installer, then Node 22:"
  say "             curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash"
  say "             nvm install 22"
  if ask_yes "           Run those two now?"; then
    if curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash; then
      export NVM_DIR="$HOME/.nvm"
      # shellcheck disable=SC1091
      . "$NVM_DIR/nvm.sh" && nvm install 22
    fi
  fi
  if have node; then
    say "  Node.js: installed ($(node --version 2>/dev/null)). Open a NEW terminal later so it stays on PATH."
  else
    say "           See $README \"2d. Node.js\"."
  fi
fi

say ""
if [ "$missing_required" -ne 0 ]; then
  say "Stopped: uv is needed to run the rest of the checks."
  say "Install it as shown above, open a new terminal, and run ./doctor.sh again."
  exit 1
fi

say "Starting the full check (the first run downloads Python packages; this can take a minute)..."
say ""
uv run --quiet hullbreach_server doctor "$@"
status=$?
if [ "$status" -ne 0 ]; then
  if [ ! -d .venv ]; then
    say ""
    say "uv could not install the Python packages. Check your internet connection,"
    say "then run: uv sync   (and read its last lines), then ./doctor.sh again."
    say "See $README \"Step 3: Install the project's packages\"."
  fi
  exit "$status"
fi
