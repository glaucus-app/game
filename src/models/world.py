from enum import StrEnum

from pydantic import BaseModel, Field

from src.models.coalition import Coalition
from src.models.entropy import EntropySnapshot


class ConsentStatus(StrEnum):
    PENDING = "pending"
    GRANTED = "granted"
    REVOKED = "revoked"


class AgentState(BaseModel):
    agent_id: str
    action_history: list[str] = Field(default_factory=list)
    coalition_membership: str | None = None
    resources: dict[str, object] = Field(default_factory=dict)
    trust_scores: dict[str, float] = Field(default_factory=dict)
    is_active: bool = True
    consent_status: ConsentStatus = ConsentStatus.PENDING


class TurnResult(BaseModel):
    turn_number: int
    mode: str
    scenario_type: str
    agent_actions: dict[str, str] = Field(default_factory=dict)
    resolution: dict[str, object] = Field(default_factory=dict)
    entropy_delta: float = 0.0
    timestamp: float | None = None


class WorldState(BaseModel):
    epoch: int = 0
    turn: int = 0
    seed: int | None = None
    resource_stocks: dict[str, float] = Field(default_factory=dict)
    infrastructure: dict[str, float] = Field(default_factory=dict)
    climate: dict[str, object] = Field(default_factory=dict)
    trust_graph: dict[str, list[str]] = Field(default_factory=dict)
    coalitions: list[Coalition] = Field(default_factory=list)
    information_asymmetry: float = 0.0
    material_entropy: float = 0.0
    social_entropy: float = 0.0
    entropy_history: list[EntropySnapshot] = Field(default_factory=list)