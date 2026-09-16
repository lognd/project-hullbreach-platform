## Done report

Implemented T-0044 per docs/design/sprint-1.md sec.6: web/src/router.tsx
(createBrowserRouter with /, /register, /login, not-found routes, each a
minimal in-file placeholder pending T-0017/T-0021/T-0045), web/src/App.tsx
as the Header/Outlet/Footer page shell, web/src/components/Header.tsx
(signed-out Register/Login links, signed-in username + Log out stub, all
real <a>/<button> elements for keyboard access), web/src/components/
Footer.tsx (cookie/data-policy links), and web/src/main.tsx wired to
RouterProvider.

Header's signed-in state needs a real session store to read, so this
ticket also adds web/src/auth/session.ts (StoredSession, saveSession,
loadSession, clearSession, useSession) -- the "session store shape T-0021
fills in" the sprint-1 doc anticipates. Scope was extended (via `frob
ticket scope --add`, each with a recorded reason) to
web/src/auth/session.ts, web/src/main.tsx, web/tests/unit/App.test.tsx,
web/tests/unit/Login.test.tsx, docs/index.md, package.json, and
package-lock.json, since the design as specified could not be implemented
or its own test suite kept green without touching them:

- web/tests/unit/App.test.tsx asserted App's OLD landing-page content;
  updated it to assert the new shell responsibility (banner/contentinfo)
  instead of leaving a now-false assertion in place.
- web/tests/unit/Login.test.tsx's "auth/session.ts" describe block
  (4 tests) exercises exactly the session.ts shape this ticket adds, in
  isolation from the Login page; those 4 were flipped from it.fails to
  it (the 6 "Login page" tests, which need T-0021's pages/Login.tsx,
  are untouched and still fail).
- docs/index.md documents the new modules and carries the frob:doc
  anchors this ticket's new public symbols point at.
- package.json/package-lock.json add react-router-dom.

Logout is a real, focusable <button> but its onClick is a documented
no-op placeholder (frob:todo T-0024): it does not clear the session or
call the API. That is T-0024's job, and its two tests in
Header.test.tsx (logout clears session/navigates, logout POSTs) are
left it.fails, per the dispatch instructions.

Known blockers not resolved by this ticket (reported to the coordinator,
not forced past):

1. SELFAUDIT001 (design/hullbreach.strata): session.ts's use of
   localStorage needs a `may "client_storage" via
   "web/src/auth/session.ts";` grant on the `browser` node. That file is
   under an active cross-worktree lease held by T-0015, so `frob ticket
   scope T-0044 --add design/hullbreach.strata` was refused
   (ScopeLeaseConflict); per instructions I did not --steal it. This is
   the one error `frob check --ticket T-0044` still reports.
2. `frob ticket evidence`/`frob ticket close` cannot verify any vitest
   (.ts/.tsx) evidence id in this frob install: `frob.testing.
   LANGUAGE_COLLECTORS` keys TypeScript as "ts", but `frob.lang.
   language_for_extension` (which `frob test`'s own selection uses, and
   which frob.toml's `[[test.runner]] language = "typescript"` matches)
   canonically returns "typescript" -- so evidence verification looks
   for a "ts" runner that can never exist here, always failing with
   NoRunner/EvidenceNotPassing even though `frob test`/`npx vitest run`
   both pass the exact same id. This is a frob defect, not specific to
   this ticket's code, and blocks recording evidence or closing T-0044
   (or any other web-track ticket) through the standard flow.

All web gates are green: npm run lint, npx prettier --check ., npx tsc
--noEmit, npx vitest run (16 passed, 20 expected fail), npm run build,
uv run crunk check, uv run crunk tokens --check, frob test --base main.
`frob check --ticket T-0044` reports 0 errors other than the SELFAUDIT001
item above.

### Changed
```
 docs/index.md                  | 31 ++++++++++++++++
 package-lock.json              | 60 ++++++++++++++++++++++++++++++-
 package.json                   |  3 +-
 tickets/T-0044/ticket.md       | 64 ++++++++++++++++++++++++++++++++-
 web/src/App.tsx                | 20 +++++++----
 web/src/auth/session.ts        | 80 ++++++++++++++++++++++++++++++++++++++++++
 web/src/components/Footer.tsx  | 11 ++++++
 web/src/components/Header.tsx  | 61 ++++++++++++++++++++++++++++++++
 web/src/main.tsx               |  5 +--
 web/src/router.tsx             | 60 +++++++++++++++++++++++++++++++
 web/tests/unit/App.test.tsx    | 13 ++++---
 web/tests/unit/Header.test.tsx | 31 ++++++++++------
 web/tests/unit/Login.test.tsx  |  8 ++---
 13 files changed, 416 insertions(+), 31 deletions(-)
```

### Evidence
(no evidence recorded)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
