from __future__ import annotations

import argparse
import os
import tomllib
from pathlib import Path

from pydantic import BaseModel, SecretStr

_ENV_PREFIX = "HULLBREACH_"
# Fields whose environment value is a comma-separated list.
_LIST_FIELDS = frozenset({"cors_origins", "game_server_api_keys"})


# frob:tests tests/unit/test_app.py::test_app_config_from_external_with_no_config_file
# frob:doc docs/index.md#public-api
class AppConfig(BaseModel):
    """Runtime configuration for the platform API.

    Precedence (lowest to highest): defaults here, `[tool.hullbreach_server]`
    in pyproject.toml, `HULLBREACH_*` environment variables, CLI flags.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = "postgresql://hullbreach:hullbreach@localhost:5432/hullbreach"
    cors_origins: list[str] = ["http://localhost:5173"]
    # Keys a game server presents in X-Server-Key (T-0052); empty means no
    # server can authenticate. Secret values: never logged or repr'd.
    game_server_api_keys: list[SecretStr] = []

    @classmethod
    def from_external(
        cls, args: argparse.Namespace, config_file: Path | None = None
    ) -> AppConfig:
        # frob:doc docs/index.md#public-api
        file_cfg: dict = {}
        # Defaults to pyproject.toml in cwd; pass an explicit path to override
        resolved = config_file if config_file is not None else Path("pyproject.toml")
        if resolved.exists():
            with resolved.open("rb") as f:
                data = tomllib.load(f)
            file_cfg = data.get("tool", {}).get("hullbreach_server", {})

        env_cfg: dict = {}
        for field in cls.model_fields:
            raw = os.environ.get(f"{_ENV_PREFIX}{field.upper()}")
            if raw is None:
                continue
            env_cfg[field] = raw.split(",") if field in _LIST_FIELDS else raw

        cli_cfg = {
            k: v
            for k, v in vars(args).items()
            if k in cls.model_fields and v is not None
        }

        return cls(**{**file_cfg, **env_cfg, **cli_cfg})
