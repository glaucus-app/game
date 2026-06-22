import pytest
from src.engine.game import GameEngine
from src.models.world import Action, ActionType, Scenario


def test_register_agent():
    engine = GameEngine()
    engine.register_agent("agent1", "profile1")
    
    assert "agent1" in engine.world_state.agents
    assert engine.world_state.agents["agent1"].human_profile_ref == "profile1"
    assert engine.world_state.agents["agent1"].connected is True


def test_generate_scenario():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    scenario = engine.generate_scenario()
    
    assert isinstance(scenario, Scenario)
    assert len(scenario.affected_agents) >= 2
    assert scenario.id in [s.id for s in engine.world_state.active_scenarios]


def test_submit_action():
    engine = GameEngine()
    engine.register_agent("agent1")
    scenario = engine.generate_scenario(involved_agents=["agent1"])
    
    action = Action(
        agent_id="agent1",
        scenario_id=scenario.id,
        action_type=ActionType.BUILD
    )
    
    result = engine.submit_action("agent1", scenario.id, action)
    assert result is True
    assert action in engine.world_state.agents["agent1"].action_history


def test_resolve_interactions_full_cooperation():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    scenario = engine.generate_scenario(involved_agents=["agent1", "agent2"])
    
    action1 = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.COOPERATE)
    action2 = Action(agent_id="agent2", scenario_id=scenario.id, action_type=ActionType.COOPERATE)
    
    engine.submit_action("agent1", scenario.id, action1)
    engine.submit_action("agent2", scenario.id, action2)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "full_cooperation"
    assert outcome["entropy_change"] == -5


def test_resolve_interactions_partial_cooperation():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    engine.register_agent("agent3")
    
    scenario = engine.generate_scenario(involved_agents=["agent1", "agent2", "agent3"])
    
    action1 = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.COOPERATE)
    action2 = Action(agent_id="agent2", scenario_id=scenario.id, action_type=ActionType.COOPERATE)
    action3 = Action(agent_id="agent3", scenario_id=scenario.id, action_type=ActionType.COMPETE)
    
    engine.submit_action("agent1", scenario.id, action1)
    engine.submit_action("agent2", scenario.id, action2)
    engine.submit_action("agent3", scenario.id, action3)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "partial_cooperation"
    assert outcome["entropy_change"] == -2


def test_resolve_interactions_conflict():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    scenario = engine.generate_scenario(involved_agents=["agent1", "agent2"])
    
    action1 = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.DESTROY)
    action2 = Action(agent_id="agent2", scenario_id=scenario.id, action_type=ActionType.COMPETE)
    
    engine.submit_action("agent1", scenario.id, action1)
    engine.submit_action("agent2", scenario.id, action2)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "conflict"
    assert outcome["entropy_change"] == 6


def test_resolve_interactions_neutral():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    scenario = engine.generate_scenario(involved_agents=["agent1", "agent2"])
    
    action1 = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.NEUTRAL)
    action2 = Action(agent_id="agent2", scenario_id=scenario.id, action_type=ActionType.NEUTRAL)
    
    engine.submit_action("agent1", scenario.id, action1)
    engine.submit_action("agent2", scenario.id, action2)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "neutral"
    assert outcome["entropy_change"] == 1


def test_resolve_interactions_single_agent():
    engine = GameEngine()
    engine.register_agent("agent1")
    
    scenario = engine.generate_scenario(involved_agents=["agent1"])
    
    action = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.COOPERATE)
    engine.submit_action("agent1", scenario.id, action)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "constructive"
    assert outcome["entropy_change"] == -2


def test_tick_advances_time():
    engine = GameEngine()
    engine.register_agent("agent1")
    
    initial_turn = engine.world_state.turn
    initial_entropy = engine.world_state.entropy
    
    engine.tick()
    
    assert engine.world_state.turn == initial_turn + 1
    assert engine.world_state.entropy > initial_entropy


def test_tick_generates_scenario():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    initial_count = len(engine.world_state.active_scenarios)
    engine.tick()
    assert len(engine.world_state.active_scenarios) >= initial_count


def test_send_message_creates_scenario():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    action = engine.send_message("agent1", "agent2", "Hello!")
    
    assert action.action_type == ActionType.COMMUNICATE
    assert action.target_agent == "agent2"
    assert action.payload["message"] == "Hello!"
    assert len(engine.world_state.active_scenarios) == 1


def test_world_state_serialization():
    engine = GameEngine()
    engine.register_agent("agent1", "profile1")
    
    json_data = engine.to_json()
    
    restored = GameEngine.from_json(json_data)
    
    assert restored.world_state.epoch == engine.world_state.epoch
    assert len(restored.world_state.agents) == len(engine.world_state.agents)


def test_negotiate_as_action():
    engine = GameEngine()
    engine.register_agent("agent1")
    engine.register_agent("agent2")
    
    scenario = engine.generate_scenario(involved_agents=["agent1", "agent2"])
    
    action1 = Action(agent_id="agent1", scenario_id=scenario.id, action_type=ActionType.NEGOTIATE)
    action2 = Action(agent_id="agent2", scenario_id=scenario.id, action_type=ActionType.NEGOTIATE)
    
    engine.submit_action("agent1", scenario.id, action1)
    engine.submit_action("agent2", scenario.id, action2)
    
    outcome = engine.resolve_interactions(scenario.id)
    
    assert outcome["result"] == "negotiated"