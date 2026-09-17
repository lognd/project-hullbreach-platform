## Done report

Implemented T-0021 per docs/design/sprint-1.md sec.5 (login endpoint
contract) and sec.6 (session persistence / inline validation errors).
web/src/auth/session.ts already existed in full from T-0044 (saveSession/
loadSession/clearSession/useSession) -- no extension was needed, since
its StoredSession shape (token/userId/username/role) already matches
what login() returns.

web/src/pages/Login.tsx is the second caller of web/src/api/auth.ts's
login(): on success it builds a StoredSession from the LoginResponse
(token, and userId/username/role from its user) and calls saveSession,
then navigates home. useSession reading the same localStorage key back
on mount is what satisfies the "signed in after reload" acceptance
criterion. Any ApiError (401 invalid credentials, 429 rate-limited)
sets a role="alert" form-level banner with the server's detail message
-- login has no field-level errors, since the contract never names a
field. web/src/router.tsx's /login route now renders the real Login
component instead of T-0044's placeholder.

Flipped the remaining 6 it.fails tests in web/tests/unit/Login.test.tsx
(the "Login page" describe block) to it; the earlier "auth/session.ts"
block (T-0044) was already passing.

Removed the WIRE001 waiver on login() in web/src/api/auth.ts now that
Login.tsx is a real production call site, and added a frob:tests
citation to Login.test.tsx alongside the existing Register.test.tsx one.

Scope was extended (via `frob ticket scope --add`, each with a recorded
reason) to web/src/router.tsx (wire the real Login page into the
existing /login route), docs/index.md (new paragraph in the existing
"Auth API client and the register page" section), and web/src/api/auth.ts
(the WIRE001 removal above).

No strata/capability changes needed this time: web/src/api/auth.ts
already carries the browser node's fetch_url grant from T-0017, and
login() is in that same file, so no new SELFAUDIT001 finding appeared.
docs/index.md was free when requested; design/hullbreach.strata was not
touched.

All web gates are green: npm run lint, npx prettier --check ., npx tsc
--noEmit, npx vitest run (34 passed, 2 expected fail -- T-0024's own
untouched logout-behavior tests), npm run build, uv run crunk check, uv
run crunk tokens --check, frob test --base main. `frob check --ticket
T-0021` reports 0 errors.

### Changed
```
 tickets/T-0021/ticket.md | 29 +++++++++++++++++++++++++++--
 1 file changed, 27 insertions(+), 2 deletions(-)
```

### Evidence
- `web/tests/unit/Login.test.tsx::Login page > keeps user signed in after reload` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 1 passed (from 1 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
