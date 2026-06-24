from copy import deepcopy

import pytest

from src.encounters.civil_sim import (
    CivilSimConfig,
    CivilSimDelta,
    CivilSimEngine,
)
from src.models.coalition import Coalition, CoalitionState
from src.models.scenario import InterfaceMode, ScenarioType
from src.models.world import WorldState


@pytest.fixture
def engine() -> CivilSimEngine:
    return CivilSimEngine()


@pytest.fixture
def world_state() -> WorldState:
    return WorldState(
        epoch=1,
        turn=1,
        seed=42,
        resource_stocks={"water": 1000.0, "energy": 500.0},
        infrastructure={"region_a": 0.9, "region_b": 0.85},
        climate={"delta_T": 2.5},
        trust_graph={
            "agent_1": ["agent_2", "agent_3"],
            "agent_2": ["agent_1"],
            "agent_3": [],
        },
        coalitions=[
            Coalition(
                id="coalition_1",
                members=["agent_1", "agent_2"],
                state=CoalitionState.FRACTURE,
                formed_at_turn=5,
                trust_threshold=0.7,
            ),
            Coalition(
                id="coalition_2",
                members=["agent_3", "agent_4"],
                state=CoalitionState.PACT,
                formed_at_turn=3,
                trust_threshold=0.6,
            ),
        ],
        information_asymmetry=0.3,
        material_entropy=0.254,
        social_entropy=0.572,
        entropy_history=[],
    )


@pytest.fixture
def crisis_world_state() -> WorldState:
    return WorldState(
        epoch=2,
        turn=10,
        seed=99,
        resource_stocks={"water": 50.0, "energy": 100.0},
        infrastructure={"region_a": 0.2, "region_b": 0.4},
        climate={"delta_T": 4.5},
        trust_graph={
            "agent_1": ["agent_2"],
            "agent_2": [],
            "agent_3": [],
            "agent_4": [],
        },
        coalitions=[
            Coalition(
                id="coalition_1",
                members=["agent_1", "agent_2"],
                state=CoalitionState.FRACTURE,
                formed_at_turn=5,
                trust_threshold=0.7,
            ),
        ],
        information_asymmetry=0.6,
        material_entropy=0.6,
        social_entropy=0.7,
        entropy_history=[],
    )


def test_allocate_water(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "allocate_water", "volume_pct": 20.0, "region": "region_a", "recipient": "agent_1"}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert delta.resource_changes[0].resource == "water"
    assert delta.resource_changes[0].old_value == 1000.0
    assert delta.resource_changes[0].new_value == 800.0
    assert delta.resource_changes[0].change == -200.0
    
    assert len(delta.welfare_changes) == 1
    wc = delta.welfare_changes[0]
    assert wc.region == "region_a"
    assert wc.segment == "agent_1"
    assert wc.change == pytest.approx(2.0, abs=0.01)
    
    assert len(delta.forecast) > 0
    assert delta.forecast[0]["step"] == 1


def test_allocate_water_above_stock(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "allocate_water", "volume_pct": 150.0, "region": "region_a", "recipient": "agent_1"}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.resource_stocks["water"] == 0.0
    assert delta.resource_changes[0].new_value == 0.0


def test_allocate_water_no_recipient(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "allocate_water", "volume_pct": 50.0, "region": "region_a"}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.resource_stocks["water"] == 500.0
    assert delta.welfare_changes[0].segment == "general"


def test_invest_infrastructure(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "invest_infrastructure", "region": "region_a", "investment_amount": 10.0}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.infrastructure["region_a"] == 1.0
    assert delta.infrastructure_changes[0].old_integrity == 0.9
    assert delta.infrastructure_changes[0].new_integrity == 1.0
    assert delta.infrastructure_changes[0].change == pytest.approx(0.1, abs=0.001)
    
    assert len(delta.welfare_changes) == 1
    assert delta.welfare_changes[0].change == pytest.approx(0.02, abs=0.001)


def test_invest_infrastructure_capped(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "invest_infrastructure", "region": "region_a", "investment_amount": 100.0}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.infrastructure["region_a"] == 1.0
    assert delta.infrastructure_changes[0].new_integrity == 1.0


