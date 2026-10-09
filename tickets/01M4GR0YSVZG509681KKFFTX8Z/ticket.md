+++
id = "01M4GR0YSVZG509681KKFFTX8Z"
title = "get_engine/get_sessionmaker: unsynchronized lazy globals and config re-read diverge from the cfg given to App/create_app"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-09T16:30:30Z"
updated = "2026-10-09T17:11:12Z"
labels = ["origin:auditor", "audit:db"]
scope = ["src/hullbreach_server/db/__init__.py"]

[[acceptance]]
text = "given an App config, when it serves, then requests use the engine it health-checked, built once even under concurrent first use, and dispose resets it"
bound = true
+++

db/__init__.py:39-69 (get_engine, get_sessionmaker) vs app/app.py:59-66 and :17-34. (1) get_engine rebuilds config via AppConfig.from_external(argparse.Namespace()) (db/__init__.py:55), ignoring the AppConfig passed to create_app(cfg)/App(cfg); App.__call__ connectivity-checks its own engine from cfg.database_url, then serves requests through a different, global engine from a re-read config, so a cfg built programmatically or with a differing config source checks one DB and serves another. (2) The check-then-set globals are not locked while sync FastAPI endpoints run in a threadpool, so concurrent first requests can build two engines/sessionmakers and leak a connection pool. (3) No dispose/reset hook, so tests and __main__._db_seed (__main__.py:37) never dispose the engine. Fix: build the engine once from cfg in create_app (store on app.state, get_db reads request.app.state), or guard init with a lock and expose an explicit reset/dispose; stop re-parsing config inside db.
