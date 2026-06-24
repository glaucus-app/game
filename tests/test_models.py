import json

from src.models.coalition import Coalition, CoalitionState
from src.models.chronicle import ChronicleData
from src.models.entropy import EntropyConfig, EntropySnapshot, MaterialEntropy, SocialEntropy
from src.models.scenario import (
    Action,
    EnvironmentalPressure,
    InterfaceMode,
    ModeDeclaration,
    Scenario,
    ScenarioType,
)
from src.models.world import AgentState, ConsentStatus, TurnResult, WorldState


def test_coalition_state():
    assert CoalitionState.PROBE.value == "probe"
    assert CoalitionState.PACT.value == "pact"
    assert CoalitionState.FRACTURE.value == "fracture"
    assert CoalitionState.REFORMATION.value == "reformation"


def test_coalition():
    c = Coalition(
        id="coalition_1",
        members=["agent_1", "agent_2"],
        state=CoalitionState.PACT,
        formed_at_turn=5,
        trust_threshold=0.8,
    )
    assert c.id == "coalition_1"
    assert c.members == ["agent_1", "agent_2"]
    data = c.model_dump()
    c2 = Coalition.model_validate(data)
    assert c2.state == CoalitionState.PACT


def test_material_entropy():
    me = MaterialEntropy(
        resource_entropy=0.38,
        infrastructure_entropy=0.12,
        climate_entropy=0.24,
        composite=0.254,
    )
    data = me.model_dump()
    assert data["composite"] == 0.254
    me2 = MaterialEntropy.model_validate(data)
    assert me2.resource_entropy == 0.38


def test_social_entropy():
    se = SocialEntropy(
        trust_entropy=0.167,
        coalition_entropy=0.75,
        info_asymmetry_entropy=0.743,
        composite=0.572,
    )
    data = se.model_dump()
    assert data["composite"] == 0.572


def test_entropy_snapshot():
    me = MaterialEntropy(resource_entropy=0.38, infrastructure_entropy=0.12, climate_entropy=0.24, composite=0.254)
    se = SocialEntropy(trust_entropy=0.167, coalition_entropy=0.75, info_asymmetry_entropy=0.743, composite=0.572)
    snap = EntropySnapshot(turn=1, material=me, social=se)
    data = snap.model_dump()
    snap2 = EntropySnapshot.model_validate(data)
    assert snap2.turn == 1


def test_entropy_config():
    config = EntropyConfig()
    assert config.w_R == 0.4
    assert config.w_I == 0.35
    assert config.w_C == 0.25
    assert config.w_T == 0.3
    assert config.w_K == 0.3
    assert config.w_A == 0.4


def test_scenario_type():
    assert ScenarioType.FREE_FORM_MUD.value == "free_form_mud"
    assert ScenarioType.CIVIL_SIM.value == "civil_sim"
    assert ScenarioType.GAME_THEORY.value == "game_theory"
    assert ScenarioType.ECONOMY.value == "economy"


def test_interface_mode():
    assert InterfaceMode.TEXT.value == "text"
    assert InterfaceMode.JSON.value == "json"
    assert InterfaceMode.PING.value == "ping"


def test_scenario():
    pressure = EnvironmentalPressure(urgency=0.5, stakes=0.7, complexity=0.3)
    s = Scenario(
        id="scenario_1",
        type=ScenarioType.CIVIL_SIM,
        title="Resource Allocation Crisis",
        narrative="A severe drought has struck the region...",
        mode=InterfaceMode.JSON,
        affected_agents=["agent_1", "agent_2"],
        environmental_pressure=pressure,
        deadline_seconds=30,
    )
    data = s.model_dump()
    json_str = s.model_dump_json()
    s2 = Scenario.model_validate_json(json_str)
    assert s2.title == "Resource Allocation Crisis"


def test_mode_declaration():
    md = ModeDeclaration(
        epoch=1,
        turn=5,
        mode=InterfaceMode.JSON,
        scene_frame="The world faces a critical decision...",
        deadline_seconds=60,
    )
    data = md.model_dump()
    assert data["epoch"] == 1


def test_action():
    a = Action(
        agent_id="agent_1",
        scenario_id="scenario_1",
        mode=InterfaceMode.TEXT,
        payload="I investigate the situation",
        timestamp=12345.0,
    )
    data = a.model_dump()
    a2 = Action.model_validate(data)
    assert a2.agent_id == "agent_1"


def test_agent_state():
    a = AgentState(
        agent_id="agent_1",
        action_history=["action_1", "action_2"],
        resources={"water": 100.0, "energy": 50.0},
        trust_scores={"agent_2": 0.8, "agent_3": 0.6},
        is_active=True,
        consent_status=ConsentStatus.GRANTED,
    )
    data = a.model_dump()
    a2 = AgentState.model_validate(data)
    assert a2.consent_status == ConsentStatus.GRANTED


def test_turn_result():
    tr = TurnResult(
        turn_number=5,
        mode="civil_sim",
        scenario_type="civil_sim",
        agent_actions={"agent_1": "alloc_water", "agent_2": "alloc_water"},
        resolution={"water_allocated": 50.0},
        entropy_delta=0.15,
        timestamp=12345.0,
    )
    data = tr.model_dump()
    tr2 = TurnResult.model_validate(data)
    assert tr2.turn_number == 5


def test_world_state():
    ws = WorldState(
        epoch=1,
        turn=5,
        seed=42,
        resource_stocks={"water": 1000.0, "energy": 500.0},
        infrastructure={"region_a": 0.9, "region_b": 0.85},
        climate={"delta_T": 2.5},
        trust_graph={"agent_1": ["agent_2", "agent_3"]},
        information_asymmetry=0.3,
        material_entropy=0.254,
        social_entropy=0.572,
    )
    data = ws.model_dump()
    ws2 = WorldState.model_validate(data)
    assert ws2.epoch == 1
    assert ws2.seed == 42


def test_chronicle_data():
    me = MaterialEntropy(resource_entropy=0.38, infrastructure_entropy=0.12, climate_entropy=0.24, composite=0.254)
    se = SocialEntropy(trust_entropy=0.167, coalition_entropy=0.75, info_asymmetry_entropy=0.743, composite=0.572)
    snap = EntropySnapshot(turn=1, material=me, social=se)
    cd = ChronicleData(
        epoch=1,
        chronicle_url="https://example.com/chronicle/1",
        world_state_snapshot={"epoch": 1, "turn": 10},
        entropy_history=[snap],
        turn_log=[{"turn_number": 1, "mode": "civil_sim"}],
        encounter_outcomes=[{"type": "civil_sim", "outcome": "resolved"}],
        toe_discovery=None,
    )
    data = cd.model_dump()
    cd2 = ChronicleData.model_validate(data)
    assert cd2.epoch == 1


def test_json_serializable():
    ws = WorldState(epoch=1, turn=1)
    json_str = ws.model_dump_json()
    data = json.loads(json_str)
    assert data["epoch"] == 1