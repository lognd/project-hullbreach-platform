import argparse
import sys

from dotenv import load_dotenv

from hullbreach_server.app import App, AppConfig


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hullbreach_server", description="Project Hullbreach platform API"
    )
    p.add_argument("--host", help="bind address (default: 127.0.0.1)")
    p.add_argument("--port", type=int, help="bind port (default: 8000)")
    sub = p.add_subparsers(dest="command")
    db_p = sub.add_parser("db", help="database maintenance")
    db_sub = db_p.add_subparsers(dest="db_command", required=True)
    db_sub.add_parser("upgrade", help="run pending Alembic migrations")
    db_sub.add_parser("seed", help="load catalog items and the first admin")
    return p


# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
def _db_upgrade() -> None:
    """Run every pending Alembic migration up to head (`db upgrade`)."""
    from alembic.config import main as alembic_main

    print("running alembic upgrade head", file=sys.stderr)
    alembic_main(["-c", "alembic.ini", "upgrade", "head"])


def _db_seed() -> None:
    """Load the catalog items and the first admin account (`db seed`)."""
    # frob:todo T-0008
    # db/seed.py::seed does not exist yet; T-0008 lands the real dispatch
    # (build an engine from AppConfig, open a session, call seed()).
    print("db seed is not implemented yet (T-0008)", file=sys.stderr)
    sys.exit(1)


# frob:tests tests/unit/test_main.py::test_main_prints_help_and_exits_cleanly
# frob:doc docs/index.md#public-api
def main() -> None:
    load_dotenv()
    args = _build_parser().parse_args()
    if args.command == "db":
        if args.db_command == "upgrade":
            _db_upgrade()
        elif args.db_command == "seed":
            _db_seed()
        return
    cfg = AppConfig.from_external(args)
    App(cfg)()


if __name__ == "__main__":
    main()
