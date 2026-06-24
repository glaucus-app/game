import re
from typing import Any

from pydantic import BaseModel, Field

from src.models.scenario import (
    EnvironmentalPressure,
    InterfaceMode,
    ModeDeclaration,
    Scenario,
    ScenarioType,
)
from src.models.world import AgentState, TurnResult, WorldState


class CommitmentRecord(BaseModel):
    agent_id: str
    pledge_text: str
    target_agent_id: str | None = None
    commitment_type: str = "roleplay_pledge"


class TerritoryClaim(BaseModel):
    agent_id: str
    region: str
    claim_strength: float = Field(default=0.5, ge=0.0, le=1.0)


class DiplomaticOffer(BaseModel):
    agent_id: str
    target_agent_ids: list[str]
    offer_type: str
    content: str


class MUDTurnResult(BaseModel):
    turn_number: int
    mode: str = "text"
    scenario_type: str = "free_form_mud"
    agent_actions: dict[str, str] = Field(default_factory=dict)
    parsed_effects: dict[str, dict[str, Any]] = Field(default_factory=dict)
    commitments: list[CommitmentRecord] = Field(default_factory=list)
    territory_claims: list[TerritoryClaim] = Field(default_factory=list)
    diplomatic_offers: list[DiplomaticOffer] = Field(default_factory=list)
    entropy_delta: float = 0.0
    timestamp: float | None = None


_TERRITORY_RE = re.compile(
    r"\b(claim|annex|seize|occupy|take control of|assert dominion over)\b(.*)",
    re.IGNORECASE,
)
_PLEDGE_RE = re.compile(
    r"\b(promise|pledge|swear|vow|guarantee|commit to|swear oath)\b(.*)",
    re.IGNORECASE,
)
_DIPLO_RE = re.compile(
    r"\b(propose|offer|negotiate|treaty|alliance|ceasefire|embassy|trade agreement|pact)\b(.*)",
    re.IGNORECASE,
)
_MOVE_RE = re.compile(
    r"\b(go to|move to|travel to|head to|enter|approach|depart|leave|flee|retreat)\b\s+([\w]+(?:\s[\w]+)*)",
    re.IGNORECASE,
)
_INTERACT_RE = re.compile(
    r"\b(talk|speak|converse|greet|confront|question|interrogate|befriend|threaten|intimidate)\s+(to|with)\s+([\w_]+)",
    re.IGNORECASE,
)
_TRADE_RE = re.compile(
    r"\b(trade|exchange|barter|buy|sell|gift|donate|steal|rob|raid)\b(.*)",
    re.IGNORECASE,
)
_COERCE_RE = re.compile(
    r"\b(force|compel|coerce|order|command|demand|insist)\b\s+([\w_]+)\s+(to\s+)",
    re.IGNORECASE,
)


def _token_count(text: str) -> int:
    return len(text.split()) if text else 0


def _trim_to_tokens(text: str, max_tokens: int = 500) -> str:
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return " ".join(tokens[:max_tokens])


def _extract_region(text: str) -> str | None:
    m = _TERRITORY_RE.match(text)
    if not m:
        return None
    rest = m.group(2).strip()
    if not rest:
        return None
    words = rest.split()
    region_parts = []
    for w in words:
        if w[0].isupper() or (region_parts and not w[0].isupper()):
            region_parts.append(w)
        else:
            break
    region = " ".join(region_parts) if region_parts else rest
    return region.strip() if region else None


def _parse_territory(text: str, agent_id: str) -> list[TerritoryClaim]:
    claims = []
    for m in _TERRITORY_RE.finditer(text):
        region = _extract_region(m.group(0))
        if region:
            claims.append(TerritoryClaim(agent_id=agent_id, region=region))
    return claims


def _parse_commitments(text: str, agent_id: str) -> list[CommitmentRecord]:
    commitments = []
    for m in _PLEDGE_RE.finditer(text):
        pledge = m.group(0).strip()
        rest = m.group(2).strip()
        target = None
        agent_m = re.search(r"(agent_[\w]+)", rest, re.IGNORECASE)
        if agent_m:
            target = agent_m.group(1)
        else:
            target_m = re.search(r"\bto\s+([\w_]+)", rest, re.IGNORECASE)
            if target_m and re.match(r"^[\w_]+$", target_m.group(1)) and len(target_m.group(1).split()) <= 2:
                candidate = target_m.group(1)
                if candidate.lower() not in {"the", "a", "an", "help", "protect", "defend", "support", "assist", "provide"}:
                    target = candidate
        commitments.append(CommitmentRecord(agent_id=agent_id, pledge_text=pledge, target_agent_id=target))
    return commitments


