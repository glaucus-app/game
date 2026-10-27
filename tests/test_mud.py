
from src.encounters.mud import (
    MUDEngine,
    _parse_commitments,
    _parse_diplomacy,
    _parse_effects,
    _parse_territory,
    _token_count,
    _trim_to_tokens,
)
from src.models.coalition import Coalition, CoalitionState
from src.models.world import AgentState, ConsentStatus, WorldState


def make_world_state(**kwargs) -> WorldState:
    defaults = dict(
        epoch=1,
        turn=1,
        seed=42,
        resource_stocks={"water": 100.0, "energy": 50.0},
        infrastructure={"region_a": 0.9, "region_b": 0.85},
        climate={"delta_T": 2.5},
        trust_graph={"agent_1": ["agent_2"], "agent_2": ["agent_1"]},
        coalitions=[
            Coalition(id="c1", members=["agent_1", "agent_2"], state=CoalitionState.PACT, formed_at_turn=1, trust_threshold=0.7)
        ],
        information_asymmetry=0.3,
        material_entropy=0.254,
        social_entropy=0.572,
    )
    defaults.update(kwargs)
    return WorldState(**defaults)


def make_agents() -> dict[str, AgentState]:
    return {
        "agent_1": AgentState(agent_id="agent_1", is_active=True, consent_status=ConsentStatus.GRANTED),
        "agent_2": AgentState(agent_id="agent_2", is_active=True, consent_status=ConsentStatus.GRANTED),
    }


def test_token_count():
    assert _token_count("hello world") == 2
    assert _token_count("") == 0


def test_trim_to_tokens_within_limit():
    text = "one two three"
    assert _trim_to_tokens(text, 10) == text


def test_trim_to_tokens_exceeds_limit():
    text = " ".join(str(i) for i in range(10))
    trimmed = _trim_to_tokens(text, 5)
    assert len(trimmed.split()) == 5


def test_parse_territory_claim():
    claims = _parse_territory("I claim the Northern Reaches", "agent_1")
    assert len(claims) == 1
    assert claims[0].agent_id == "agent_1"
    assert claims[0].region == "the Northern Reaches"
    assert claims[0].claim_strength == 0.5


def test_parse_territory_no_match():
    claims = _parse_territory("I walk north", "agent_1")
    assert len(claims) == 0


def test_parse_commitments():
    commits = _parse_commitments("I promise to help agent_2", "agent_1")
    assert len(commits) == 1
    assert commits[0].agent_id == "agent_1"
    assert commits[0].target_agent_id == "agent_2"
    assert "promise" in commits[0].pledge_text


def test_parse_commitments_no_target():
    commits = _parse_commitments("I vow to protect the weak", "agent_1")
    assert len(commits) == 1
    assert commits[0].target_agent_id is None


def test_parse_diplomacy():
    offers = _parse_diplomacy("I propose an alliance with agent_2 and agent_3", "agent_1")
    assert len(offers) == 1
    assert offers[0].agent_id == "agent_1"
    assert "agent_2" in offers[0].target_agent_ids
    assert "agent_3" in offers[0].target_agent_ids
    assert offers[0].offer_type == "propose"


def test_parse_diplomacy_no_match():
    offers = _parse_diplomacy("I walk peacefully", "agent_1")
    assert len(offers) == 0


def test_parse_effects_movement():
    effects = _parse_effects("I go to the Northern Reaches", "agent_1")
    assert "movement" in effects
    assert effects["movement"]["destination"] == "the Northern Reaches"


def test_parse_effects_interaction():
    effects = _parse_effects("I talk to agent_2", "agent_1")
    assert "interaction" in effects
    assert effects["interaction"]["target"] == "agent_2"
    assert effects["interaction"]["action_type"] == "talk"


def test_parse_effects_trade():
    effects = _parse_effects("I trade water for energy", "agent_1")
    assert "trade" in effects
    assert "trade" in effects["trade"]["description"]


def test_parse_effects_coercion():
    effects = _parse_effects("I force agent_2 to move", "agent_1")
    assert "coercion" in effects
    assert effects["coercion"]["target"] == "agent_2"


def test_parse_effects_none():
    effects = _parse_effects("I contemplate existence", "agent_1")
    assert len(effects) == 0


def test_mud_engine_generate_scene_frame():
    ws = make_world_state()
    engine = MUDEngine()
    agents = make_agents()
    frame = engine.generate_scene_frame(ws, ["agent_1", "agent_2"], agents)
    assert "Epoch 1" in frame
    assert "Turn 1" in frame
    assert "agent_1" in frame
    assert "agent_2" in frame
    assert "temperature anomaly" in frame


