## Done report

Documents the intended main branch protection: PR-only, one approving review, all three CI checks required by name (server (python), web (typescript), frob check), Scrum Master on the ruleset bypass list, merge by merge commit as practiced. Also fixes stale prose describing a nonexistent combined 'All checks pass' job and a squash/rebase policy not actually followed. The GitHub ruleset itself is unchanged (owner's call); ticket kind changed feature->docs since the acceptance criterion is a UI setting with no test node id, and cmd evidence (gh api repos/lognd/project-hullbreach-platform/rules/branches/main) verifies the actual current ruleset state.

### Changed
```
 CONTRIBUTING.md               | 20 ++++++++++++--------
 README.md                     | 15 ++++++++++-----
 tickets/T-0010/done-report.md | 16 ++++++++++++++++
 tickets/T-0010/ticket.md      | 21 ++++++++++++++++++---
 4 files changed, 56 insertions(+), 16 deletions(-)
```

### Evidence
- `cmd:gh api repos/lognd/project-hullbreach-platform/rules/branches/main exit=0 sha256=df8956df9a54` (cmd evidence, exit=0)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
