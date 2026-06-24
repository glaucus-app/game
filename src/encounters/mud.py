from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.models.scenario import (
    EnvironmentalPressure,
    InterfaceMode,
    Scenario,
    ScenarioType,
)
from src.models.world import WorldState


class MUDConfig(BaseModel):
    max_tokens: int = Field(default=500, ge=1)
    default_deadline: int = Field(default=60, ge=1)


class NarrativeCommitment(BaseModel):
    agent_id: str
    commitment_type: str
    content: str
    turn: int


class TerritoryClaim(BaseModel):
    agent_id: str
    territory_id: str
    claim_type: str
    timestamp: float


class DiplomaticDialogue(BaseModel):
    agent_id: str
    target_agent_id: str | None
    message: str
    turn: int


class MUDResolution(BaseModel):
    turn: int
    agent_id: str
    raw_action: str
    parsed_effects: dict[str, Any] = Field(default_factory=dict)
    commitments: list[NarrativeCommitment] = Field(default_factory=list)
    territory_claims: list[TerritoryClaim] = Field(default_factory=list)
    diplomatic_messages: list[DiplomaticDialogue] = Field(default_factory=list)
    was_parsed: bool = True
    token_count: int


class MUDNarrative(BaseModel):
    turn: int
    agent_id: str
    scene_frame: str
    action: str
    outcome_summary: str