def test_mud_engine_generate_scene_frame_no_agents():
    ws = make_world_state()
    engine = MUDEngine()
    frame = engine.generate_scene_frame(ws, [])
    assert "no one else of note" in frame


def test_mud_engine_create_scenario():
    ws = make_world_state()
    engine = MUDEngine()
    agents = make_agents()
    scenario = engine.create_scenario(ws, ["agent_1", "agent_2"], agents)
    assert scenario.type.value == "free_form_mud"
    assert scenario.mode.value == "text"
    assert scenario.action_schema is None
    assert "agent_1" in scenario.affected_agents


def test_mud_engine_create_mode_declaration():
    ws = make_world_state()
    engine = MUDEngine()
    agents = make_agents()
    md = engine.create_mode_declaration(ws, ["agent_1"], agents)
    assert md.mode.value == "text"
    assert md.action_schema is None
    assert "Epoch 1" in md.scene_frame


def test_mud_engine_limit_action():
    engine = MUDEngine()
    short = "Short action"
    assert engine.limit_action(short) == short
    long_text = " ".join(f"word{i}" for i in range(600))
    limited = engine.limit_action(long_text, 500)
    assert len(limited.split()) == 500


def test_mud_engine_process_action_parsed():
    ws = make_world_state()
    engine = MUDEngine()
    result = engine.process_action("agent_1", "I claim the Northern Reaches and propose an alliance with agent_2", ws, 1)
    assert result["parsed"] is True
    assert len(result["territory_claims"]) == 1
    assert len(result["diplomatic_offers"]) == 1
    assert result["token_count"] <= 500


def test_mud_engine_process_action_unparsed():
    ws = make_world_state()
    engine = MUDEngine()
    result = engine.process_action("agent_1", "I think deeply about the nature of things", ws, 1)
    assert result["parsed"] is False
    assert result["raw"] == "I think deeply about the nature of things"


def test_mud_engine_process_action_commitments():
    ws = make_world_state()
    engine = MUDEngine()
    result = engine.process_action("agent_1", "I promise agent_2 I will help", ws, 1)
    assert len(result["commitments"]) == 1
    assert result["commitments"][0]["target_agent_id"] == "agent_2"


def test_mud_engine_process_action_token_trim():
    ws = make_world_state()
    engine = MUDEngine()
    long_text = " ".join(f"word{i}" for i in range(600))
    result = engine.process_action("agent_1", long_text, ws, 1)
    assert result["token_count"] == 500


def test_mud_engine_resolve_turn():
    ws = make_world_state()
    agents = make_agents()
    engine = MUDEngine()
    actions = {
        "agent_1": "I go to the market and talk to agent_2",
        "agent_2": "I promise agent_1 a fair trade",
    }
    result = engine.resolve_turn(ws, 1, actions, agents)
    assert result.turn_number == 1
    assert result.scenario_type == "free_form_mud"
    assert result.mode == "text"
    assert "agent_1" in result.agent_actions
    assert "agent_2" in result.agent_actions
    assert len(result.commitments) == 1
    assert len(result.parsed_effects) == 2


def test_mud_engine_resolve_turn_entropy():
    ws = make_world_state()
    agents = make_agents()
    engine = MUDEngine()
    actions = {"agent_1": "I force agent_2 to move"}
    result = engine.resolve_turn(ws, 1, actions, agents)
    assert result.entropy_delta > 0


def test_mud_engine_resolve_turn_empty_actions():
    ws = make_world_state()
    engine = MUDEngine()
    result = engine.resolve_turn(ws, 1, {})
    assert result.turn_number == 1
    assert result.entropy_delta == 0.0


def test_mud_engine_to_turn_result():
    ws = make_world_state()
    agents = make_agents()
    engine = MUDEngine()
    actions = {"agent_1": "I go to the Northern Reaches"}
    mud_result = engine.resolve_turn(ws, 1, actions, agents)
    turn_result = engine.to_turn_result(mud_result)
    assert turn_result.turn_number == 1
    assert turn_result.scenario_type == "free_form_mud"
    assert "parsed_effects" in turn_result.resolution


def test_mud_engine_scene_frame_with_fracture():
    ws = make_world_state()
    ws.coalitions = [
        Coalition(id="c1", members=["agent_1"], state=CoalitionState.FRACTURE, formed_at_turn=1, trust_threshold=0.7)
    ]
    agents = make_agents()
    engine = MUDEngine()
    frame = engine.generate_scene_frame(ws, ["agent_1"], agents)
    assert "fractured" in frame


def test_mud_engine_scene_frame_high_entropy():
    ws = make_world_state(material_entropy=0.8, social_entropy=0.8)
    agents = make_agents()
    engine = MUDEngine()
    frame = engine.generate_scene_frame(ws, ["agent_1"], agents)
    assert "decay" in frame or "fraying" in frame
