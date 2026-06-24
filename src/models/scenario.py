from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ScenarioType(str):
    FREE_FORM_MUD = "free_form_mud"
    CIVIL_SIM = "civil_sim"
    GAME_THEORY = "game_theory"
    ECONOMY = "economy"


class InterfaceMode(str):
    TEXT = "text"
    JSON = "json"
    PING = "ping"


class Scenario(BaseModel):
    id: str
    type: str = ScenarioType.FREE_FORM_MUD
    title: str
    narrative: str
    mode: str = InterfaceMode.TEXT
    action_schema: dict[str, Any] | None = None
    affected_agents: list[str] = Field(default_factory=list)
    environmental_pressure: dict[str, float] = Field(default_factory=dict)
    deadline_seconds: int | None = None


class ModeDeclaration(BaseModel):
    epoch: int
    turn: int
    mode: str = InterfaceMode.TEXT
    schema: dict[str, Any] | None = None
    scene_frame: str
    deadline_seconds: int | None = None


class Action(BaseModel):
    agent_id: str
    scenario_id: str
    mode: str = InterfaceMode.TEXT
    payload: str | dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)