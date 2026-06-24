from __future__ import annotations

from pydantic import BaseModel


class CoalitionState(str):
    PROBE = "probe"
    PACT = "pact"
    FRACTURE = "fracture"
    REFORMATION = "reformation"


class Coalition(BaseModel):
    id: str
    members: list[str]
    state: str = CoalitionState.PROBE
    formed_at_turn: int
    trust_threshold: float = 0.5
    breach_record: str | None = None