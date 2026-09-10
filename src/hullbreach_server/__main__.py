import argparse

from dotenv import load_dotenv

from hullbreach_server.app import App, AppConfig


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hullbreach_server", description="Project Hullbreach platform API"
    )
    p.add_argument("--host", help="bind address (default: 127.0.0.1)")
    p.add_argument("--port", type=int, help="bind port (default: 8000)")
    return p


# frob:tests tests/unit/test_main.py::test_main_prints_help_and_exits_cleanly
# frob:doc docs/index.md#public-api
def main() -> None:
    load_dotenv()
    args = _build_parser().parse_args()
    cfg = AppConfig.from_external(args)
    App(cfg)()


if __name__ == "__main__":
    main()
