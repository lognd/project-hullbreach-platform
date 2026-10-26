"""Saved ship designs (S35), per docs/index.md#ship-designs.

A design is the game's BlockGridDesign JSON (FormatVersion, MaxBlocks,
MaxJsonChars in game/.../Hullbreach.Net/BlockGridDesign.cs); the limits are
mirrored here and every save is validated before it is stored.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.design import ShipDesign
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger, log_event

_log = get_logger(__name__)

# Mirrors of BlockGridDesign.FormatVersion / MaxBlocks / MaxJsonChars.
FORMAT_VERSION = 1
MAX_BLOCKS = 4096
MAX_JSON_CHARS = 1 << 20
# BlockKey.Min / Max: the inclusive grid coordinate range.
GRID_MIN = -128
GRID_MAX = 127
# Nesting the game's parser accepts: {"blocks":[{...}]} is depth 3.
MAX_NESTING = 6
# Display-name bound and the per-player cap on saved designs.
MAX_NAME_CHARS = 64
MAX_DESIGNS_PER_USER = 50


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignBlock(BaseModel):
    """One placed block: grid cell, block type name and modifier byte."""

    model_config = ConfigDict(extra="forbid")

    x: int = Field(ge=GRID_MIN, le=GRID_MAX)
    y: int = Field(ge=GRID_MIN, le=GRID_MAX)
    type: str = Field(min_length=1, max_length=64)
    mods: int = Field(default=0, ge=0, le=255)


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignDocument(BaseModel):
    """The BlockGridDesign file: a format version and 1..MAX_BLOCKS blocks."""

    model_config = ConfigDict(extra="forbid")

    version: int
    blocks: list[DesignBlock] = Field(min_length=1, max_length=MAX_BLOCKS)


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignError(BaseModel):
    """Why a design operation failed; `kind` selects the HTTP status."""

    kind: Literal["invalid", "too_large", "unsupported_version", "not_found", "limit"]
    detail: str
    field: str | None = None


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignOut(BaseModel):
    """A stored design as the API returns it, including the design JSON object."""

    id: uuid.UUID
    name: str
    format_version: int
    design: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignSummary(BaseModel):
    """A row of the player's design list: no design body."""

    id: uuid.UUID
    name: str
    format_version: int
    block_count: int
    updated_at: datetime


def _depth(value: object) -> int:
    """Nesting depth of a parsed JSON value (a scalar is 0, an empty list 1)."""
    if isinstance(value, dict):
        return 1 + max((_depth(v) for v in value.values()), default=0)
    if isinstance(value, list):
        return 1 + max((_depth(v) for v in value), default=0)
    return 0


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_validate_design_rejects_each_bad_shape
# noqa: E501  # frob:tests tests/unit/test_designs.py::test_oversized_design_returns_413_naming_the_limit
# frob:tests tests/unit/test_designs.py::test_wrong_format_version_returns_422
def validate_design(design: dict[str, Any]) -> Result[str, DesignError]:
    """Check `design` against the BlockGridDesign limits; Ok is its JSON text."""
    text = json.dumps(design, separators=(",", ":"), ensure_ascii=False)
    if len(text) > MAX_JSON_CHARS:
        return Err(
            DesignError(
                kind="too_large",
                field="design",
                detail=f"design is larger than {MAX_JSON_CHARS} characters",
            )
        )
    if _depth(design) > MAX_NESTING:
        return Err(
            DesignError(
                kind="invalid", field="design", detail="design is nested too deeply"
            )
        )
    version = design.get("version")
    if type(version) is not int or version != FORMAT_VERSION:
        return Err(
            DesignError(
                kind="unsupported_version",
                field="design.version",
                detail=(
                    "unsupported design version "
                    f"(this server reads version {FORMAT_VERSION})"
                ),
            )
        )
    try:
        doc = DesignDocument.model_validate(design)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(p) for p in first["loc"])
        return Err(
            DesignError(
                kind="invalid",
                field=f"design.{where}" if where else "design",
                detail=f"design.{where}: {first['msg']}" if where else first["msg"],
            )
        )
    seen: set[tuple[int, int]] = set()
    for block in doc.blocks:
        if (block.x, block.y) in seen:
            return Err(
                DesignError(
                    kind="invalid",
                    field="design.blocks",
                    detail=f"two blocks overlap at {block.x},{block.y}",
                )
            )
        seen.add((block.x, block.y))
    return Ok(text)


