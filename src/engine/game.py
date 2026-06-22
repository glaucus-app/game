import random
from typing import Optional
from pydantic import BaseModel
from uuid import uuid4
from src.models.world import Scenario, Action, AgentState, WorldState, ActionType


class GameEngine:
    def __init__(self, world_state: Optional[WorldState] = None):
        self.world_state = world_state or WorldState()

    def register_agent(self, agent_id: str, human_profile_ref: Optional[str] = None) -> None:
        if agent_id not in self.world_state.agents:
            self.world_state.agents[agent_id] = AgentState(
                agent_id=agent_id,
                human_profile_ref=human_profile_ref,
                position=(random.randint(0, 10), random.randint(0, 10))
            )

    def generate_scenario(self, involved_agents: Optional[list[str]] = None) -> Scenario:
        all_agents = list(self.world_state.agents.keys())
        if not all_agents:
            raise ValueError("No agents registered")

        count = min(random.randint(2, max(2, len(all_agents))), len(all_agents))
        agents_involved = involved_agents or random.sample(all_agents, count)

        titles = [
            "Resource Shortage",
            "Territorial Dispute",
            "Natural Disaster",
            "Trade Negotiation",
            "Knowledge Exchange",
            "Infrastructure Crisis"
        ]

        narratives = [
            "Critical resources are running low in the region.",
            "Borders have been crossed, tensions rise.",
            "A disaster threatens the community.",
            "Opportunity for mutual benefit through exchange.",
            "Wisdom can be shared between agents.",
            "The foundational systems are failing."
        ]

        pressures = [
            {"urgency": random.uniform(0.5, 1.0), "stakes": random.uniform(0.3, 0.8), "complexity": random.uniform(0.2, 0.6)},
            {"urgency": random.uniform(0.3, 0.7), "stakes": random.uniform(0.6, 1.0), "complexity": random.uniform(0.4, 0.9)},
            {"urgency": random.uniform(0.8, 1.0), "stakes": random.uniform(0.5, 1.0), "complexity": random.uniform(0.3, 0.7)}
        ]

        idx = random.randint(0, len(titles) - 1)
        scenario = Scenario(
            id=str(uuid4()),
            title=titles[idx],
            narrative=narratives[idx],
            affected_agents=agents_involved,
            available_actions=[a.value for a in ActionType],
            environmental_pressure=pressures[idx % len(pressures)]
        )
        self.world_state.active_scenarios.append(scenario)
        return scenario

    def submit_action(self, agent_id: str, scenario_id: str, action: Action) -> bool:
        if agent_id not in self.world_state.agents:
            raise ValueError(f"Agent {agent_id} not registered")

        scenario = next((s for s in self.world_state.active_scenarios if s.id == scenario_id), None)
        if scenario is None:
            raise ValueError(f"Scenario {scenario_id} not found")

        if agent_id not in scenario.affected_agents:
            raise ValueError(f"Agent {agent_id} not involved in scenario {scenario_id}")

        self.world_state.agents[agent_id].action_history.append(action)
        return True

    def resolve_interactions(self, scenario_id: str) -> dict:
        scenario = next((s for s in self.world_state.active_scenarios if s.id == scenario_id), None)
        if scenario is None:
            raise ValueError(f"Scenario {scenario_id} not found")

        actions_by_agent = {}
        for agent_id in scenario.affected_agents:
            agent_actions = [a for a in self.world_state.agents[agent_id].action_history if a.scenario_id == scenario_id]
            if agent_actions:
                actions_by_agent[agent_id] = agent_actions[-1]

        if not actions_by_agent:
            outcome = {"entropy_change": 0, "result": "no_action"}
        else:
            outcome = self._compute_outcome(actions_by_agent)

        self.world_state.active_scenarios.remove(scenario)
        resolved = {
            "scenario_id": scenario_id,
            "actions": actions_by_agent,
            "outcome": outcome,
            "turn": self.world_state.turn,
            "epoch": self.world_state.epoch
        }
        self.world_state.resolved_scenarios.append(resolved)
        return outcome

    def _compute_outcome(self, actions: dict[str, Action]) -> dict:
        if len(actions) == 1:
            action = list(actions.values())[0]
            return self._single_action_outcome(action)

        action_types = [a.action_type for a in actions.values()]
        
        cooperators = [aid for aid, a in actions.items() if a.action_type in (ActionType.COOPERATE, ActionType.SHARE, ActionType.BUILD)]
        communicators = [aid for aid, a in actions.items() if a.action_type in (ActionType.COMMUNICATE, ActionType.NEGOTIATE)]

        if len(cooperators) >= len(actions):
            return {"entropy_change": -5, "result": "full_cooperation", "bonus": "negentropy"}
        
        if len(cooperators) > 0 and len(cooperators) < len(actions):
            return {"entropy_change": -2, "result": "partial_cooperation", "bonus": "modest_negentropy"}

        destroyers = [aid for aid, a in actions.items() if a.action_type in (ActionType.DESTROY, ActionType.COMPETE)]
        if len(destroyers) > 0:
            return {"entropy_change": min(len(destroyers) * 3, 10), "result": "conflict", "penalty": "chaos"}

        if len(communicators) > 0 and len(communicators) == len(actions):
            return {"entropy_change": -1, "result": "negotiated", "bonus": "tension_reduced"}

        return {"entropy_change": 1, "result": "neutral"}

    def _single_action_outcome(self, action: Action) -> dict:
        if action.action_type in (ActionType.COOPERATE, ActionType.SHARE, ActionType.BUILD):
            return {"entropy_change": -2, "result": "constructive"}
        if action.action_type in (ActionType.DESTROY, ActionType.COMPETE):
            return {"entropy_change": 3, "result": "destructive"}
        return {"entropy_change": 0, "result": "neutral"}

    def tick(self) -> None:
        self.world_state.turn += 1
        self.world_state.entropy += random.uniform(0.5, 2)
        self.world_state.entropy = min(100.0, self.world_state.entropy)

        if self.world_state.entropy < 100:
            count = min(3, len(self.world_state.agents))
            if count >= 2:
                self.generate_scenario()

    def get_pending_scenarios(self) -> list[Scenario]:
        return self.world_state.active_scenarios

    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        return self.world_state.agents.get(agent_id)

    def send_message(self, from_agent: str, to_agent: str, content: str) -> Action:
        if from_agent not in self.world_state.agents or to_agent not in self.world_state.agents:
            raise ValueError("Agent not found")

        scenario = Scenario(
            id=str(uuid4()),
            title="Direct Communication",
            narrative=f"{from_agent} sends a message to {to_agent}",
            affected_agents=[from_agent, to_agent],
            available_actions=[ActionType.COMMUNICATE.value, ActionType.NEGOTIATE.value],
            environmental_pressure={"urgency": 0.2, "stakes": 0.3, "complexity": 0.1}
        )
        self.world_state.active_scenarios.append(scenario)

        action = Action(
            agent_id=from_agent,
            scenario_id=scenario.id,
            action_type=ActionType.COMMUNICATE,
            target_agent=to_agent,
            payload={"message": content}
        )
        return action

    def to_json(self) -> str:
        return self.world_state.to_json()

    @classmethod
    def from_json(cls, data: str) -> "GameEngine":
        world_state = WorldState.from_json(data)
        return cls(world_state)