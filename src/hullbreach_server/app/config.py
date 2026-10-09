from __future__ import annotations

import argparse
import os
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, SecretStr, ValidationError, field_validator
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_ENV_PREFIX = "HULLBREACH_"
# Names the config file explicitly, overriding the upward pyproject.toml search.
_CONFIG_ENV_VAR = "HULLBREACH_CONFIG"
_CONFIG_FILE_NAME = "pyproject.toml"
_CONFIG_TABLE = "hullbreach_server"
# Fields whose environment value is a comma-separated list.
_LIST_FIELDS = frozenset({"cors_origins", "game_server_api_keys"})


# frob:tests tests/unit/test_app.py::test_from_external_returns_err_for_a_bad_port
# frob:doc docs/index.md#public-api
class ConfigError(BaseModel):
    """A log-safe configuration failure: names the offending key, never its value."""

    model_config = {}

    message: str

    def __str__(self) -> str:
        return self.message


# frob:tests tests/unit/test_app.py::test_app_config_from_external_with_no_config_file
# frob:doc docs/index.md#public-api
class AppConfig(BaseModel):
    """Runtime configuration for the platform API.

    Precedence (lowest to highest): defaults here, `[tool.hullbreach_server]`
    in pyproject.toml, `HULLBREACH_*` environment variables, CLI flags.
    Unknown keys are rejected, and `database_url` has no default so no
    well-known credential can be used by accident (INV-005).
    """

    model_config = ConfigDict(extra="forbid")

    host: str = "127.0.0.1"
    port: int = 8000
    # frob:invariant INV-005
    database_url: str
    cors_origins: list[str] = ["http://localhost:5173"]
    # Keys a game server presents in X-Server-Key (T-0052); empty means no
    # server can authenticate. Secret values: never logged or repr'd.
    game_server_api_keys: list[SecretStr] = []

    # frob:invariant INV-004
    @field_validator("cors_origins")
    @classmethod
    def _validate_cors_origins(cls, origins: list[str]) -> list[str]:
        """Allow only explicit http(s) origins: credentialed CORS never takes a wildcard."""  # noqa: E501
        for origin in origins:
            parts = urlsplit(origin)
            if (
                parts.scheme not in ("http", "https")
                or not parts.netloc
                or parts.path not in ("", "/")
                or parts.query
                or parts.fragment
            ):
                raise ValueError(
                    "each origin must be an explicit http(s) origin such as "
                    "https://example.com (no wildcard, path or query)"
                )
        return [origin.rstrip("/") for origin in origins]

    @classmethod
    def from_external(
        cls, args: argparse.Namespace, config_file: Path | None = None
    ) -> Result[AppConfig, ConfigError]:
        # frob:doc docs/index.md#public-api
        """Build the config from file, environment and CLI flags.

        Returns Err(ConfigError) for an unreadable or malformed config file,
        or for any invalid or unknown key (the message names the key, never
        a value, so a database URL password cannot leak into logs).
        The config file is `config_file`, else $HULLBREACH_CONFIG, else the
        nearest pyproject.toml above the cwd that has a
        [tool.hullbreach_server] table; which one was used is logged.
        """
        file_result = _load_file_config(config_file)
        if file_result.is_err:
            return Err(file_result.danger_err)

        env_cfg: dict = {}
        for field in cls.model_fields:
            raw = os.environ.get(f"{_ENV_PREFIX}{field.upper()}")
            if raw is None:
                continue
            env_cfg[field] = _split_list(raw) if field in _LIST_FIELDS else raw

        cli_cfg = {
            k: v
            for k, v in vars(args).items()
            if k in cls.model_fields and v is not None
        }

        try:
            return Ok(cls(**{**file_result.danger_ok, **env_cfg, **cli_cfg}))
        except ValidationError as exc:
            detail = "; ".join(
                f"{'.'.join(str(p) for p in e['loc']) or 'config'}: {e['msg']}"
                for e in exc.errors()
            )
            _log.error("invalid configuration: %s", detail)
            return Err(ConfigError(message=f"invalid configuration: {detail}"))


def _split_list(raw: str) -> list[str]:
    """Split a comma-separated env value, stripping whitespace and dropping empties."""
    return [item.strip() for item in raw.split(",") if item.strip()]


def _find_config_file(start: Path) -> Path | None:
    """Nearest pyproject.toml at or above `start` that has a [tool.hullbreach_server] table."""  # noqa: E501
    for directory in (start, *start.parents):
        candidate = directory / _CONFIG_FILE_NAME
        if not candidate.is_file():
            continue
        try:
            with candidate.open("rb") as f:
                table = tomllib.load(f).get("tool", {}).get(_CONFIG_TABLE)
        except (OSError, tomllib.TOMLDecodeError):
            continue
        if table is not None:
            return candidate
    return None


def _load_file_config(config_file: Path | None) -> Result[dict, ConfigError]:
    """Locate and parse the file layer of the config; {} when there is none."""
    explicit = config_file
    if explicit is None and _CONFIG_ENV_VAR in os.environ:
        explicit = Path(os.environ[_CONFIG_ENV_VAR])
    if explicit is not None:
        # An explicitly named file that is missing is not an error: callers
        # (and tests) pass a path to mean "this, or nothing".
        resolved: Path | None = explicit if explicit.exists() else None
    else:
        resolved = _find_config_file(Path.cwd())

    if resolved is None:
        _log.info("config: no %s file used", _CONFIG_FILE_NAME)
        return Ok({})
    try:
        with resolved.open("rb") as f:
            data = tomllib.load(f)
    except OSError as exc:
        _log.error("config: cannot read %s (%s)", resolved, type(exc).__name__)
        return Err(ConfigError(message=f"cannot read config file {resolved}"))
    except tomllib.TOMLDecodeError as exc:
        _log.error("config: %s is not valid TOML", resolved)
        return Err(
            ConfigError(message=f"config file {resolved} is not valid TOML: {exc}")
        )
    _log.info("config: using %s", resolved)
    table = data.get("tool", {}).get(_CONFIG_TABLE, {})
    if not isinstance(table, dict):
        return Err(
            ConfigError(message=f"[tool.{_CONFIG_TABLE}] in {resolved} must be a table")
        )
    return Ok(table)