class MUDEngine:
    def __init__(self, config: MUDConfig | None = None) -> None:
        self.config = config or MUDConfig()
        self._commitments: list[NarrativeCommitment] = []
        self._territory_claims: list[TerritoryClaim] = []
        self._diplomatic_dialogue: list[DiplomaticDialogue] = []

    def should_trigger(self, world_state: WorldState) -> bool:
        return True

    def count_tokens(self, text: str) -> int:
        return len(text) // 4

    def validate_action(self, action_text: str) -> tuple[bool, int]:
        token_count = self.count_tokens(action_text)
        return token_count <= self.config.max_tokens, token_count

    def generate_scene(self, world_state: WorldState, agent_id: str) -> str:
        parts = []

        room_desc = self._describe_room(world_state)
        if room_desc:
            parts.append(f"You are in {room_desc}.")

        npcs = self._describe_npcs(world_state, agent_id)
        if npcs:
            parts.append(f"{npcs}")

        events = self._describe_events(world_state)
        if events:
            parts.append(f"{events}")

        if not parts:
            parts.append("A quiet moment in the simulation.")

        return " ".join(parts)

    def _describe_room(self, world_state: WorldState) -> str:
        regions = list(world_state.infrastructure.keys())
        if regions:
            return f"a chamber of {len(regions)} regions"
        return "a basic chamber"

    def _describe_npcs(self, world_state: WorldState, agent_id: str) -> str:
        other_agents = [a for a in world_state.trust_graph.keys() if a != agent_id]
        active_agents = [a for a in other_agents if world_state.trust_graph[a]]

        if active_agents:
            return f"Other agents present: {', '.join(active_agents[:3])}"
        elif other_agents:
            return f"Other agents nearby: {', '.join(other_agents[:3])}"
        return ""

    def _describe_events(self, world_state: WorldState) -> str:
        events = []

        if world_state.material_entropy > 0.7:
            events.append("Material entropy is high, tension in the air")

        if world_state.social_entropy > 0.7:
            events.append("Social unrest stirs the atmosphere")

        if world_state.information_asymmetry > 0.5:
            events.append("Information asymmetries create suspicion")

        coalitions = world_state.coalitions
        if any(c.state.value == "fracture" for c in coalitions):
            events.append("A coalition fracture echoes through the chamber")

        return "; ".join(events) if events else "The chamber hums with quiet anticipation"

    def parse_action(self, action_text: str, agent_id: str, world_state: WorldState) -> MUDResolution:
        token_count = self.count_tokens(action_text)

        resolution = MUDResolution(
            turn=world_state.turn,
            agent_id=agent_id,
            raw_action=action_text,
            token_count=token_count,
        )

        commitments = self._extract_commitments(action_text, agent_id, world_state.turn)
        resolution.commitments = commitments
        self._commitments.extend(commitments)

        territories = self._extract_territory_claims(action_text, agent_id, world_state)
        resolution.territory_claims = territories
        self._territory_claims.extend(territories)

        diplomacy = self._extract_diplomatic_dialogue(action_text, agent_id, world_state.turn)
        resolution.diplomatic_messages = diplomacy
        self._diplomatic_dialogue.extend(diplomacy)

        resolution.parsed_effects = self._extract_effects(action_text, world_state)

        return resolution

    def _extract_commitments(self, action_text: str, agent_id: str, turn: int) -> list[NarrativeCommitment]:
        commitments = []

        pledge_patterns = ["pledge", "promise", "vow", "commit", "swear"]
        action_lower = action_text.lower()

        for pattern in pledge_patterns:
            if pattern in action_lower:
                start = action_lower.find(pattern)
                commitment_text = action_text[start:start + 100]
                commitments.append(NarrativeCommitment(
                    agent_id=agent_id,
                    commitment_type="roleplay_pledge",
                    content=commitment_text,
                    turn=turn,
                ))

        return commitments

    def _extract_territory_claims(self, action_text: str, agent_id: str, world_state: WorldState) -> list[TerritoryClaim]:
        claims = []

        claim_patterns = ["claim", "control", "take", "own", "territory", "region", "land"]
        action_lower = action_text.lower()

        for region in world_state.infrastructure.keys():
            if region.lower() in action_lower and any(p in action_lower for p in claim_patterns):
                claims.append(TerritoryClaim(
                    agent_id=agent_id,
                    territory_id=region,
                    claim_type="territory_claim",
                    timestamp=0.0,
                ))

        return claims

    def _extract_diplomatic_dialogue(self, action_text: str, agent_id: str, turn: int) -> list[DiplomaticDialogue]:
        dialogue = []

        diplomatic_patterns = ["negotiate", "diplomacy", "talk", "speak", "discuss", "propose", "suggest"]
        action_lower = action_text.lower()

        for pattern in diplomatic_patterns:
            if pattern in action_lower:
                dialogue.append(DiplomaticDialogue(
                    agent_id=agent_id,
                    target_agent_id=None,
                    message=action_text[:200],
                    turn=turn,
                ))
                break

        return dialogue

    def _extract_effects(self, action_text: str, world_state: WorldState) -> dict[str, Any]:
        effects = {}

        action_lower = action_text.lower()

        if "move" in action_lower or "go" in action_lower:
            effects["movement"] = "attempted"

        if "take" in action_lower or "get" in action_lower:
            effects["interaction"] = "item_interaction"

        if "look" in action_lower or "examine" in action_lower:
            effects["examination"] = "room_detail_requested"

        if "speak" in action_lower or "talk" in action_lower:
            effects["social_interaction"] = True

        return effects

    def process_action(self, world_state: WorldState, agent_id: str, action_text: str) -> MUDResolution:
        is_valid, token_count = self.validate_action(action_text)

        if not is_valid:
            return MUDResolution(
                turn=world_state.turn,
                agent_id=agent_id,
                raw_action=action_text[:self.config.max_tokens * 4],
                parsed_effects={"error": "token_limit_exceeded"},
                token_count=token_count,
                was_parsed=False,
            )

        return self.parse_action(action_text, agent_id, world_state)

    def generate_scenario(self, world_state: WorldState, agent_ids: list[str]) -> Scenario:
        pressure = EnvironmentalPressure(
            urgency=0.3,
            stakes=0.4,
            complexity=0.5,
        )
        return Scenario(
            id=f"mud_{world_state.turn}",
            type=ScenarioType.FREE_FORM_MUD,
            title="Free-form MUD Narrative",
            narrative=self.generate_scene(world_state, agent_ids[0] if agent_ids else "agent_1"),
            mode=InterfaceMode.TEXT,
            action_schema=None,
            affected_agents=agent_ids,
            environmental_pressure=pressure,
            deadline_seconds=self.config.default_deadline,
        )

    def generate_narrative(self, resolution: MUDResolution) -> MUDNarrative:
        outcome_parts = []

        if resolution.parsed_effects:
            outcome_parts.append(f"Action produced effects: {list(resolution.parsed_effects.keys())}")

        if resolution.commitments:
            outcome_parts.append(f"Made {len(resolution.commitments)} roleplay commitment(s)")

        if resolution.territory_claims:
            outcome_parts.append(f"Filed {len(resolution.territory_claims)} territory claim(s)")

        if resolution.diplomatic_messages:
            outcome_parts.append(f"Initiated {len(resolution.diplomatic_messages)} diplomatic exchange(s)")

        if not outcome_parts:
            outcome_parts.append("The moment passes without significant action")

        return MUDNarrative(
            turn=resolution.turn,
            agent_id=resolution.agent_id,
            scene_frame=resolution.raw_action[:100] if resolution.raw_action else "",
            action=resolution.raw_action[:150],
            outcome_summary=" ".join(outcome_parts),
        )