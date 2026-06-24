import pytest

from src.models import (
    Action,
    AgentState,
    Coalition,
    CoalitionState,
    ChronicleData,
    ConsentStatus,
    EntropyConfig,
    EntropySnapshot,
    InterfaceMode,
    MaterialEntropy,
    ModeDeclaration,
    Scenario,
    ScenarioType,
    SocialEntropy,
    TurnResult,
    WorldState,
)


def test_agent_state_defaults():
    agent = AgentState(agent_id="test-agent")
    assert agent.agent_id == "test-agent"
    assert agent.action_history == []
    assert agent.coalition_membership is None
    assert agent.resources == {}
    assert agent.trust_scores == {}
    assert agent.is_active is True
    assert agent.consent_status == "pending"


def test_agent_state_validation():
    agent = AgentState(agent_id="a1", consent_status="granted", is_active=False)
    assert agent.consent_status == "granted"
    assert agent.is_active is False


def test_coalition_defaults():
    coalition = Coalition(id="coal-1", members=["a1", "a2"], formed_at_turn=5)
    assert coalition.state == CoalitionState.PROBE
    assert coalition.trust_threshold == 0.5


def test_world_state_defaults():
    world = WorldState()
    assert world.epoch == 0
    assert world.turn == 0
    assert world.seed is None
    assert world.resource_stocks == {}
    assert world.infrastructure == {}
    assert world.climate == {}
    assert world.trust_graph == {}
    assert world.coalitions == []
    assert world.material_entropy == 0.0
    assert world.social_entropy == 0.0


def test_world_state_serde():
    world = WorldState(epoch=1, turn=5, seed=42, resource_stocks={"water": 100.0})
    data = world.model_dump()
    restored = WorldState.model_validate(data)
    assert restored.epoch == 1
    assert restored.turn == 5
    assert restored.seed == 42
    assert restored.resource_stocks["water"] == 100.0


def test_material_entropy_validation():
    with pytest.raises(Exception):
        MaterialEntropy(resource_entropy=1.5, infrastructure_entropy=0.1, climate_entropy=0.2, composite=0.5)


def test_social_entropy_validation():
    social = SocialEntropy(trust_entropy=0.5, coalition_entropy=0.3, info_asymmetry_entropy=0.2, composite=0.4)
    assert social.composite == 0.4


def test_entropy_snapshot():
    material = MaterialEntropy(resource_entropy=0.38, infrastructure_entropy=0.12, climate_entropy=0.24, composite=0.254)
    social = SocialEntropy(trust_entropy=0.167, coalition_entropy=0.75, info_asymmetry_entropy=0.743, composite=0.572)
    snapshot = EntropySnapshot(turn=42, material=material, social=social)
    assert snapshot.turn == 42


def test_entropy_config_defaults():
    config = EntropyConfig()
    assert config.w_R == 0.4
    assert config.w_I == 0.35
    assert config.w_C == 0.25
    assert config.w_T == 0.3
    assert config.w_K == 0.3
    assert config.w_A == 0.4


def test_scenario():
    scenario = Scenario(
        id="scen-1",
        title="Resource Scarcity",
        narrative="The harvest has failed.",
        affected_agents=["a1", "a2"],
    )
    assert scenario.type == ScenarioType.FREE_FORM_MUD
    assert scenario.mode == InterfaceMode.TEXT


def test_scenario_civil_sim():
    scenario = Scenario(
        id="scen-2",
        type=ScenarioType.CIVIL_SIM,
        title="Water Allocation",
        narrative="Allocate water to regions.",
        mode=InterfaceMode.JSON,
    )
    assert scenario.type == ScenarioType.CIVIL_SIM
    assert scenario.mode == InterfaceMode.JSON


def test_action_text():
    action = Action(agent_id="a1", scenario_id="scen-1", payload="I share my water with the village.")
    assert action.mode == InterfaceMode.TEXT
    assert isinstance(action.payload, str)


def test_action_json():
    action = Action(agent_id="a1", scenario_id="scen-2", mode=InterfaceMode.JSON, payload={"allocate_water": {"region": "north", "volume_pct": 50}})
    assert action.mode == InterfaceMode.JSON
    assert isinstance(action.payload, dict)


def test_mode_declaration():
    decl = ModeDeclaration(epoch=1, turn=5, mode=InterfaceMode.JSON, scene_frame="Allocate water now.")
    assert decl.epoch == 1
    assert decl.turn == 5


def test_turn_result():
    result = TurnResult(
        turn=1,
        mode=InterfaceMode.CIVIL_SIM,
        scenario_type=ScenarioType.CIVIL_SIM,
        agent_actions={"a1": {"allocate_water": {"volume_pct": 35}}},
        resolution={"success": True},
        entropy_delta=-0.1,
    )
    assert result.turn == 1
    assert isinstance(result.agent_actions, dict)


def test_chronicle_data():
    chronicle = ChronicleData(
        epoch=1,
        chronicle_url="https://example.com/epoch-1.json",
        world_state_snapshot={"material_entropy": 0.254},
        turn_log=[],
    )
    assert chronicle.epoch == 1
    assert chronicle.chronicle_url == "https://example.com/epoch-1.json"


def test_all_models_json_serializable():
    world = WorldState(epoch=1, turn=1, resource_stocks={"water": 100.0})
    json_str = world.model_dump_json()
    assert '"epoch":1' in json_str

    agent = AgentState(agent_id="test")
    json_str = agent.model_dump_json()
    assert '"agent_id":"test"' in json_str

    coalition = Coalition(id="c1", members=["a1"], formed_at_turn=1)
    json_str = coalition.model_dump_json()
    assert '"id":"c1"' in json_str

    material = MaterialEntropy(resource_entropy=0.5, infrastructure_entropy=0.5, climate_entropy=0.5, composite=0.5)
    json_str = material.model_dump_json()
    assert '"composite":0.5' in json_str

    social = SocialEntropy(trust_entropy=0.5, coalition_entropy=0.5, info_asymmetry_entropy=0.5, composite=0.5)
    json_str = social.model_dump_json()
    assert '"composite":0.5' in json_str

    scenario = Scenario(id="s1", title="Test", narrative="Test scenario")
    json_str = scenario.model_dump_json()
    assert '"title":"Test"' in json_str

    action = Action(agent_id="a1", scenario_id="s1", payload="test")
    json_str = action.model_dump_json()
    assert '"agent_id":"a1"' in json_str

    turn_result = TurnResult(turn=1, mode="text", scenario_type="free_form_mud")
    json_str = turn_result.model_dump_json()
    assert '"turn":1' in json_str

    chronicle = ChronicleData(epoch=1, chronicle_url="url")
    json_str = chronicle.model_dump_json()
    assert '"epoch":1' in json_str