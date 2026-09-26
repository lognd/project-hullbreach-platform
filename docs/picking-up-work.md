# Picking up work

Sprint 1 (accounts, sessions, roles, the page shell) landed as PRs #6
through #29. Everything after that is open and is meant to be split across
the team. This page is the map: where the open work is, how to claim a
piece, and which existing file to copy when you start.

## Claim a ticket

Every unit of work is a frob ticket under `tickets/`. Do not start from a
bare idea; start from a ticket id.

```
frob ticket doable                 # what is unblocked right now
frob ticket brief T-0031           # the full mission: body, acceptance, scope
git switch main && git pull
git switch -c T-0031-me-endpoint   # branch name starts with the ticket id
frob ticket start T-0031           # marks it in-progress and leases its scope
```

The branch name must start with the ticket id: frob derives the ticket from
it and CI runs `frob check --ticket` against that id. One ticket per branch,
one PR per branch, merge commit, delete the branch.

A ticket's `scope` is a write lease on the files it names. If you need to
touch a file outside it (you will: the router mount and the model registry
are shared), add it first:

```
frob ticket scope T-0031 --add src/hullbreach_server/api/__init__.py
frob ticket sweep T-0031
```

Two people cannot hold the same file at once, so shout in chat before
adding `docs/index.md` or `design/hullbreach.strata` to a scope; every
backend ticket wants both, and they serialize.

## Read the breadcrumbs in the code

Wherever a queued ticket has to plug into existing code there is a
`frob:todo T-####` comment naming it. Grep for your ticket id before you
write anything:

```
git grep "frob:todo T-0031"
```

The marker sites today:

| File                                          | What plugs in there                                                          |
| --------------------------------------------- | ---------------------------------------------------------------------------- |
| `src/hullbreach_server/api/__init__.py`       | every new resource router                                                    |
| `src/hullbreach_server/db/models/__init__.py` | every new ORM model                                                          |
| `src/hullbreach_server/api/auth.py`           | suspension check on login (T-0077), active skin in the game session (T-0040) |
| `web/src/router.tsx`                          | every new page                                                               |
| `web/src/App.tsx`                             | the cookie notice (T-0048)                                                   |
| `web/src/components/Footer.tsx`               | the data policy page (T-0049)                                                |
| `web/src/api/auth.ts`                         | request timeout (T-0102)                                                     |

When your ticket closes, delete its marker in the same PR. frob turns a
`frob:todo` red the moment its ticket is no longer open (TODO002), so a
stale one fails the gate for the next person.

## Lanes

The backlog splits into four lanes that rarely touch the same files. Pick a
lane, then work down its list; each row is one ticket, one PR. The "copy"
column is the finished file closest in shape to what you are building.

### Lane A: backend, player-facing (E3, E5)

| Ticket | What                                             | Copy from                                        |
| ------ | ------------------------------------------------ | ------------------------------------------------ |
| T-0031 | GET /api/v1/me aggregate                         | `api/auth.py` `session()`, `auth/schemas.py`     |
| T-0034 | PATCH /api/v1/me with password confirmation      | `api/auth.py` `login()`                          |
| T-0037 | DELETE /api/v1/me (anonymize, keep matches)      | `api/auth.py` `logout()`                         |
| T-0053 | Match and MatchPlayerStats models plus migration | `db/models/session.py`, T-0101's migration       |
| T-0056 | Pure Elo module (no DB, no FastAPI)              | `auth/passwords.py` for a pure helper with tests |
| T-0054 | POST /api/v1/matches with idempotency key        | `api/auth.py` `register()` for a 409 path        |
| T-0057 | RatingChange rows written on match record        | T-0053                                           |
| T-0059 | GET /api/v1/me/matches, cursor paged             | T-0031                                           |
| T-0062 | GET /api/v1/leaderboard with own rank            | T-0059                                           |

Start with T-0031 or T-0056; both are self-contained. T-0054 needs T-0052
(game-server API key dependency, lane C) first, so file that or pair on it.

### Lane B: web pages (E3, E4, E5, E6)

