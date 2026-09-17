## Done report

Changed:
src/hullbreach_server/api/auth.py::logout
src/hullbreach_server/api/auth.py::session
src/hullbreach_server/auth/schemas.py::SessionInfo
docs/index.md (Auth API section extended for logout/session)
design/hullbreach.strata (REL200 waivers re-pointed to T-0100:
  session_token__revoke, f_session_check, f_session_token_to_game_server)

Evidence:
tests/unit/test_auth_logout.py::test_logout_returns_204
tests/unit/test_auth_logout.py::test_logout_revokes_token_so_it_is_rejected_afterward
tests/unit/test_auth_logout.py::test_logout_without_all_only_revokes_the_presented_session
tests/unit/test_auth_logout.py::test_logout_with_all_true_revokes_every_session
tests/unit/test_auth_logout.py::test_logout_with_already_invalid_token_returns_401

Filed: none

Gates: frob check --base origin/main --ticket T-0023 clean, 0 errors.
ruff, ruff format, ty, full pytest (72 passed, 3 xfailed), frob coverage
--fail-on-degraded all clean.

Notes (read before starting T-0026):
- tests/unit/test_auth_logout.py's own revocation checks (3 of its 5
  tests) needed a protected endpoint to prove a token is now rejected,
  and GET /api/v1/auth/session was the only one specified anywhere
  (design section 5) -- but that route is T-0026's declared scope, not
  T-0023's. Rather than block or rewrite the pre-written test bodies,
  T-0023 scope-added auth/schemas.py and tests/unit/test_auth_game.py
  (reason recorded in the scope-change log) and implemented the
  minimal GET /session (SessionInfo schema + route via get_current_user,
  matching web/src/api/auth.ts's SessionInfo/fetchSession contract
  exactly) needed to make its own tests runnable. This trivially
  satisfies 3 of T-0026's 4 xfail tests in test_auth_game.py
  (player_id/role for a valid token, 401 missing token, 401 malformed
  token -- all three follow directly from reusing get_current_user), so
  those three markers were dropped; the fourth
  (test_session_endpoint_omits_username_and_email) was already dropped
  by T-0020 for the same reason.
- T-0026's remaining real scope is now just the game-client login path
  ("Bearer-token login for the game client") plus any docs/strata work
  that ticket still wants to do on top of what's landed here -- its
  GET /session acceptance criterion is already met. Flagging this for
  the coordinator since T-0026's ticket body/scope may want updating
  before it's picked up.
- Waived WIRE001 on logout: it is already called from
  web/src/components/Header.tsx via api/auth.ts's logout() (T-0024,
  merged), but this Python-only gate cannot trace the cross-language
  call site.
