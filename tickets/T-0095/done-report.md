## Done report

Design-first pass for milestone 0.1.0: docs/design/sprint-1.md is the
system design (data model, config, CLI, auth contracts, web routing,
per-acceptance-criterion test plan) for T-0006, T-0007, T-0008, T-0010,
T-0012, T-0015, T-0016, T-0017, T-0019, T-0020, T-0021, T-0023, T-0024,
T-0026, T-0028, T-0044; design/hullbreach.strata is the checked kernel
companion (nodes, flows, secrets for the same target architecture).

Evidence: cmd:grep -n 'module hullbreach_sprint1' design/hullbreach.strata
exit=0 sha256=4619336c0007 (design-kind work, no executable behavior to
bind pytest node ids to; confirms the strata file exists with its module
intact).

Filed: none.

Gates: frob check --ticket T-0095 clean except:
- gate:CROSSTICKET (2 errors) -- pre-existing: T-0003's own scope
  (tickets/**, itself flagged too broad by TICK009) is IN_PROGRESS and
  covers every tickets/ file, so any new ticket file reads as carrying
  T-0003's unfinished work. Reproduced against main before this ticket's
  changes; not this ticket's to fix.
- gate:SELFAUDIT (7 errors): 5 are REL200 on std.secrets' auto-generated
  "reads" flows (session_token/password_hash/database_url -> their
  audience) -- the secret_prop grammar has no waive slot (only node/store
  do), so these are mechanically undischargeable at this design stage
  (documented in section 9 of the design doc); 2 are SYS103 on
  tests/system/test_build.py and tests/unit/test_app.py, pre-existing
  (reproduced against main), unrelated to this ticket's scope.
- gate:TEST (1 error) -- pre-existing TEST003 on web/src/App.tsx,
  reproduced against main, unrelated to this ticket's scope.
- gate:FLAGCOV (1 unresolved) -- pre-existing, repo-wide unmeasured CLI
  surface, unrelated.

All REL200/REL201 findings on real declared nodes, all SYS111
capability-ratchet findings, all COV001/002, DOC001/006, REF001/002,
SCOPE001/002, and PRE001 findings this design introduced were discharged
(waive clauses in design/hullbreach.strata naming the ticket that will
resolve each, the capability-via-ratchet lock file, docs/index.md
linking, frob:ticket directives, and inline frob:waive DOC006 comments).
frob sys threats: no violations. frob coverage --full
--fail-on-degraded: clean. npx prettier --check .: clean. web
lint/tsc: clean (unaffected by this docs-only diff).

### Changed
```
 design/hullbreach.strata           | 179 ++++++++++
 docs/design/sprint-1.md            | 673 +++++++++++++++++++++++++++++++++++++
 tickets/T-0095/ticket.md           |  61 ++++
 tickets/T-draft-fe2e50bc/ticket.md |  36 ++
 4 files changed, 949 insertions(+)
```

### Evidence
- `cmd:grep -n 'module hullbreach_sprint1' design/hullbreach.strata exit=0 sha256=4619336c0007` (cmd evidence, exit=0)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: 5 error(s), 65 warning(s), 0 waived
- error-findings: CROSSTICKET001@tickets/T-0095/ticket.md, CROSSTICKET001@tickets/T-draft-fe2e50bc/ticket.md, SELFAUDIT001@design, SELFAUDIT001@tests/system/test_build.py, SELFAUDIT001@tests/unit/test_app.py
