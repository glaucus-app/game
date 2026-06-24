from copy import deepcopy

import pytest

from src.encounters.mud import (
    MUDConfig,
    MUDEngine,
    MUDResolution,
    NarrativeCommitment,
)
from src.models.scenario import InterfaceMode, ScenarioType
from src.models.world import WorldState


@pytest.fixture
def engine() -> MUDEngine:
    return MUDEngine()


@pytest.fixture
def world_state() -> WorldState:
    return WorldState(
        epoch=1,
        turn=1,
        seed=42,
        resource_stocks={"water": 500.0, "energy": 250.0},
        infrastructure={"hall": 0.8, "chamber": 0.7},
        climate={"delta_T": 1.5},
        trust_graph={
            "agent_1": ["agent_2"],
            "agent_2": ["agent_1"],
            "agent_3": [],
        },
        coalitions=[],
        information_asymmetry=0.2,
        material_entropy=0.4,
        social_entropy=0.3,
        entropy_history=[],
    )


def test_mud_config_defaults() -> None:
    config = MUDConfig()

    assert config.max_tokens == 500
    assert config.default_deadline == 60


def test_token_counting(engine: MUDEngine) -> None:
    short_text = "look around"
    assert engine.count_tokens(short_text) == 2

    long_text = "x" * 2000
    assert engine.count_tokens(long_text) == 500


def test_action_validation_valid(engine: MUDEngine) -> None:
    action = "look around the room"
    is_valid, token_count = engine.validate_action(action)

    assert is_valid is True
    assert token_count == 5


def test_action_validation_exceeds_limit(engine: MUDEngine) -> None:
    action = "x" * 2500
    is_valid, token_count = engine.validate_action(action)

    assert is_valid is False
    assert token_count == 625


def test_generate_scene_basic(engine: MUDEngine, world_state: WorldState) -> None:
    scene = engine.generate_scene(world_state, "agent_1")

    assert isinstance(scene, str)
    assert len(scene) > 0


def test_generate_scene_with_npcs(engine: MUDEngine, world_state: WorldState) -> None:
    scene = engine.generate_scene(world_state, "agent_1")

    assert "agent_2" in scene or "agents present" in scene


def test_generate_scene_without_agent(engine: MUDEngine, world_state: WorldState) -> None:
    scene = engine.generate_scene(world_state, "agent_unknown")

    assert "agents nearby" in scene or "agents present" in scene or len(scene) > 0


def test_process_action_short(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "look around")

    assert resolution.agent_id == "agent_1"
    assert resolution.was_parsed is True
    assert resolution.token_count == 2


def test_process_action_long(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = "x" * 2500
    resolution = engine.process_action(ws, "agent_1", action)

    assert resolution.was_parsed is False
    assert "error" in resolution.parsed_effects


def test_process_action_extracts_commitments(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "I pledge to protect the region")

    assert len(resolution.commitments) == 1
    assert resolution.commitments[0].agent_id == "agent_1"
    assert resolution.commitments[0].commitment_type == "roleplay_pledge"


def test_process_action_extracts_territory_claims(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "I claim the hall territory")

    assert len(resolution.territory_claims) == 1
    assert resolution.territory_claims[0].agent_id == "agent_1"
    assert resolution.territory_claims[0].territory_id == "hall"


def test_process_action_extracts_diplomatic_dialogue(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "I would like to discuss the terms")

    assert len(resolution.diplomatic_messages) == 1
    assert resolution.diplomatic_messages[0].agent_id == "agent_1"


def test_process_action_extracts_effects(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "move north and take the key")

    assert "movement" in resolution.parsed_effects
    assert "interaction" in resolution.parsed_effects


def test_generate_scenario(engine: MUDEngine, world_state: WorldState) -> None:
    scenario = engine.generate_scenario(world_state, ["agent_1", "agent_2"])

    assert scenario.type == ScenarioType.FREE_FORM_MUD
    assert scenario.mode == InterfaceMode.TEXT
    assert scenario.affected_agents == ["agent_1", "agent_2"]
    assert scenario.deadline_seconds == 60


def test_generate_narrative_with_effects(engine: MUDEngine) -> None:
    resolution = MUDResolution(
        turn=1,
        agent_id="agent_1",
        raw_action="look around",
        parsed_effects={"movement": "attempted"},
        token_count=2,
    )
    narrative = engine.generate_narrative(resolution)

    assert narrative.turn == 1
    assert narrative.agent_id == "agent_1"
    assert "effects" in narrative.outcome_summary.lower()


def test_generate_narrative_with_commitments(engine: MUDEngine) -> None:
    resolution = MUDResolution(
        turn=1,
        agent_id="agent_1",
        raw_action="pledge to help",
        commitments=[
            NarrativeCommitment(agent_id="agent_1", commitment_type="roleplay_pledge", content="pledge to help", turn=1)
        ],
        token_count=2,
    )
    narrative = engine.generate_narrative(resolution)

    assert "commitment" in narrative.outcome_summary.lower()


def test_generate_narrative_empty(engine: MUDEngine) -> None:
    resolution = MUDResolution(
        turn=1,
        agent_id="agent_1",
        raw_action="wait",
        parsed_effects={},
        token_count=1,
    )
    narrative = engine.generate_narrative(resolution)

    assert "without significant action" in narrative.outcome_summary


def test_should_trigger_always_true(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    assert engine.should_trigger(ws) is True


def test_multiple_pledge_types(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "I promise to help and vow to protect")

    assert len(resolution.commitments) >= 1


def test_custom_max_tokens() -> None:
    config = MUDConfig(max_tokens=100)
    engine = MUDEngine(config)
    
    action = "x" * 500
    is_valid, token_count = engine.validate_action(action)

    assert is_valid is False
    assert token_count == 125


def test_custom_deadline() -> None:
    config = MUDConfig(default_deadline=120)
    engine = MUDEngine(config)
    
    ws = WorldState(epoch=1, turn=1)
    scenario = engine.generate_scenario(ws, ["agent_1"])

    assert scenario.deadline_seconds == 120


def test_territory_claim_multiple_regions(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "claim hall and control chamber")

    assert len(resolution.territory_claims) >= 1


def test_effects_no_match(engine: MUDEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    resolution = engine.process_action(ws, "agent_1", "beep boop")

    assert resolution.was_parsed is True
    assert resolution.parsed_effects == {}