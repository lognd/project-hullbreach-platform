---
id: T-0019
title: Session model with expiry and revocation, and the current-user auth dependency
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0018
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- src/hullbreach_server/db/models/session.py
- src/hullbreach_server/auth/sessions.py
- src/hullbreach_server/auth/deps.py
- tests/unit/test_sessions.py
- src/hullbreach_server/db/models/__init__.py
- src/hullbreach_server/db/migrations/versions/*.py
- .env.example
- docs/index.md
- design/hullbreach.strata
- docs/design/sprint-1.md
- docs/design/registry/capability-via-ratchet.lock.json
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: src/hullbreach_server/db/models/__init__.py
  reason: Session must be re-exported here so Base.metadata (and Alembic autogenerate)
    sees it, per env.py's own comment naming T-0019
  actor: logan
  at: '2026-09-16'
- op: add
  glob: src/hullbreach_server/db/migrations/versions/*.py
  reason: session migration file lives under versions/, needed to create the sessions
    table
  actor: logan
  at: '2026-09-16'
- op: add
  glob: .env.example
  reason: documents HULLBREACH_SESSION_TTL_SECONDS per docs/design/sprint-1.md section
    3, brief-allowed config exception
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: add frob:doc anchors for the new Session/sessions.py/deps.py public API,
    re-point the REL200 waivers off T-0019 to their real successors, add the SYS100
    env.read capability on hullbreach_server_auth and the auth->logging Flow
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: add frob:doc anchors for the new Session/sessions.py/deps.py public API,
    re-point the REL200 waivers off T-0019 to their real successors, add the SYS100
    env.read capability on hullbreach_server_auth and the auth->logging Flow
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/sprint-1.md
  reason: AFFECT001 on the new f_auth_to_logging flow needs its section-9 doc touched,
    and SELFAUDIT001/SYS111's env.read ratchet on hullbreach_server_auth needs raising
    to 1 with a reason
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: AFFECT001 on the new f_auth_to_logging flow needs its section-9 doc touched,
    and SELFAUDIT001/SYS111's env.read ratchet on hullbreach_server_auth needs raising
    to 1 with a reason
  actor: logan
  at: '2026-09-16'
evidence:
- tests/unit/test_sessions.py::test_expired_token_returns_401
- tests/unit/test_sessions.py::test_revoked_token_returns_401
designated_repro_test: null
acceptance:
- text: given an expired or revoked token, when a protected route is called, then
    401
  evidence:
  - tests/unit/test_sessions.py::test_expired_token_returns_401
  - tests/unit/test_sessions.py::test_revoked_token_returns_401
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---

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
docs/index.md (public-api + database-migrations sections)
design/hullbreach.strata (env.read capability, f_auth_to_logging flow,
  re-pointed REL200 waivers: f_api_to_auth/session_token__issue/
  f_session_token_to_browser -> T-0020, session_token__revoke -> T-0023,
  f_auth_to_db -> T-0100)
docs/design/sprint-1.md (section 9 note for f_auth_to_logging + env.read)
docs/design/registry/capability-via-ratchet.lock.json
  (hullbreach_server_auth::env.read accepted_count 1)

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

Gates: frob check --ticket T-0019 clean, 0 errors (gate:AFFECT, gate:SCOPE,
gate:SELFAUDIT, gate:SYS, gate:REF, gate:WIRE, gate:TEST, gate:LANDPARITY,
gate:PRE all pass). ruff, ruff format, ty, typani.lint, full pytest and
vitest suites all clean. Migration files' WIRE001 follow_up re-pointed
from T-0019 to T-0020 so closing doesn't leave a dangling tracker.
Waivers: REF002 on the sessions migration (single-anchor leaf, same
shape as the pre-existing migrations); WIRE001 on issue_session,
get_current_user, revoke_session, revoke_all_sessions,
_UTCDateTime.process_result_value, and the migration upgrade/downgrade
(no route wires session issuance/revocation yet -- T-0020/T-0023
follow-ups); TEST001 on _UTCDateTime.process_result_value (SQLAlchemy's
own TypeDecorator interface, exercised indirectly by every Session
round-trip test).
