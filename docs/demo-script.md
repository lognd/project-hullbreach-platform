# Demo script (about 5 minutes)

A timed run-of-show for the front-end-to-back-end demo: a browser on the
left, the server console on the right, a third terminal for the "game
server". The plain checklist and troubleshooting live in the
[demo runbook](demo-runbook.md); this page is what to say and click, in
order. Default ports are used below; with others, use the URLs `make demo`
prints.

## Before the audience arrives

1. `make demo` (first run installs things, so do this ahead of time). It
   ends by printing the login line.
2. Terminal A: `make console-db` (API requests plus database changes).
3. Terminal B: empty, in the same checkout, for `make demo-match`.
4. Browser: http://localhost:5173 (the home page).
5. `make demo-match` is not needed yet; if you want a dry run, do it now
   and note that it raises `demo_pilot`'s ELO for real.

Navigate only with the in-app links. A reload or typed address signs you
out by design (INV-006).

## Run of show

| Time | Do                                                                                            | Say / point at                                                                                                                                                       |
| ---- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00 | Show the home page and terminal A side by side.                                               | Three layers: React website, FastAPI server, Postgres. The console is the server's own log.                                                                          |
| 0:30 | Click **Create account**. Register `showtime` / `showtime@example.com` / `demo-password-123`. | Console: `POST /api/v1/auth/register 201` and a `DB  user registered: 'showtime'` line. The password is hashed, never logged.                                        |
| 1:15 | **Log out**, then **Sign in** as `showtime`.                                                  | Console: `DB  login ok` and a `POST /auth/login 200`. The token lives in memory only.                                                                                |
| 1:45 | Click **Profile**, then **Matches**.                                                          | Rating 1200, no matches yet. Each page load is a `GET /me` line with the user id.                                                                                    |
| 2:15 | Log out, sign in as `demo_pilot` / `demo-password-123`, click **Profile**.                    | The seeded pilot: ELO about 1228 and 6 matches. Note the number.                                                                                                     |
| 2:35 | Click **Leaderboard** (before the match).                                                     | Public top players by ELO; your row (`demo_pilot`) is highlighted and its ELO reads about 1228. Note the rank. Console: `GET /api/v1/leaderboard 200`.               |
| 2:50 | Terminal B: `make demo-match`.                                                                | This is the game server speaking. It signs the request with the shared key (`X-Server-Key`); browsers never have it. Output ends `demo_pilot rating: 1228 -> 1243`.  |
| 3:20 | Terminal A: point at the new lines.                                                           | `POST /api/v1/matches 201 [server-key]` (only the presence of a key is shown) and `DB  match recorded ... ratings demo_pilot 1228 -> 1243, rival_xxxx 1200 -> 1185`. |
| 3:50 | Browser: click **Profile**, then **Matches** (no reload).                                     | New ELO and a new top row in history. Front end, server, database, and back.                                                                                         |
| 4:15 | Click **Leaderboard** again (after the match).                                                | `demo_pilot` now reads 1243 and `rival_xxxx` has joined the board at 1185: the same public list, re-ranked by the match you just posted.                             |
| 4:40 | Optional: `make smoke`, or run `make demo-match` again.                                       | One command walks register, login, profile, match, log out and checks every step.                                                                                    |
| 4:55 | **Log out**; Terminal B: `make stop`.                                                         | Accounts are kept. Done.                                                                                                                                             |

## The same steps by hand (curl)

If someone asks what `make demo-match` does, or it is unavailable:

```
API=http://127.0.0.1:8000/api/v1
KEY=<first value of HULLBREACH_GAME_SERVER_API_KEYS in your settings file>
curl -s -XPOST $API/auth/register -H 'content-type: application/json' \
  -d '{"username":"showtime2","email":"showtime2@example.com","password":"demo-password-123"}'
curl -s -XPOST $API/auth/login -H 'content-type: application/json' \
  -d '{"username":"showtime2","password":"demo-password-123"}'
```

The login reply holds `token` and `user.id`. Posting a match then needs
two user ids (see the curl block in the runbook, step 5), sent with
`-H "X-Server-Key: $KEY"`. A `201` means recorded.

`make server-key` prints a fresh key and where it goes; it changes nothing
by itself. `make demo` already creates one, so you rarely need it.

## If it breaks

| Symptom                                                                    | Cause                                             | Fix                                                                                                                                                                            |
| -------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Database rejected the password                                             | Stale `pgdata` volume from an older settings file | `uv run hullbreach_server reset-db` (deletes accounts), then `make demo` again                                                                                                 |
| Port in use                                                                | Another stack on 5432, 8000 or 5173               | Set `HULLBREACH_DB_PORT`, `HULLBREACH_PORT`, `HULLBREACH_WEB_PORT` (and the port inside `HULLBREACH_DATABASE_URL`) and a distinct `COMPOSE_PROJECT_NAME`; use the printed URLs |
| `make demo-match` says no game-server key, or curl to `/matches` gives 503 | No server key configured                          | `make demo` creates one; otherwise `make server-key`, put the value in the settings file, `make stop`, `make demo`                                                             |
| curl to `/matches` gives 401                                               | Wrong `X-Server-Key`                              | Use a value from `HULLBREACH_GAME_SERVER_API_KEYS`                                                                                                                             |
| Signed out suddenly                                                        | Reload or typed URL                               | Sign in again; use top-bar links                                                                                                                                               |
| Console is empty                                                           | Stack down or another checkout                    | Run `make console-db` from the checkout that ran `make demo`                                                                                                                   |
| Anything else                                                              |                                                   | `make status`, `./doctor.sh`, logs in `.hullbreach/logs`                                                                                                                       |
