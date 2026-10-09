+++
id = "01M4GR0GC074Y7KQAZQ8W2CV9Y"
title = "App.__call__ checks one database but the served app uses another (cfg.database_url ignored by get_engine)"
type = "bug"
category = "todo"
priority = "high"
reporter = "lognd"
created = "2026-10-09T16:30:15Z"
updated = "2026-10-09T16:30:15Z"
labels = ["origin:auditor"]
scope = ["src/hullbreach_server/app/app.py"]

[[acceptance]]
text = "Engine used by get_db derives from the cfg passed to create_app/App"
bound = false
+++

src/hullbreach_server/app/app.py:63-70. App.__call__ runs check_connectivity against create_db_engine(self._cfg.database_url), then serves create_app(self._cfg). But request-time sessions come from db.get_engine() (db/__init__.py:~53) which rebuilds config via AppConfig.from_external(argparse.Namespace()) and ignores app.state.cfg. Any App(cfg) whose database_url differs from env/pyproject/cwd (tests, embedders) passes the fail-fast check yet serves against a different DB: wrong-but-not-erroring. The startup engine is also never disposed. Contract: the database that is checked must be the database that is served. Fix: create_app should build/own the engine from cfg.database_url (store on app.state, or set the db module engine from cfg) and App.__call__ should reuse that same engine and dispose it on exit; add an integration test with a non-default cfg.
