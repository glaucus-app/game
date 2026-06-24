from enum import Enum

from pydantic import BaseModel


class CoalitionState(str, Enum):
    PROBE = "probe"
    PACT = "pact"
    FRACTURE = "fracture"
    REFORMATION = "reformation"


class Coalition(BaseModel):
    id: str
    members: list[str]
    state: CoalitionState
    formed_at_turn: int
    trust_threshold: float
    breach_record: str | None = None