from enum import Enum

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    FREE_FORM_MUD = "free_form_mud"
    CIVIL_SIM = "civil_sim"
    GAME_THEORY = "game_theory"
    ECONOMY = "economy"


class InterfaceMode(str, Enum):
    TEXT = "text"
    JSON = "json"
    PING = "ping"


class EnvironmentalPressure(BaseModel):
    urgency: float = Field(ge=0.0, le=1.0)
    stakes: float = Field(ge=0.0, le=1.0)
    complexity: float = Field(ge=0.0, le=1.0)


class Scenario(BaseModel):
    id: str
    type: ScenarioType
    title: str
    narrative: str
    mode: InterfaceMode
    action_schema: dict | None = None
    affected_agents: list[str]
    environmental_pressure: EnvironmentalPressure
    deadline_seconds: int


class ModeDeclaration(BaseModel):
    epoch: int
    turn: int
    mode: InterfaceMode
    schema: dict | None = None
    scene_frame: str
    deadline_seconds: int


class Action(BaseModel):
    agent_id: str
    scenario_id: str
    mode: InterfaceMode
    payload: str | dict
    timestamp: float