def test_set_policy_global(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "set_policy", "policy_type": "emission_target", "target_value": 0.8}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.climate["emission_target"] == 0.8
    assert delta.policy_changes[0].old_value is None
    assert delta.policy_changes[0].new_value == 0.8
    assert delta.policy_changes[0].region is None
    assert len(delta.policy_changes[0].horizon_effects) == 5
    
    step1 = delta.policy_changes[0].horizon_effects[0]
    assert step1["step"] == 1
    assert step1["effect_value"] == pytest.approx(0.64, abs=0.001)
    assert step1["region"] is None


def test_set_policy_regional(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "set_policy", "policy_type": "emission_target", "region": "region_a", "target_value": 0.6}
    
    delta = engine.process_action(ws, "agent_1", action)
    
    assert ws.climate["policy_emission_target_region_a"] == 0.6
    assert delta.policy_changes[0].region == "region_a"
    assert delta.policy_changes[0].new_value == 0.6


def test_tick_resource_depletion(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    initial_water = ws.resource_stocks["water"]
    
    delta = engine.tick(ws)
    
    assert ws.resource_stocks["water"] < initial_water
    assert len(delta.resource_changes) == 2
    water_change = [r for r in delta.resource_changes if r.resource == "water"][0]
    assert water_change.old_value == initial_water
    assert water_change.change < 0


def test_tick_infrastructure_decay(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    initial_region_a = ws.infrastructure["region_a"]
    
    delta = engine.tick(ws)
    
    assert ws.infrastructure["region_a"] < initial_region_a
    infra_change = [i for i in delta.infrastructure_changes if i.region == "region_a"][0]
    assert infra_change.old_integrity == initial_region_a
    assert infra_change.change < 0


def test_tick_welfare_delta(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    
    delta = engine.tick(ws)
    
    assert len(delta.welfare_changes) == 2
    for wc in delta.welfare_changes:
        assert wc.old_welfare > wc.new_welfare


def test_trigger_conditions_crisis(world_state: WorldState) -> None:
    engine = CivilSimEngine()
    ws = deepcopy(world_state)
    ws.resource_stocks["water"] = 50.0
    
    assert engine.should_trigger(ws) is True


def test_trigger_conditions_no_crisis(world_state: WorldState) -> None:
    engine = CivilSimEngine()
    ws = deepcopy(world_state)
    ws.coalitions = []
    
    assert engine.should_trigger(ws) is False


def test_trigger_conditions_high_tension(world_state: WorldState) -> None:
    engine = CivilSimEngine()
    ws = deepcopy(world_state)
    ws.resource_stocks["water"] = 10.0
    
    assert engine.should_trigger(ws) is True


def test_forecast_horizon(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "allocate_water", "volume_pct": 50.0, "region": "region_a", "recipient": "agent_1"}
    
    forecast = engine.forecast(ws, action, horizon=3)
    
    assert len(forecast) == 3
    assert forecast[0]["step"] == 1
    assert forecast[2]["step"] == 3
    
    assert forecast[0]["resource_stocks"]["water"] == pytest.approx(495.0, abs=0.001)
    assert forecast[0]["infrastructure"]["region_a"] == pytest.approx(0.8955, abs=0.001)


def test_forecast_decay_over_horizon(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    
    forecast = engine.forecast(ws, horizon=5)
    
    stock_step1 = forecast[0]["resource_stocks"]["water"]
    stock_step5 = forecast[4]["resource_stocks"]["water"]
    assert stock_step5 < stock_step1
    
    infra_step1 = forecast[0]["infrastructure"]["region_a"]
    infra_step5 = forecast[4]["infrastructure"]["region_a"]
    assert infra_step5 < infra_step1


def test_forecast_infrastructure_investment(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "invest_infrastructure", "region": "region_a", "investment_amount": 20.0}
    
    forecast = engine.forecast(ws, action, horizon=3)
    
    assert forecast[0]["infrastructure"]["region_a"] > 0.9


def test_generate_scenario(engine: CivilSimEngine, world_state: WorldState) -> None:
    scenario = engine.generate_scenario(world_state, ["agent_1", "agent_2"])
    
    assert scenario.type == ScenarioType.CIVIL_SIM
    assert scenario.mode == InterfaceMode.JSON
    assert scenario.affected_agents == ["agent_1", "agent_2"]
    assert "allocate_water" in scenario.action_schema
    assert "invest_infrastructure" in scenario.action_schema
    assert "set_policy" in scenario.action_schema
    assert scenario.deadline_seconds == 30


def test_generate_narrative_from_delta(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    action = {"action_type": "allocate_water", "volume_pct": 25.0, "region": "region_a", "recipient": "agent_1"}
    delta = engine.process_action(ws, "agent_1", action)
    
    narrative = engine.generate_narrative(delta)
    
    assert narrative.turn == 1
    assert "water" in narrative.summary.lower()
    assert len(narrative.highlights) > 0


def test_generate_narrative_empty_delta(engine: CivilSimEngine, world_state: WorldState) -> None:
    delta = CivilSimDelta(turn=1, agent_id="system", action={"action_type": "tick"})
    
    narrative = engine.generate_narrative(delta)
    
    assert narrative.summary == "No significant changes this tick."
    assert len(narrative.highlights) == 0


def test_civil_sim_config_defaults() -> None:
    config = CivilSimConfig()
    
    assert config.resource_depletion_rate == 0.02
    assert config.resource_replenish_rate == 0.01
    assert config.infrastructure_decay_rate == 0.005
    assert config.forecasting_horizon == 5
    assert config.water_threshold == 0.3
    assert config.political_tension_threshold == 0.5
    assert config.welfare_decay_rate == 0.01
    assert config.policy_strength_decay == pytest.approx(0.8, abs=0.001)


def test_policy_propagates_over_horizon(engine: CivilSimEngine) -> None:
    effects = engine._propagate_policy("emission_target", "region_a", 1.0)
    
    assert len(effects) == 5
    assert effects[0]["effect_value"] == pytest.approx(0.8, abs=0.001)
    assert effects[1]["effect_value"] == pytest.approx(0.64, abs=0.001)
    assert effects[2]["effect_value"] == pytest.approx(0.512, abs=0.001)


def test_political_tension_isolation(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    ws.trust_graph = {
        "agent_1": [],
        "agent_2": [],
        "agent_3": [],
    }
    
    tension = engine._compute_political_tension(ws)
    assert tension > 0.0


def test_political_tension_fracture(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    ws.coalitions = [
        Coalition(
            id="c1",
            members=["a", "b"],
            state=CoalitionState.FRACTURE,
            formed_at_turn=1,
            trust_threshold=0.5,
        ),
        Coalition(
            id="c2",
            members=["c", "d"],
            state=CoalitionState.FRACTURE,
            formed_at_turn=2,
            trust_threshold=0.5,
        ),
        Coalition(
            id="c3",
            members=["e", "f"],
            state=CoalitionState.FRACTURE,
            formed_at_turn=3,
            trust_threshold=0.5,
        ),
    ]
    
    tension = engine._compute_political_tension(ws)
    assert tension > 0.0


def test_political_tension_capped_at_one(engine: CivilSimEngine, world_state: WorldState) -> None:
    ws = deepcopy(world_state)
    ws.coalitions = [
        Coalition(
            id=f"c{i}",
            members=[f"a{i}", f"b{i}"],
            state=CoalitionState.FRACTURE,
            formed_at_turn=i,
            trust_threshold=0.5,
        )
        for i in range(10)
    ]
    ws.trust_graph = {f"agent_{i}": [] for i in range(20)}
    
    tension = engine._compute_political_tension(ws)
    assert tension <= 1.0


def test_tick_empty_world(engine: CivilSimEngine) -> None:
    ws = WorldState(epoch=1, turn=1)
    delta = engine.tick(ws)
    
    assert len(delta.resource_changes) == 0
    assert len(delta.infrastructure_changes) == 0
    assert len(delta.welfare_changes) == 0