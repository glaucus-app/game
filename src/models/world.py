from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4


class ActionType(str, Enum):
    COOPERATE = "cooperate"
    COMPETE = "compete"
    NEUTRAL = "neutral"
    COMMUNICATE = "communicate"
    NEGOTIATE = "negotiate"
    DESTROY = "destroy"
    BUILD = "build"
    SHARE = "share"
    REFUSE = "refuse"


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    scenario_id: str
    action_type: ActionType
    target_agent: Optional[str] = None
    payload: dict = Field(default_factory=dict)


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    narrative: str
    affected_agents: list[str] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    environmental_pressure: dict = Field(default_factory=dict)


class AgentState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    human_profile_ref: Optional[str] = None
    position: tuple[int, int] = (0, 0)
    action_history: list[Action] = Field(default_factory=list)
    connected: bool = True


class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    epoch: int = 0
    turn: int = 0
    agents: dict[str, AgentState] = Field(default_factory=dict)
    active_scenarios: list[Scenario] = Field(default_factory=list)
    resolved_scenarios: list[dict] = Field(default_factory=list)
    entropy: float = 0.0

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "WorldState":
        return cls.model_validate_json(data)