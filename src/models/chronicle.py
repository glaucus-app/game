from typing import Any, Union

from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    agent_id: str
    action: str
    outcome: str
    entropy_delta: float = 0.0


class TurnSummary(BaseModel):
    turn: int
    scenario: str
    affected_agents: list[str]
    actions: list[AgentAction]
    entropy_before: float
    entropy_after: float
    interaction_outcome: str = ""


class NotableEvent(BaseModel):
    turn: int
    event_type: str
    description: str
    agents_involved: list[str]
    entropy_delta: float


class AgentPerformance(BaseModel):
    agent_id: str
    accuracy: list[float] = Field(default_factory=list)
    performance_score: float = 0.0
    cooperation_count: int = 0
    betrayal_count: int = 0


class EpochHistory(BaseModel):
    epoch_number: int
    civilization_name: str
    start_date: str
    end_date: str
    initial_world_state: dict[str, Any]
    final_entropy: float
    entropy_graph: list[tuple[int, float]]
    turns: list[TurnSummary]
    agents: list[str]
    human_profiles: dict[str, str]
    agent_performance: dict[str, AgentPerformance]
    notable_events: list[NotableEvent] = Field(default_factory=list)
    collapse_cause: str = "entropy_collapse"