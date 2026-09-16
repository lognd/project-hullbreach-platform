## Done report

Merged as PR #1. The platform monorepo is scaffolded: FastAPI server with AppConfig, house logging and the health route; React/Vite web app with the crunk design system; frob and crunk gates wired into a PR-gated CI workflow; README and CONTRIBUTING. Every gate is green on main.

### Changed
```
 tickets/T-0001/done-report.md | 17 +++++++++++++++++
 tickets/T-0001/ticket.md      | 13 +++++++++++--
 tickets/T-0002/ticket.md      | 33 +++++++++++++++++++++++++++++++++
 3 files changed, 61 insertions(+), 2 deletions(-)
```

### Evidence
- `tests/system/test_build.py::test_package_imports` (pytest node id, verified passing when recorded)
- `tests/system/test_build.py::test_cli_help` (pytest node id, verified passing when recorded)
- `tests/system/test_build.py::test_app_builds_and_serves_health` (pytest node id, verified passing when recorded)
- `tests/unit/test_api.py::test_health_reports_ok_and_version` (pytest node id, verified passing when recorded)

### Captured claims
- tests: 4 passed (from 4 evidence id(s))
- gates: 0 error(s), 25 warning(s), 0 waived
- error-findings: none (measured, zero errors)