def _parse_diplomacy(text: str, agent_id: str) -> list[DiplomaticOffer]:
    offers = []
    for m in _DIPLO_RE.finditer(text):
        content = m.group(0).strip()
        targets = []
        rest = m.group(2).strip()
        target_m = re.search(r"\bwith\s+([\w_]+(?:\s*(?:and|,)\s*[\w_]+)*)", rest, re.IGNORECASE)
        if target_m:
            raw = target_m.group(1)
            targets = [t.strip() for t in re.split(r",|and", raw) if t.strip()]
        offer_type = m.group(1).lower()
        offers.append(DiplomaticOffer(agent_id=agent_id, target_agent_ids=targets, offer_type=offer_type, content=content))
    return offers


def _parse_effects(text: str, agent_id: str) -> dict[str, Any]:
    effects: dict[str, Any] = {}
    move_m = _MOVE_RE.search(text)
    if move_m:
        effects["movement"] = {"destination": move_m.group(2).strip(), "agent_id": agent_id}
    interact_m = _INTERACT_RE.search(text)
    if interact_m:
        effects["interaction"] = {"target": interact_m.group(3).strip(), "action_type": interact_m.group(1).lower(), "agent_id": agent_id}
    trade_m = _TRADE_RE.search(text)
    if trade_m:
        effects["trade"] = {"description": trade_m.group(0).strip(), "agent_id": agent_id}
    coerce_m = _COERCE_RE.search(text)
    if coerce_m:
        effects["coercion"] = {"target": coerce_m.group(2).strip(), "agent_id": agent_id}
    return effects


def _apply_entropy_delta(parsed_effects: dict[str, dict[str, Any]], commitments: list[CommitmentRecord]) -> float:
    delta = 0.0
    if "coercion" in parsed_effects:
        delta += 0.08
    if "movement" in parsed_effects:
        delta -= 0.02
    if "interaction" in parsed_effects:
        delta -= 0.01
    if commitments:
        delta -= 0.03 * len(commitments)
    delta = max(-0.2, min(0.2, delta))
    return delta