def _not_found() -> DesignError:
    """The one error for a missing design or one owned by someone else."""
    return DesignError(kind="not_found", detail="design not found")


def _owned(db: DBSession, user: User, design_id: uuid.UUID) -> ShipDesign | None:
    """The design `design_id` if `user` owns it, else None (never reveals others')."""
    row = db.get(ShipDesign, design_id)
    if row is None or row.user_id != user.id:
        return None
    return row


def _out(row: ShipDesign) -> DesignOut:
    """Build the API shape from a stored row."""
    return DesignOut(
        id=row.id,
        name=row.name,
        format_version=row.format_version,
        design=json.loads(row.design_json),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_list_returns_only_my_designs
def list_designs(db: DBSession, user: User) -> list[DesignSummary]:
    """The caller's designs, most recently updated first."""
    rows = db.scalars(
        select(ShipDesign)
        .where(ShipDesign.user_id == user.id)
        .order_by(ShipDesign.updated_at.desc(), ShipDesign.id)
    ).all()
    _log.info("listed %d designs for user %s", len(rows), user.id)
    return [
        DesignSummary(
            id=r.id,
            name=r.name,
            format_version=r.format_version,
            block_count=len(json.loads(r.design_json)["blocks"]),
            updated_at=r.updated_at,
        )
        for r in rows
    ]


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_create_then_get_roundtrips_the_design
# noqa: E501  # frob:tests tests/unit/test_designs.py::test_create_beyond_the_per_player_cap_returns_409
def create_design(
    db: DBSession, user: User, name: str, design: dict[str, Any]
) -> Result[DesignOut, DesignError]:
    """Validate and store a new design for `user`, enforcing the per-player cap."""
    checked = validate_design(design)
    if checked.is_err:
        _log.warning(
            "design rejected for user %s: %s", user.id, checked.danger_err.detail
        )
        return Err(checked.danger_err)
    count = db.scalar(
        select(func.count())
        .select_from(ShipDesign)
        .where(ShipDesign.user_id == user.id)
    )
    if (count or 0) >= MAX_DESIGNS_PER_USER:
        _log.warning("design cap reached for user %s", user.id)
        return Err(
            DesignError(
                kind="limit",
                detail=f"at most {MAX_DESIGNS_PER_USER} designs per player",
            )
        )
    now = datetime.now(timezone.utc)
    row = ShipDesign(
        user_id=user.id,
        name=name,
        format_version=FORMAT_VERSION,
        design_json=checked.danger_ok,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    log_event(
        _log,
        "design %s created for user %s (%d chars)",
        row.id,
        user.id,
        len(row.design_json),
    )
    return Ok(_out(row))


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# noqa: E501  # frob:tests tests/unit/test_designs.py::test_other_players_design_is_404_for_get_put_delete
def get_design(
    db: DBSession, user: User, design_id: uuid.UUID
) -> Result[DesignOut, DesignError]:
    """Return `user`'s design, or not_found when missing or owned by someone else."""
    row = _owned(db, user, design_id)
    if row is None:
        _log.info("design %s not found for user %s", design_id, user.id)
        return Err(_not_found())
    return Ok(_out(row))


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_put_replaces_name_and_design
def update_design(
    db: DBSession, user: User, design_id: uuid.UUID, name: str, design: dict[str, Any]
) -> Result[DesignOut, DesignError]:
    """Replace the name and design of `user`'s design after validating the new JSON."""
    row = _owned(db, user, design_id)
    if row is None:
        _log.info("design %s not found for user %s", design_id, user.id)
        return Err(_not_found())
    checked = validate_design(design)
    if checked.is_err:
        _log.warning(
            "design update rejected for user %s: %s", user.id, checked.danger_err.detail
        )
        return Err(checked.danger_err)
    row.name = name
    row.design_json = checked.danger_ok
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    log_event(_log, "design %s updated for user %s", row.id, user.id)
    return Ok(_out(row))


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_delete_removes_the_design
def delete_design(
    db: DBSession, user: User, design_id: uuid.UUID
) -> Result[None, DesignError]:
    """Delete `user`'s design, or not_found when missing or owned by someone else."""
    row = _owned(db, user, design_id)
    if row is None:
        _log.info("design %s not found for user %s", design_id, user.id)
        return Err(_not_found())
    db.delete(row)
    db.commit()
    log_event(_log, "design %s deleted for user %s", design_id, user.id)
    return Ok(None)
