# Demo runbook

One page for the live demo. Every command below is a real `Makefile`
target or documented in the [README](../README.md); nothing here is new.

## Before you start

- Installed: Git, uv, Docker (running), Node.js. Check with `./doctor.sh`
  (use `./doctor.sh --demo website` for this demo). On a fresh clone it
  also reports FAIL for web-deps, env-file, compose-file and settings;
  that is expected, `make demo` installs and creates those. Any other
  FAIL (a missing tool, a port in use) must be fixed first.
- Free ports 5432 (database), 8000 (API), 5173 (website), or pick others
  (see Troubleshooting).
- Two terminals open in the checkout, plus a browser.
- Rehearse once; the first `make demo` installs dependencies and is slow.

> **If `make demo` says the database rejected the password:** a stale
> `platform_pgdata` volume from an earlier `.env` is the cause. Run
> `uv run hullbreach_server reset-db` (deletes all accounts), then
> `make demo` again.

> **`make server-key` changes nothing by itself.** It only prints the
> value to set. Edit `.env` with it, then `make stop` and `make demo` to
> restart the stack; until then curl to `/matches` still answers 503.

## Run it

1. Terminal 1: `make demo`. It installs what is missing, starts the
   database, API and website, and seeds a demo player with 6 matches. It
   ends by printing the login line.
2. Browser: http://localhost:5173/login, sign in as `demo_pilot` /
   `demo-password-123`.
3. Navigate **only with the in-app links** in the top bar (Profile,
   Matches, Settings, Log out). A full page reload or typing an address
   signs you out by design (INV-006: the session token lives in memory).
   If it happens, just sign in again.
4. Terminal 2: `make console` shows one line per API request;
   `make console-db` also shows database changes (user registered, match
   recorded with rating changes). Leave it visible next to the browser.
5. Show Profile (ELO) and Matches (history), then trigger a match:
   - Quickest: `make smoke` in a third terminal. It
     registers a fresh smoke player and a rival, records a match with the
     server key, and checks the rating rose. The console shows each
     request and the `match recorded ... ratings 1200 -> 1216` DB line.
     Note this changes a smoke player, not `demo_pilot`.
   - To change `demo_pilot`'s ELO on screen, POST a match with curl (the
     game server's route, `POST /api/v1/matches`, needs the `X-Server-Key`
     header whose value is in `HULLBREACH_GAME_SERVER_API_KEYS` in your
     `.env`, set by `make demo`):

     ```
     API=http://127.0.0.1:8000/api/v1
     KEY=<value from .env>
     login() { curl -s -XPOST $API/auth/login -H 'content-type: application/json' \
       -d "{\"username\":\"$1\",\"password\":\"demo-password-123\"}"; }
     id() { python3 -c 'import json,sys; print(json.load(sys.stdin)["user"]["id"])'; }
     curl -s -XPOST $API/auth/register -H 'content-type: application/json' \
       -d '{"username":"rival1","email":"rival1@example.com","password":"demo-password-123"}' >/dev/null
     P=$(login demo_pilot | id); R=$(login rival1 | id)
     curl -s -XPOST $API/matches -H "X-Server-Key: $KEY" -H 'content-type: application/json' \
       -d "{\"match_id\":\"$(python3 -c 'import uuid; print(uuid.uuid4())')\",\"winner_id\":\"$P\",\"duration_seconds\":120,\"players\":[{\"user_id\":\"$P\",\"damage_dealt\":500},{\"user_id\":\"$R\",\"damage_dealt\":200}]}"
     ```

     A 201 means recorded. Register `rival1` only once (names cannot be
     reused); for a second match skip that line and reuse the rest with a
     new `match_id`.
6. In the browser click **Profile** (not reload) to see the new ELO, then
   **Matches** for the new row.
7. Finish: **Log out**, then `make stop` (accounts are kept).

## Troubleshooting

| Symptom                                             | Cause                                      | Fix                                                                                                                                                                                                                                       |
| --------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Signed out suddenly                                 | Page reload or typed URL (INV-006)         | Sign in again; use top-bar links only                                                                                                                                                                                                     |
| `make demo` or doctor says a port is in use         | Another stack on 5432/8000/5173            | Set `HULLBREACH_DB_PORT`, `HULLBREACH_PORT`, `HULLBREACH_WEB_PORT` (and the port in `HULLBREACH_DATABASE_URL`) in `.env`, plus a distinct `COMPOSE_PROJECT_NAME` if another copy's database is up; then `make demo`. Use the printed URLs |
| `make demo` says the database rejected the password | Old database volume from an earlier `.env` | Restore the old `.env`, or `uv run hullbreach_server reset-db` (deletes all accounts) then `make demo`                                                                                                                                    |
| `make smoke` says nothing answers                   | Stack not running                          | `make demo` first; `make status` shows what runs                                                                                                                                                                                          |
| curl to `/matches` answers 401                      | Missing or wrong `X-Server-Key`            | Use a value from `HULLBREACH_GAME_SERVER_API_KEYS` in `.env`                                                                                                                                                                              |
| curl to `/matches` answers 503                      | No server key configured                   | `make server-key` prints what to set; restart with `make stop` then `make demo`                                                                                                                                                           |
| Console is empty                                    | Stack not running or wrong checkout        | Run `make console` from the same checkout as `make demo`                                                                                                                                                                                  |
| Anything else                                       |                                            | `make status`, `./doctor.sh`, logs in `.hullbreach/logs`                                                                                                                                                                                  |