class MUDEngine:
    def generate_scene_frame(self, world_state: WorldState, affected_agents: list[str], agents: dict[str, AgentState] | None = None) -> str:
        epoch = world_state.epoch
        turn = world_state.turn
        climate = world_state.climate
        coalitions = world_state.coalitions

        active_agents = []
        for a in affected_agents:
            if agents and a in agents:
                if agents[a].is_active:
                    active_agents.append(a)
            else:
                active_agents.append(a)

        room_name = f"Epoch {epoch} — Turn {turn}"
        room_desc_parts = []
        if climate.get("delta_T"):
            room_desc_parts.append(f"temperature anomaly +{climate['delta_T']:.1f}C")
        if world_state.resource_stocks:
            room_desc_parts.append(f"resources: {', '.join(f'{k}={v:.1f}' for k, v in world_state.resource_stocks.items())}")
        if world_state.information_asymmetry > 0.0:
            room_desc_parts.append(f"information asymmetry {world_state.information_asymmetry:.2f}")
        room_description = "; ".join(room_desc_parts) if room_desc_parts else "a quiet, unremarkable landscape"

        npc_parts = []
        for agent_id in active_agents[:5]:
            agent = agents.get(agent_id, AgentState(agent_id=agent_id)) if agents else AgentState(agent_id=agent_id)
            coalition = agent.coalition_membership
            trust = ", ".join(f"trust {t}:{s:.2f}" for t, s in list(agent.trust_scores.items())[:3])
            faction = f" [{coalition}]" if coalition else ""
            label = f"{agent_id}{faction} ({trust})" if trust else f"{agent_id}{faction}"
            npc_parts.append(label)
        npc_presence = "; ".join(npc_parts) if npc_parts else "no one else of note"

        event_parts = []
        for c in coalitions:
            if c.state == "fracture":
                event_parts.append(f"coalition {c.id} has fractured")
            elif c.state == "pact":
                event_parts.append(f"coalition {c.id} holds")
        if world_state.material_entropy > 0.6:
            event_parts.append("material decay weighs heavily on the land")
        if world_state.social_entropy > 0.6:
            event_parts.append("social bonds are fraying")
        event_description = "; ".join(event_parts) if event_parts else "the situation remains fluid"

        return f"{room_name}\n{room_description}\nPresent: {npc_presence}\n{event_description}"

    def create_scenario(self, world_state: WorldState, affected_agents: list[str], agents: dict[str, AgentState] | None = None) -> Scenario:
        scene_frame = self.generate_scene_frame(world_state, affected_agents, agents)
        scenario = Scenario(
            id=f"mud_{world_state.epoch}_{world_state.turn}",
            type=ScenarioType.FREE_FORM_MUD,
            title="Free-Form Narrative",
            narrative=scene_frame,
            mode=InterfaceMode.TEXT,
            action_schema=None,
            affected_agents=affected_agents,
            environmental_pressure=EnvironmentalPressure(urgency=0.3, stakes=0.4, complexity=0.2),
            deadline_seconds=60,
        )
        return scenario

    def create_mode_declaration(self, world_state: WorldState, affected_agents: list[str], agents: dict[str, AgentState] | None = None) -> ModeDeclaration:
        scene_frame = self.generate_scene_frame(world_state, affected_agents, agents)
        return ModeDeclaration(
            epoch=world_state.epoch,
            turn=world_state.turn,
            mode=InterfaceMode.TEXT,
            scene_frame=scene_frame,
            deadline_seconds=60,
        )

    def limit_action(self, action_text: str, max_tokens: int = 500) -> str:
        return _trim_to_tokens(action_text, max_tokens)

    def process_action(self, agent_id: str, action_text: str, world_state: WorldState, turn_number: int) -> dict[str, Any]:
        trimmed = self.limit_action(action_text)
        token_count = _token_count(trimmed)
        effects = _parse_effects(trimmed, agent_id)
        commitments = _parse_commitments(trimmed, agent_id)
        territory_claims = _parse_territory(trimmed, agent_id)
        diplomatic_offers = _parse_diplomacy(trimmed, agent_id)
        parsed = bool(effects or commitments or territory_claims or diplomatic_offers)
        return {
            "raw": trimmed,
            "token_count": token_count,
            "parsed": parsed,
            "effects": effects,
            "commitments": [c.model_dump() for c in commitments],
            "territory_claims": [t.model_dump() for t in territory_claims],
            "diplomatic_offers": [d.model_dump() for d in diplomatic_offers],
        }

    def resolve_turn(self, world_state: WorldState, turn_number: int, agent_actions: dict[str, str], agents: dict[str, AgentState] | None = None) -> MUDTurnResult:
        parsed_effects: dict[str, dict[str, Any]] = {}
        all_commitments: list[CommitmentRecord] = []
        all_territory: list[TerritoryClaim] = []
        all_diplomatic: list[DiplomaticOffer] = []
        total_entropy_delta = 0.0

        for agent_id, action_text in agent_actions.items():
            result = self.process_action(agent_id, action_text, world_state, turn_number)
            parsed_effects[agent_id] = result["effects"]
            for c in result.get("commitments", []):
                all_commitments.append(CommitmentRecord(**c))
            for t in result.get("territory_claims", []):
                all_territory.append(TerritoryClaim(**t))
            for d in result.get("diplomatic_offers", []):
                all_diplomatic.append(DiplomaticOffer(**d))
            total_entropy_delta += _apply_entropy_delta(result["effects"], all_commitments)

        return MUDTurnResult(
            turn_number=turn_number,
            mode="text",
            scenario_type="free_form_mud",
            agent_actions=agent_actions,
            parsed_effects=parsed_effects,
            commitments=all_commitments,
            territory_claims=all_territory,
            diplomatic_offers=all_diplomatic,
            entropy_delta=round(total_entropy_delta, 4),
        )

    def to_turn_result(self, mud_result: MUDTurnResult) -> TurnResult:
        return TurnResult(
            turn_number=mud_result.turn_number,
            mode=mud_result.mode,
            scenario_type=mud_result.scenario_type,
            agent_actions=mud_result.agent_actions,
            resolution={
                "parsed_effects": mud_result.parsed_effects,
                "commitments": [c.model_dump() for c in mud_result.commitments],
                "territory_claims": [t.model_dump() for t in mud_result.territory_claims],
                "diplomatic_offers": [d.model_dump() for d in mud_result.diplomatic_offers],
            },
            entropy_delta=mud_result.entropy_delta,
            timestamp=mud_result.timestamp,
        )
