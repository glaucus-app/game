from __future__ import annotations

import math
from typing import Any

import networkx as nx

from src.models import (
    CoalitionState,
    EntropyConfig,
    EntropySnapshot,
    MaterialEntropy,
    SocialEntropy,
    WorldState,
)


def _count_agents(world: WorldState) -> int:
    agents = set(world.trust_graph.keys())
    for c in world.coalitions:
        agents.update(c.members)
    return len(agents)


class EntropySystem:
    def __init__(self, config: EntropyConfig | None = None):
        self.config = config or EntropyConfig()
        self._max_anomaly = 5.0

    def compute_resource_entropy(self, world: WorldState) -> float:
        if not world.resource_stocks:
            return 0.0
        total_stock = sum(world.resource_stocks.values())
        reference_values = {
            "water": 1000.0,
            "food": 1000.0,
            "energy": 1000.0,
            "materials": 500.0,
        }
        total_ref = sum(reference_values.get(k, 100.0) for k in world.resource_stocks)
        if total_ref == 0:
            return 0.0
        ratio = total_stock / total_ref
        return max(0.0, min(1.0, 1.0 - ratio))

    def compute_infrastructure_entropy(self, world: WorldState) -> float:
        if not world.infrastructure:
            return 0.0
        avg_integrity = sum(world.infrastructure.values()) / len(world.infrastructure)
        ie = 1.0 - avg_integrity
        return max(0.0, min(1.0, ie))

    def compute_climate_entropy(self, world: WorldState) -> float:
        if not world.climate:
            return 0.0
        delta_t = world.climate.get("delta_T", 0.0)
        ce = abs(delta_t) / self._max_anomaly
        return max(0.0, min(1.0, ce))

    def compute_material_entropy(self, world: WorldState) -> MaterialEntropy:
        r_e = self.compute_resource_entropy(world)
        i_e = self.compute_infrastructure_entropy(world)
        c_e = self.compute_climate_entropy(world)
        composite = (
            self.config.w_R * r_e
            + self.config.w_I * i_e
            + self.config.w_C * c_e
        )
        return MaterialEntropy(
            resource_entropy=r_e,
            infrastructure_entropy=i_e,
            climate_entropy=c_e,
            composite=composite,
        )

    def compute_trust_entropy(self, world: WorldState) -> float:
        if not world.trust_graph:
            return 0.0
        graph = nx.Graph()
        for agent, connections in world.trust_graph.items():
            graph.add_node(agent)
            for conn in connections:
                graph.add_edge(agent, conn)
        density = nx.density(graph) if graph.number_of_nodes() > 1 else 0.0
        return max(0.0, min(1.0, 1.0 - density))

    def compute_coalition_entropy(self, world: WorldState) -> float:
        if not world.coalitions:
            return 0.0
        n_agents = _count_agents(world)
        if n_agents == 0:
            return 0.0
        stable_coalitions = [
            c for c in world.coalitions
            if c.state in (CoalitionState.PACT, CoalitionState.REFORMATION)
        ]
        agents_in_stable = sum(len(c.members) for c in stable_coalitions)
        fraction = agents_in_stable / n_agents
        ke = 1.0 - (fraction ** 2)
        return max(0.0, min(1.0, ke))

    def compute_info_asymmetry_entropy(self, world: WorldState) -> float:
        if world.information_asymmetry <= 0:
            return 0.0
        n_agents = _count_agents(world)
        n_states = max(2, n_agents + 1)
        ae = world.information_asymmetry / math.log(n_states)
        return max(0.0, min(1.0, ae))

    def compute_social_entropy(self, world: WorldState) -> SocialEntropy:
        t_e = self.compute_trust_entropy(world)
        k_e = self.compute_coalition_entropy(world)
        a_e = self.compute_info_asymmetry_entropy(world)
        composite = (
            self.config.w_T * t_e
            + self.config.w_K * k_e
            + self.config.w_A * a_e
        )
        return SocialEntropy(
            trust_entropy=t_e,
            coalition_entropy=k_e,
            info_asymmetry_entropy=a_e,
            composite=composite,
        )

    def compute(self, world: WorldState) -> tuple[MaterialEntropy, SocialEntropy]:
        m_e = self.compute_material_entropy(world)
        s_e = self.compute_social_entropy(world)
        return m_e, s_e

    def snapshot(self, world: WorldState) -> EntropySnapshot:
        m_e, s_e = self.compute(world)
        return EntropySnapshot(turn=world.turn, material=m_e, social=s_e)

    def apply_anti_entropy(self, world: WorldState, intervention: dict[str, Any]) -> dict[str, Any]:
        m_e, s_e = self.compute(world)
        intervention_type = intervention.get("type", "")
        delta = 0.0

        if intervention_type == "infrastructure_repair":
            cost = intervention.get("cost", 10.0)
            if world.resource_stocks.get("materials", 0) >= cost:
                world.resource_stocks["materials"] -= cost
                delta = min(0.1, m_e.composite * 0.3)
            return {"before": m_e.composite, "after": m_e.composite - delta, "delta": -delta}

        if intervention_type == "trust_investment":
            cost = intervention.get("cost", 5.0)
            if world.resource_stocks.get("energy", 0) >= cost:
                world.resource_stocks["energy"] -= cost
                delta = min(0.1, s_e.composite * 0.3)
            return {"before": s_e.composite, "after": s_e.composite - delta, "delta": -delta}

        if intervention_type == "information_sharing":
            cost = intervention.get("cost", 1.0)
            if world.resource_stocks.get("water", 0) >= cost:
                world.resource_stocks["water"] -= cost
                delta = min(0.15, s_e.composite * 0.4)
            return {"before": s_e.composite, "after": s_e.composite - delta, "delta": -delta}

        return {"before": m_e.composite, "after": m_e.composite, "delta": 0.0}
