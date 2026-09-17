## Done report

Changed:
src/hullbreach_server/db/models/session.py::Session
src/hullbreach_server/db/models/session.py::_UTCDateTime
src/hullbreach_server/db/models/__init__.py (re-export Session)
src/hullbreach_server/auth/sessions.py::issue_session
src/hullbreach_server/auth/sessions.py::resolve_session
src/hullbreach_server/auth/sessions.py::revoke_session
src/hullbreach_server/auth/sessions.py::revoke_all_sessions
src/hullbreach_server/auth/sessions.py::SessionError
src/hullbreach_server/auth/deps.py::get_current_user
src/hullbreach_server/auth/deps.py::AuthContext
src/hullbreach_server/db/migrations/versions/550676f68926_create_sessions_table.py
.env.example (HULLBREACH_SESSION_TTL_SECONDS)

Evidence:
tests/unit/test_sessions.py::test_issue_session_returns_row_and_plaintext_token_once
tests/unit/test_sessions.py::test_issue_session_stores_sha256_hash_of_token
tests/unit/test_sessions.py::test_issue_session_sets_expiry_from_default_ttl
tests/unit/test_sessions.py::test_resolve_session_succeeds_for_a_valid_token
tests/unit/test_sessions.py::test_resolve_session_fails_for_an_expired_token
tests/unit/test_sessions.py::test_resolve_session_fails_for_a_revoked_token
tests/unit/test_sessions.py::test_revoke_session_sets_revoked_at
tests/unit/test_sessions.py::test_revoke_all_sessions_revokes_every_non_revoked_session_for_user
tests/unit/test_sessions.py::test_expired_token_returns_401
tests/unit/test_sessions.py::test_revoked_token_returns_401
tests/unit/test_sessions.py::test_missing_authorization_header_returns_401_not_403
tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata (sessions migration)

Filed: none

Gates: frob check --ticket T-0019 clean except gate:AFFECT, gate:SELFAUDIT,
gate:SYS -- all three require edits to docs/index.md and/or
design/hullbreach.strata (the frob:doc anchors, the SYS100 env.read
capability declaration on hullbreach_server_auth, and the missing
auth-to-logging Flow), both of which are held under T-0044's live
cross-worktree lease for the duration of this ticket. gate:PRE,
gate:LANDPARITY, gate:WIRE, gate:TEST, gate:SCOPE, ruff, ty, and the full
pytest/vitest suites are clean. Per the coordinator's dispatch
instructions, this is reported rather than worked around with --steal.
