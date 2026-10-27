# Demo runbook

One page for the live demo. For a timed, minute-by-minute show see the [demo script](demo-script.md).
Every command below is a real `Makefile`
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
   database, API and website, and seeds four demo players with 14 matches between them
   (`demo_pilot` has 9; open any row on **Matches** for its detail). It
   ends by printing the login line.
2. Browser: http://localhost:5173/login, sign in as `demo_pilot` /
   `demo-password-123`.
3. Navigate **only with the in-app links** in the top bar (Profile,
   Matches, Settings, Log out). A page reload keeps you signed in: login sets
   an HttpOnly session cookie and the app restores it on load. Log out clears
   it.
4. Terminal 2: `make console` shows one line per API request;
   `make console-db` also shows database changes (user registered, match
   recorded with rating changes). Each line shows the signed-in username and
   a short summary of the request payload (passwords and tokens appear as
   `<redacted>`; `--no-payloads` hides it). Leave it visible next to the
   browser.
5. Show Profile (ELO) and Matches (history), then trigger a match:
   - Quickest: `make smoke` in a third terminal. It
     registers a fresh smoke player and a rival, records a match with the
     server key, and checks the rating rose. The console shows each
     request and the `match recorded ... ratings 1200 -> 1216` DB line.
     Note this changes a smoke player, not `demo_pilot`.
   - To change `demo_pilot`'s ELO on screen, run `make demo-match` (it
     does the curl below for you and prints the rating change), or POST a match with curl (the
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
7. Show the store: click **Store**. `demo_pilot` has a starter balance of 630
   (300 granted once as a ledger row with reason `demo_grant`, plus the
   match payouts from the seeded history) and the catalog has four cheap demo items
   (**Rookie Stripes** 40, **Rust Bucket Wrap** 60, **First Flight Decal** 80,
   **Demo Day Badge** 100). Buy **Rookie Stripes**, then click **Profile** and press the
   skin to equip it (it shows "(equipped)"); press it again to unequip it. Everything else costs 199 or more and a match pays only 50/10,
   so do not try to buy those live.

   To buy something pricier, give the account more credits first (demo
   only): `make grant-credits USER=demo_pilot AMOUNT=500`. It prints the
   new balance and the console shows `DB  credits granted: +500 to
'demo_pilot' (balance N)`; reload the Store (go to another page and
   back) and the larger balance is there. The command works only when
   `HULLBREACH_DEMO_MODE=1` is in `.env` (a fresh `make demo` writes it; add
   the line by hand to an older `.env`). Without it the command refuses, so
   it is unavailable in production, and there is no web endpoint for it.
   The footer shows **API up** (cyan dot) while the backend and database answer
   `/api/v1/ready`; **API down** (orange) means the front-to-back link is broken.

8. Finish: **Log out**, then `make stop` (accounts are kept).

## Verified step list (rehearsal)

Rehearsed end to end on a clean checkout (no `.env`, no `node_modules`),
with the ports moved so nothing already running was touched:

```
export HULLBREACH_DB_PORT=54329 HULLBREACH_PORT=8010 HULLBREACH_WEB_PORT=5183
export COMPOSE_PROJECT_NAME=hullbreach-demo   # own database volume
make demo            # about 15 s once dependencies are installed
make console-db      # second terminal
```

Driven through the real website (headless Chromium), each step checked
against the console:

| Step in the browser                         | Console shows                                                                                           |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Create account `showtime`                   | `POST /api/v1/auth/register 201`, `DB  user registered`                                                 |
| Log in, click **Profile** (ELO 1200)        | `DB  login ok`, `POST /auth/login 200`, `GET /me 200`                                                   |
| Log out                                     | `DB  logout ... session revoked`, `POST /auth/logout 204`                                               |
| Log in `demo_pilot`, **Profile** (ELO 1239) | same lines for `demo_pilot`; 9 matches, balance 630                                                     |
| **Store**, buy **Rookie Stripes** (40)      | `POST /store/purchase 200 user=demo_pilot body={"item_id":...}`, `DB  purchase: ... bought ... balance` |
| **Profile**, press the skin to equip it     | `PUT /me/equipped 200`, `DB  skin equipped: ...`                                                        |
| Press the equipped skin again to unequip it | `DELETE /me/equipped 204`, `DB  skin unequipped: ...`                                                   |
| **Log out**                                 | `DB  logout`                                                                                            |

Notes from the rehearsal: registering does not sign you in (you land on
a "Registration complete" page with a **Log in** link); buying any item
over the balance shows a red "costs N, you have M" error and the console
prints a `purchase refused` warning (that is the correct refusal, not a
fault); a 401 on `GET /me` before sign-in is the app checking for a
session cookie and is expected.

## Wiping between runs

`make demo-wipe` (or `uv run hullbreach_server wipe-demo`) removes every
trace of earlier runs that this checkout can reach: it stops the website
and API, runs `docker compose down -v` for the compose project (database
container and volume), and deletes `.hullbreach/logs/*`,
`.hullbreach/run/*` and any `hullbreach-support-*.zip`. It needs a
terminal and asks you to type the volume name back.

Why not `reset-db`: it recreates only the database. The API log survives
it, and `make console` replays the last lines of `.hullbreach/logs/api.log`,
so an old username can reappear on screen after a database wipe even
though the server never reads logs to make names.

What no command can clear, and the wipe prints after it finishes:

- Browser: cookies, localStorage and saved form data for the site, plus
  autofill (a saved username offered in the sign-in box comes from here).
- Game: the saved name in Unity PlayerPrefs, and any
  `HULLBREACH_PLATFORM_USERNAME`, `_PASSWORD` or `_TOKEN` in the
  environment that launches the game.
- Other checkouts: every folder has its own compose project, volumes,
  `.env` and logs. Run the wipe inside each copy you have demoed from (for
  example one under `/mnt` on a Windows drive). The wipe warns when
  `COMPOSE_PROJECT_NAME` is set by hand, since checkouts sharing a name
  share a volume, and lists other `*pgdata` volumes it did not touch.

## Demonstrating ship motion

The web app has no motion view; ships fly only in the Unity game (the
`game` repo). This needs the Unity editor and was not run while writing
this section; the steps are quoted from the game README.

Single player, no platform (Guide 1):

1. Open the project in Unity, then `Assets` > `Scenes` and double-click
   `DemoScene`.
2. Press Play. You start in Build mode; press `Tab` for Fly mode.
3. In Fly mode `W`/`S` thrust, `A`/`D` turn, `Space` fires, `R` resets
   the ship, `O` cycles the stress and damage overlays.

With a platform account (Guide 4):

1. Run `make demo` here and register an account on the website.
2. In the game folder run `.\play.cmd online` (add
   `--platform-url ...` if the API is not at `http://127.0.0.1:8000`).
3. Sign in on the lobby screen, host and join as in Guide 2, then
   **START GAME** and fly as above.

## If it breaks

1. `make status` shows what runs; logs are in `.hullbreach/logs`.
2. Ports taken: set the three `HULLBREACH_*_PORT` variables as above
   before `make demo`. The doctor names the process holding a port; leave
   unrelated processes alone.
3. "Database rejected the password": the compose project's volume is from
   an older `.env`. Safest: pick a fresh project name with
   `COMPOSE_PROJECT_NAME=hullbreach-demo` (never touches the old volume).
   Only if the old data does not matter, `uv run hullbreach_server reset-db`
   deletes this project's volume.
4. Console empty: run `make console-db` from the same checkout and with
   the same port variables as `make demo`.
5. Store buy does nothing: the item costs more than the balance; use a cheap one
   (Rookie Stripes 40, Demo Day Badge 100).
6. Clean up after a rehearsal: `make stop`, then remove the volume you
   created (`docker volume rm hullbreach-demo_pgdata`) if you want a
   fresh start.

## Troubleshooting

| Symptom                                             | Cause                                      | Fix                                                                                                                                                                                                                                       |
| --------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `make demo` or doctor says a port is in use         | Another stack on 5432/8000/5173            | Set `HULLBREACH_DB_PORT`, `HULLBREACH_PORT`, `HULLBREACH_WEB_PORT` (and the port in `HULLBREACH_DATABASE_URL`) in `.env`, plus a distinct `COMPOSE_PROJECT_NAME` if another copy's database is up; then `make demo`. Use the printed URLs |
| `make demo` says the database rejected the password | Old database volume from an earlier `.env` | Restore the old `.env`, or `uv run hullbreach_server reset-db` (deletes all accounts) then `make demo`                                                                                                                                    |
| `make smoke` says nothing answers                   | Stack not running                          | `make demo` first; `make status` shows what runs                                                                                                                                                                                          |
| curl to `/matches` answers 401                      | Missing or wrong `X-Server-Key`            | Use a value from `HULLBREACH_GAME_SERVER_API_KEYS` in `.env`                                                                                                                                                                              |
| curl to `/matches` answers 503                      | No server key configured                   | `make server-key` prints what to set; restart with `make stop` then `make demo`                                                                                                                                                           |
| Console is empty                                    | Stack not running or wrong checkout        | Run `make console` from the same checkout as `make demo`                                                                                                                                                                                  |
| Anything else                                       |                                            | `make status`, `./doctor.sh`, logs in `.hullbreach/logs`                                                                                                                                                                                  |
