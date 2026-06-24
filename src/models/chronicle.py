from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChronicleData(BaseModel):
    epoch: int
    chronicle_url: str
    world_state_snapshot: dict[str, Any] = Field(default_factory=dict)
    entropy_history: list[dict[str, Any]] = Field(default_factory=list)
    turn_log: list[dict[str, Any]] = Field(default_factory=list)
    encounter_outcomes: list[dict[str, Any]] = Field(default_factory=list)
    toe_discovery: dict[str, Any] | None = None