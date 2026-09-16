---
id: T-0044
title: Router, page shell, header and footer components with signed-in and signed-out
  states
state: in-progress
kind: feature
origin: human
created: '2026-09-15'
priority: medium
parent: T-0043
tier: ticket
sprint: sprint-1
runs_last: false
milestone: 0.1.0
runs_last_parallel_safe: false
runs_last_parallel_safe_reason: null
scope:
- web/src/App.tsx
- web/src/components/Header.tsx
- web/src/components/Footer.tsx
- web/src/router.tsx
- web/tests/unit/Header.test.tsx
- web/src/auth/session.ts
- web/src/main.tsx
- web/tests/unit/App.test.tsx
- web/tests/unit/Login.test.tsx
- package.json
- package-lock.json
- frob.toml
- design/hullbreach.strata
- docs/design/registry/capability-via-ratchet.lock.json
- docs/index.md
scope_breadth_ack: false
scope_breadth_ack_reason: null
no_scope_declared: false
no_scope_declared_reason: null
scope_changes:
- op: add
  glob: web/src/auth/session.ts
  reason: router.tsx needs createBrowserRouter wired into main.tsx to replace the
    bare App render, and Header's signed-in state requires the useSession/saveSession/clearSession
    shape design/sprint-1.md sec.6 puts in auth/session.ts; T-0021 (already scoped
    to this same file) fills in Login.tsx's usage and reload-persistence coverage
    on top of this shape
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/src/main.tsx
  reason: router.tsx needs createBrowserRouter wired into main.tsx to replace the
    bare App render, and Header's signed-in state requires the useSession/saveSession/clearSession
    shape design/sprint-1.md sec.6 puts in auth/session.ts; T-0021 (already scoped
    to this same file) fills in Login.tsx's usage and reload-persistence coverage
    on top of this shape
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/tests/unit/App.test.tsx
  reason: App.tsx's job changed from rendering landing content to being the page shell
    (Header/Outlet/Footer) per design/sprint-1.md sec.6; the pre-existing scaffold
    smoke test asserted the old content and must be updated to match, not left asserting
    something now false
  actor: logan
  at: '2026-09-16'
- op: add
  glob: web/tests/unit/Login.test.tsx
  reason: web/src/auth/session.ts's own shape (saveSession/loadSession/clearSession/useSession)
    is fully implemented by T-0044 (needed by Header's signed-in state) and Login.test.tsx's
    'auth/session.ts' describe block tests exactly that shape in isolation from the
    Login page; flipping just those 4 to it, leaving the 6 'Login page' tests (which
    need pages/Login.tsx, T-0021's own file) untouched and failing
  actor: logan
  at: '2026-09-16'
- op: add
  glob: package.json
  reason: react-router-dom dependency addition needed for router.tsx (createBrowserRouter/RouterProvider),
    per docs/design/sprint-1.md sec.6
  actor: logan
  at: '2026-09-16'
- op: add
  glob: package-lock.json
  reason: react-router-dom dependency addition needed for router.tsx (createBrowserRouter/RouterProvider),
    per docs/design/sprint-1.md sec.6
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: documenting the new router/Header/Footer/session shell in the same change,
    per the doc-as-you-go convention; adding frob:doc anchors above the new public
    symbols
  actor: logan
  at: '2026-09-16'
- op: add
  glob: frob.toml
  reason: workaround for frob 0.531.0's LANGUAGE_COLLECTORS keying vitest tests as
    language=ts while frob.toml/frob test use typescript, which otherwise blocks frob
    ticket evidence/close on any vitest node id; mirrors the existing typescript runner
    entry (coordinator-approved workaround)
  actor: logan
  at: '2026-09-16'
- op: remove
  glob: docs/index.md
  reason: yielding docs/index.md to break a lease deadlock with T-0099 (T-0099 holds
    design/hullbreach.strata and needs docs/index.md; T-0044 held docs/index.md and
    needs the strata file); patch kept at scratchpad/t0044-docs.patch to re-apply
    once T-0099 lands
  actor: logan
  at: '2026-09-16'
- op: add
  glob: design/hullbreach.strata
  reason: web/src/auth/session.ts (T-0044) uses window.localStorage in production
    code; the browser node's capability declaration must grant client_storage via
    that real file, or SELFAUDIT001 flags an undeclared observed capability
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/design/registry/capability-via-ratchet.lock.json
  reason: 'SYS111 ratchet: browser node''s client_storage via-list grew from 0 to
    1 site (web/src/auth/session.ts) with T-0044''s may declaration; raising accepted_count
    in the same diff per the ratchet''s own requirement'
  actor: logan
  at: '2026-09-16'
- op: add
  glob: docs/index.md
  reason: re-adding after T-0099 landed and freed the lease deadlock; re-applying
    T-0044's own docs section
  actor: logan
  at: '2026-09-16'
evidence:
- web/tests/unit/Header.test.tsx::Header keyboard access > tab order matches visual
  order and Enter activates each control
designated_repro_test: null
acceptance:
- text: given the header, when tabbing through, then focus order matches visual order
    and every control activates with Enter
  evidence:
  - web/tests/unit/Header.test.tsx::Header keyboard access > tab order matches visual
    order and Enter activates each control
threat: null
component: null
anchor: false
anchor_reason: null
land_commit: null
---