| Ticket | What                                               | Copy from                                         |
| ------ | -------------------------------------------------- | ------------------------------------------------- |
| T-0046 | Landing page with real content and calls to action | the `Landing()` stub in `router.tsx`              |
| T-0048 | Cookie notice, dismissal in localStorage           | `auth/session.ts` for the localStorage pattern    |
| T-0049 | Data policy page, linked from the footer           | `pages/Login.tsx` for page shape                  |
| T-0032 | Profile page, phone-width responsive               | `pages/Login.tsx`, `api/auth.ts` `fetchSession()` |
| T-0035 | Account settings form                              | `pages/Register.tsx` (inline validation)          |
| T-0038 | Delete-account confirmation                        | `components/Header.tsx` (logout control)          |
| T-0060 | Match history with paging                          | T-0032                                            |
| T-0063 | Leaderboard page                                   | T-0060                                            |
| T-0068 | Store page with category tabs                      | T-0032                                            |
| T-0102 | Request timeout in `api/auth.ts`                   | none, one function                                |

T-0046, T-0048, T-0049 and T-0102 need no backend and are the fastest first
PRs in the repo. Pages that read data (T-0032 onward) can be built against
a hard-coded fixture and `it.fails` tests until the endpoint lands; that is
how sprint 1 was done (see `docs/design/sprint-1.md`).

Every page gets a `web/tests/unit/<Name>.test.tsx`, and every className
must use the crunk token names (`bg-paper`, `gap-space-8`); a stock
Tailwind class fails `crunk check`.

### Lane C: backend, store, admin and game server (E6, E7, E13)

| Ticket         | What                                         | Copy from                             |
| -------------- | -------------------------------------------- | ------------------------------------- |
| T-0066         | Item and Inventory models plus migration     | `db/models/user.py`, `db/seed.py`     |
| T-0067         | GET /api/v1/catalog with owned flag          | `api/auth.py`                         |
| T-0070         | Currency ledger and payout on match record   | T-0066                                |
| T-0072         | POST /api/v1/store/purchase, one transaction | `auth/sessions.py` `issue_session()`  |
| T-0040         | PUT /api/v1/me/active-skin                   | T-0067                                |
| T-0052         | Game-server API key dependency               | `auth/deps.py` `get_current_user()`   |
| T-0076         | Admin player search and detail               | `auth/deps.py` `require_admin()`      |
| T-0077         | Suspension with ModerationLog; login refuses | `api/auth.py` `login()`               |
| T-0080, T-0081 | Admin set-rating and void-match              | T-0057                                |
| T-0083         | Admin item CRUD with retire                  | T-0066                                |
| T-0087         | Matchmaking queue endpoints                  | T-0052                                |
| T-0089         | ShipDesign CRUD as validated JSON            | T-0066, pydantic model for the design |
| T-0091         | Trust events from the game server            | T-0052                                |

Start with T-0066 or T-0052; almost everything else in this lane depends on
one of them. Coordinate with lane A on `db/models/__init__.py`.

### Lane D: admin web and ops (E7, T-0100)

| Ticket | What                                              | Copy from                                   |
| ------ | ------------------------------------------------- | ------------------------------------------- |
| T-0078 | Admin section: search, detail, suspend, reinstate | `pages/Login.tsx`, role from `useSession()` |
| T-0084 | Admin item editor                                 | T-0078                                      |
| T-0100 | Wire /health and /ready into a real caller        | `api/auth.ts`                               |
| T-0094 | Replay page design spike                          | `docs/design/sprint-1.md`                   |

Lane D depends on lane C's endpoints, so it is the right lane for someone
who also wants to review lane C PRs.

## Story and epic tickets

Tickets titled `S01`, `E1` and so on are stories and epics. They do not get
a branch; they close when their children close. Leave them alone unless you
are filing new children under them (`frob ticket new --parent T-0029`).

Every ticket's Jira key (or `jira:none`) is in
[backlog.md](backlog.md), the cross-reference generated by B6.

## Definition of done, per PR

- `frob check` green locally, then all three CI jobs green.
- Every new public symbol carries a `frob:tests` line pointing at a test.
- Every new endpoint or component has a paragraph in `docs/index.md`
  bound with `frob:describes`.
- The ticket's acceptance criteria are bound as evidence
  (`frob ticket evidence T-#### tests/unit/test_x.py::test_name`).
- The `frob:todo` marker for your ticket is gone.
- One approving review from someone not on the same lane.
