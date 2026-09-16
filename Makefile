# Stamp files: `uv sync` / `npm ci` run only when their manifest changes.
PY_STAMP  := .venv/.install-stamp
WEB_STAMP := node_modules/.install-stamp

.PHONY: install install-py install-web clean run dev db build

# T-3400: this Makefile intentionally does NOT ship format/lint/typecheck/
# test/coverage/check targets. This is a frob-enabled polyglot project
# (see frob.toml) and frob IS the interface for those workflows, not a
# make wrapper around it -- use the commands below directly:
#
#   frob format     ruff check --fix + ruff format + frob: directive canon
#   frob check      the aggregate gate: ruff, ty, tsc, eslint, prettier,
#                   vitest, frob cycle/dup/arch/...
#   frob test       select and run tests for the touched set (or --all)
#   frob coverage   refresh coverage.xml / the coverage stamp
#
# Only bootstrap (install), the run/dev conveniences, build, and clean stay
# here: bootstrap cannot be a frob subcommand because it installs frob's
# own prerequisites, and the rest carry project-specific logic frob has no
# equivalent for. This repo is private and never published, so there is no
# upload target.

# ---------- install (stamp-guarded bootstrap) ----------

$(PY_STAMP): pyproject.toml uv.lock
	uv sync
	@touch $(PY_STAMP)

$(WEB_STAMP): package.json package-lock.json
	npm ci
	@touch $(WEB_STAMP)

install-py: $(PY_STAMP)
install-web: $(WEB_STAMP)
install: install-py install-web

# ---------- run ----------

db:
	docker compose up -d db

run: $(PY_STAMP)
	uv run hullbreach_server

dev: $(WEB_STAMP)
	npm run dev

build: $(WEB_STAMP)
	npm run build

# ---------- clean ----------

clean:
	rm -rf dist/ build/ coverage/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/ coverage.xml
	find . -path ./node_modules -prune -o -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -path ./node_modules -prune -o -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null; true
