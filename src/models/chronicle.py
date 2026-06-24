from pydantic import BaseModel, Field

from src.models.entropy import EntropySnapshot


class ChronicleData(BaseModel):
    epoch: int
    chronicle_url: str
    world_state_snapshot: dict
    entropy_history: list[EntropySnapshot] = Field(default_factory=list)
    turn_log: list[dict] = Field(default_factory=list)
    encounter_outcomes: list[dict] = Field(default_factory=list)
    toe_discovery: dict | None = None