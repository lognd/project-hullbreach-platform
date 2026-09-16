## Done report

The Module 4 story map was filed as epics, stories and tickets T-0004..T-0094 in PR #4 (merged 2026-09-16). The ticket stayed in-progress with a tickets/** scope, which makes every later ticket's own ledger file look like T-0003 work (CROSSTICKET001), so it is closed here with the filing PR as its evidence.

### Changed
```
 .prettierignore                                    |   1 +
 design/hullbreach.strata                           | 411 ++++++++++++
 .../registry/capability-via-ratchet.lock.json      |  44 ++
 docs/design/sprint-1.md                            | 732 +++++++++++++++++++++
 docs/index.md                                      |  26 +
 frob-coverage.lock.json                            |   4 +-
 frob.toml                                          |   8 +
 pyproject.toml                                     |   2 +
 src/hullbreach_server/db/__init__.py               |  73 ++
 src/hullbreach_server/db/engine.py                 |  95 +++
 tests/system/test_build.py                         |  39 ++
 tests/unit/conftest.py                             |  81 +++
 tests/unit/test_api.py                             |  35 +
 tests/unit/test_auth_game.py                       |  75 +++
 tests/unit/test_auth_login.py                      | 156 +++++
 tests/unit/test_auth_logout.py                     |  95 +++
 tests/unit/test_auth_register.py                   | 111 ++++
 tests/unit/test_db_engine.py                       |  88 +++
 tests/unit/test_passwords.py                       |  55 ++
 tests/unit/test_roles.py                           | 129 ++++
 tests/unit/test_seed.py                            |  96 +++
 tests/unit/test_sessions.py                        | 227 +++++++
 tickets/T-0002/done-report.md                      | 149 +++++
 tickets/T-0002/ticket.md                           |  18 +-
 tickets/T-0003/ticket.md                           |  32 +
 tickets/T-0004/ticket.md                           |  44 ++
 tickets/T-0005/ticket.md                           |  55 ++
 tickets/T-0006/done-report.md                      |  83 +++
 tickets/T-0006/ticket.md                           | 160 +++++
 tickets/T-0007/ticket.md                           |  37 ++
 tickets/T-0008/ticket.md                           |  41 ++
 tickets/T-0009/ticket.md                           |  44 ++
 tickets/T-0010/ticket.md                           |  34 +
 tickets/T-0011/ticket.md                           |  40 ++
 tickets/T-0012/ticket.md                           |  39 ++
 tickets/T-0013/ticket.md                           |  55 ++
 tickets/T-0014/ticket.md                           |  55 ++
 tickets/T-0015/ticket.md                           |  37 ++
 tickets/T-0016/ticket.md                           |  42 ++
 tickets/T-0017/ticket.md                           |  34 +
 tickets/T-0018/ticket.md                           |  55 ++
 tickets/T-0019/ticket.md                           |  40 ++
 tickets/T-0020/ticket.md                           |  35 +
 tickets/T-0021/ticket.md                           |  34 +
 tickets/T-0022/ticket.md                           |  41 ++
 tickets/T-0023/ticket.md                           |  36 +
 tickets/T-0024/ticket.md                           |  33 +
 tickets/T-0025/ticket.md                           |  46 ++
 tickets/T-0026/ticket.md                           |  40 ++
 tickets/T-0027/ticket.md                           |  46 ++
 tickets/T-0028/ticket.md                           |  39 ++
 tickets/T-0029/ticket.md                           |  47 ++
 tickets/T-0030/ticket.md                           |  46 ++
 tickets/T-0031/ticket.md                           |  34 +
 tickets/T-0032/ticket.md                           |  32 +
 tickets/T-0033/ticket.md                           |  46 ++
 tickets/T-0034/ticket.md                           |  35 +
 tickets/T-0035/ticket.md                           |  33 +
 tickets/T-0036/ticket.md                           |  47 ++
 tickets/T-0037/ticket.md                           |  35 +
 tickets/T-0038/ticket.md                           |  33 +
 tickets/T-0039/ticket.md                           |  47 ++
 tickets/T-0040/ticket.md                           |  37 ++
 tickets/T-0041/ticket.md                           |  35 +
 tickets/T-0042/ticket.md                           |  42 ++
 tickets/T-0043/ticket.md                           |  44 ++
 tickets/T-0044/ticket.md                           |  37 ++
 tickets/T-0045/ticket.md                           |  44 ++
 tickets/T-0046/ticket.md                           |  33 +
 tickets/T-0047/ticket.md                           |  44 ++
 tickets/T-0048/ticket.md                           |  32 +
 tickets/T-0049/ticket.md                           |  34 +
 tickets/T-0050/ticket.md                           |  55 ++
 tickets/T-0051/ticket.md                           |  53 ++
 tickets/T-0052/ticket.md                           |  35 +
 tickets/T-0053/ticket.md                           |  36 +
 tickets/T-0054/ticket.md                           |  36 +
 tickets/T-0055/ticket.md                           |  49 ++
 tickets/T-0056/ticket.md                           |  34 +
 tickets/T-0057/ticket.md                           |  34 +
 tickets/T-0058/ticket.md                           |  43 ++
 tickets/T-0059/ticket.md                           |  34 +
 tickets/T-0060/ticket.md                           |  32 +
 tickets/T-0061/ticket.md                           |  43 ++
 tickets/T-0062/ticket.md                           |  34 +
 tickets/T-0063/ticket.md                           |  32 +
 tickets/T-0064/ticket.md                           |  48 ++
 tickets/T-0065/ticket.md                           |  49 ++
 tickets/T-0066/ticket.md                           |  35 +
 tickets/T-0067/ticket.md                           |  34 +
 tickets/T-0068/ticket.md                           |  33 +
 tickets/T-0069/ticket.md                           |  43 ++
 tickets/T-0070/ticket.md                           |  37 ++
 tickets/T-0071/ticket.md                           |  48 ++
 tickets/T-0072/ticket.md                           |  35 +
 tickets/T-0073/ticket.md                           |  34 +
 tickets/T-0074/ticket.md                           |  50 ++
 tickets/T-0075/ticket.md                           |  54 ++
 tickets/T-0076/ticket.md                           |  34 +
 tickets/T-0077/ticket.md                           |  36 +
 tickets/T-0078/ticket.md                           |  33 +
 tickets/T-0079/ticket.md                           |  45 ++
 tickets/T-0080/ticket.md                           |  34 +
 tickets/T-0081/ticket.md                           |  34 +
 tickets/T-0082/ticket.md                           |  46 ++
 tickets/T-0083/ticket.md                           |  34 +
 tickets/T-0084/ticket.md                           |  33 +
 tickets/T-0085/ticket.md                           |  41 ++
 tickets/T-0086/ticket.md                           |  47 ++
 tickets/T-0087/ticket.md                           |  37 ++
 tickets/T-0088/ticket.md                           |  43 ++
 tickets/T-0089/ticket.md                           |  36 +
 tickets/T-0090/ticket.md                           |  44 ++
 tickets/T-0091/ticket.md                           |  38 ++
 tickets/T-0092/ticket.md                           |  32 +
 tickets/T-0093/ticket.md                           |  40 ++
 tickets/T-0094/ticket.md                           |  36 +
 tickets/T-0095/done-report.md                      |  60 ++
 tickets/T-0095/ticket.md                           |  77 +++
 tickets/T-0097/done-report.md                      |  70 ++
 tickets/T-0097/ticket.md                           | 167 +++++
 tickets/T-0098/done-report.md                      |  55 ++
 tickets/T-0098/ticket.md                           |  70 ++
 tickets/T-0099/ticket.md                           |  30 +
 ty.toml                                            |  10 +
 uv.lock                                            | 193 ++++++
 126 files changed, 7345 insertions(+), 4 deletions(-)
```

### Evidence
(no evidence recorded)

### Captured claims
- tests: 0 passed (from 0 evidence id(s))
- gates: unmeasured (no parsable gate-summary from a fresh check)
