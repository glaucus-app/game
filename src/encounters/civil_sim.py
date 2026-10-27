from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.models.coalition import Coalition
from src.models.scenario import (
    EnvironmentalPressure,
    InterfaceMode,
    Scenario,
    ScenarioType,
)
from src.models.world import WorldState


class CivilSimConfig(BaseModel):
    resource_depletion_rate: float = Field(default=0.02, ge=0.0)
    resource_replenish_rate: float = Field(default=0.01, ge=0.0)
    infrastructure_decay_rate: float = Field(default=0.005, ge=0.0)
    forecasting_horizon: int = Field(default=5, ge=1)
    water_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    political_tension_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    resource_reference_values: dict[str, float] = Field(default_factory=lambda: {"water": 1000.0})
    welfare_decay_rate: float = Field(default=0.01, ge=0.0)
    policy_strength_decay: float = Field(default=0.8, ge=0.0, le=1.0)


class ResourceDelta(BaseModel):
    resource: str
    old_value: float
    new_value: float
    change: float


class InfrastructureDelta(BaseModel):
    region: str
    old_integrity: float
    new_integrity: float
    change: float


class PolicyDelta(BaseModel):
    policy_type: str
    region: str | None
    old_value: float | None
    new_value: float
    horizon_effects: list[dict[str, Any]] = Field(default_factory=list)


class WelfareDelta(BaseModel):
    region: str
    segment: str
    old_welfare: float
    new_welfare: float
    change: float


class CivilSimDelta(BaseModel):
    turn: int
    agent_id: str
    action: dict[str, Any]
    resource_changes: list[ResourceDelta] = Field(default_factory=list)
    infrastructure_changes: list[InfrastructureDelta] = Field(default_factory=list)
    policy_changes: list[PolicyDelta] = Field(default_factory=list)
    welfare_changes: list[WelfareDelta] = Field(default_factory=list)
    forecast: list[dict[str, Any]] = Field(default_factory=list)


class CivilSimNarrative(BaseModel):
    turn: int
    summary: str
    highlights: list[str] = Field(default_factory=list)


class CivilSimEngine:
    def __init__(self, config: CivilSimConfig | None = None) -> None:
        self.config = config or CivilSimConfig()

    def should_trigger(self, world_state: WorldState) -> bool:
        water_stock = world_state.resource_stocks.get("water", 0.0)
        water_reference = self.config.resource_reference_values.get("water", 1000.0)
        resource_below = water_stock <= water_reference * self.config.water_threshold
        
        political_tension = self._compute_political_tension(world_state)
        tension_above = political_tension >= self.config.political_tension_threshold
        
        return resource_below and tension_above

    def _compute_political_tension(self, world_state: WorldState) -> float:
        coalitions: list[Coalition] = world_state.coalitions
        fracture_count = sum(1 for c in coalitions if c.state.value == "fracture")
        
        trust_graph = world_state.trust_graph
        isolated_count = sum(1 for agents in trust_graph.values() if len(agents) == 0)
        total_agents = len(trust_graph)
        isolation_ratio = isolated_count / total_agents if total_agents > 0 else 0.0
        
        tension = min(1.0, (fracture_count * 0.3) + (isolation_ratio * 0.5) + (len(coalitions) * 0.1))
        return tension

    def process_action(self, world_state: WorldState, agent_id: str, action: dict[str, Any]) -> CivilSimDelta:
        action_type = action.get("action_type", "")
        delta = CivilSimDelta(turn=world_state.turn, agent_id=agent_id, action=action)
        
        if action_type == "allocate_water":
            self._apply_allocate_water(world_state, action, delta)
        elif action_type == "invest_infrastructure":
            self._apply_invest_infrastructure(world_state, action, delta)
        elif action_type == "set_policy":
            self._apply_set_policy(world_state, action, delta)
        
        delta.forecast = self.forecast(world_state, action)
        return delta

    def _apply_allocate_water(self, world_state: WorldState, action: dict[str, Any], delta: CivilSimDelta) -> None:
        volume_pct = action.get("volume_pct", 0.0) / 100.0
        region = action.get("region", "")
        recipient = action.get("recipient", "")
        
        current_stock = world_state.resource_stocks.get("water", 0.0)
        allocate_amount = current_stock * volume_pct
        
        if allocate_amount > current_stock:
            allocate_amount = current_stock
        
        new_stock = max(0.0, current_stock - allocate_amount)
        world_state.resource_stocks["water"] = new_stock
        
        delta.resource_changes.append(ResourceDelta(
            resource="water",
            old_value=current_stock,
            new_value=new_stock,
            change=-allocate_amount,
        ))
        
        welfare_delta = allocate_amount * 0.01
        delta.welfare_changes.append(WelfareDelta(
            region=region,
            segment=recipient or "general",
            old_welfare=0.5,
            new_welfare=0.5 + welfare_delta,
            change=welfare_delta,
        ))

    def _apply_invest_infrastructure(self, world_state: WorldState, action: dict[str, Any], delta: CivilSimDelta) -> None:
        region = action.get("region", "")
        amount = action.get("investment_amount", 0.0)
        
        current_integrity = world_state.infrastructure.get(region, 1.0)
        repair_amount = min(amount * 0.05, 1.0 - current_integrity)
        new_integrity = min(1.0, current_integrity + repair_amount)
        
        world_state.infrastructure[region] = new_integrity
        
        delta.infrastructure_changes.append(InfrastructureDelta(
            region=region,
            old_integrity=current_integrity,
            new_integrity=new_integrity,
            change=repair_amount,
        ))
        
        welfare_delta = repair_amount * 0.2
        delta.welfare_changes.append(WelfareDelta(
            region=region,
            segment="general",
            old_welfare=0.5,
            new_welfare=0.5 + welfare_delta,
            change=welfare_delta,
        ))

    def _apply_set_policy(self, world_state: WorldState, action: dict[str, Any], delta: CivilSimDelta) -> None:
        policy_type = action.get("policy_type", "")
        region = action.get("region")
        target_value = action.get("target_value", 0.0)
        
        old_value: Any = world_state.climate.get(policy_type) if region is None else world_state.infrastructure.get(f"policy_{policy_type}_{region}")
        
        if region is not None:
            policy_key = f"policy_{policy_type}_{region}"
            world_state.climate[policy_key] = target_value
        else:
            world_state.climate[policy_type] = target_value
            
        delta.policy_changes.append(PolicyDelta(
            policy_type=policy_type,
            region=region,
            old_value=old_value,
            new_value=target_value,
            horizon_effects=self._propagate_policy(policy_type, region, target_value),
        ))

    def _propagate_policy(self, policy_type: str, region: str | None, value: float) -> list[dict[str, Any]]:
        horizon_effects = []
        current_value = value
        
        for step in range(1, self.config.forecasting_horizon + 1):
            current_value = current_value * self.config.policy_strength_decay
            effect = {
                "step": step,
                "policy_type": policy_type,
                "region": region,
                "effect_value": round(current_value, 4),
            }
            horizon_effects.append(effect)
        
        return horizon_effects

    def tick(self, world_state: WorldState) -> CivilSimDelta:
        delta = CivilSimDelta(turn=world_state.turn, agent_id="system", action={"action_type": "tick"})
        
        for resource in list(world_state.resource_stocks.keys()):
            old_stock = world_state.resource_stocks[resource]
            depletion = old_stock * self.config.resource_depletion_rate
            replenishment = old_stock * self.config.resource_replenish_rate
            new_stock = max(0.0, old_stock - depletion + replenishment)
            world_state.resource_stocks[resource] = new_stock
            
            delta.resource_changes.append(ResourceDelta(
                resource=resource,
                old_value=old_stock,
                new_value=new_stock,
                change=new_stock - old_stock,
            ))
        
        for region in list(world_state.infrastructure.keys()):
            old_integrity = world_state.infrastructure[region]
            decay = old_integrity * self.config.infrastructure_decay_rate
            new_integrity = max(0.0, old_integrity - decay)
            world_state.infrastructure[region] = new_integrity
            
            delta.infrastructure_changes.append(InfrastructureDelta(
                region=region,
                old_integrity=old_integrity,
                new_integrity=new_integrity,
                change=-decay,
            ))
            
            welfare_change = -decay * self.config.welfare_decay_rate
            delta.welfare_changes.append(WelfareDelta(
                region=region,
                segment="general",
                old_welfare=0.5 + (old_integrity * 0.5),
                new_welfare=0.5 + (new_integrity * 0.5),
                change=welfare_change,
            ))
        
        return delta

    def forecast(self, world_state: WorldState, action: dict[str, Any] | None = None, horizon: int | None = None) -> list[dict[str, Any]]:
        h = horizon or self.config.forecasting_horizon
        forecast_steps = []
        
        projected_stocks = dict(world_state.resource_stocks)
        projected_infra = dict(world_state.infrastructure)
        
        if action:
            action_type = action.get("action_type", "")
            if action_type == "allocate_water":
                volume_pct = action.get("volume_pct", 0.0) / 100.0
                water = projected_stocks.get("water", 0.0)
                projected_stocks["water"] = max(0.0, water * (1 - volume_pct))
            elif action_type == "invest_infrastructure":
                region = action.get("region", "")
                amount = action.get("investment_amount", 0.0)
                current = projected_infra.get(region, 1.0)
                projected_infra[region] = min(1.0, current + min(amount * 0.05, 1.0 - current))
        
        for step in range(1, h + 1):
            for resource in list(projected_stocks.keys()):
                projected_stocks[resource] = max(0.0, projected_stocks[resource] * (1 - self.config.resource_depletion_rate + self.config.resource_replenish_rate))
            
            for region in list(projected_infra.keys()):
                projected_infra[region] = max(0.0, projected_infra[region] * (1 - self.config.infrastructure_decay_rate))
            
            forecast_steps.append({
                "step": step,
                "resource_stocks": dict(projected_stocks),
                "infrastructure": dict(projected_infra),
            })
        
        return forecast_steps

    def generate_scenario(self, world_state: WorldState, agent_ids: list[str]) -> Scenario:
        pressure = EnvironmentalPressure(
            urgency=0.7,
            stakes=0.8,
            complexity=0.6,
        )
        return Scenario(
            id=f"civil_sim_{world_state.turn}",
            type=ScenarioType.CIVIL_SIM,
            title="Civil-Simulation: Resource & Policy Management",
            narrative=self._generate_narrative(world_state),
            mode=InterfaceMode.JSON,
            action_schema={
                "allocate_water": {
                    "volume_pct": "float (0-100)",
                    "region": "str",
                    "recipient": "str",
                },
                "invest_infrastructure": {
                    "region": "str",
                    "investment_amount": "float",
                },
                "set_policy": {
                    "policy_type": "str",
                    "region": "str (optional)",
                    "target_value": "float",
                },
            },
            affected_agents=agent_ids,
            environmental_pressure=pressure,
            deadline_seconds=30,
        )

    def _generate_narrative(self, world_state: WorldState) -> str:
        parts = []
        water = world_state.resource_stocks.get("water", 0.0)
        if water < 500.0:
            parts.append(f"Water reserves critically low at {water:.1f} units.")
        
        for region, integrity in world_state.infrastructure.items():
            if integrity < 0.5:
                parts.append(f"Infrastructure in {region} degraded to {integrity:.1%} integrity.")
        
        if not parts:
            parts.append("The civil-simulation session begins. Managing resources, infrastructure, and policy.")
        
        return " ".join(parts)

    def generate_narrative(self, delta: CivilSimDelta) -> CivilSimNarrative:
        parts = []
        highlights = []
        
        for rc in delta.resource_changes:
            parts.append(f"Resource {rc.resource}: {rc.old_value:.1f} -> {rc.new_value:.1f} ({rc.change:+.1f}).")
            highlights.append(f"{rc.resource} changed by {rc.change:+.1f}")
        
        for ic in delta.infrastructure_changes:
            parts.append(f"Infrastructure {ic.region}: {ic.old_integrity:.2f} -> {ic.new_integrity:.2f} ({ic.change:+.2f}).")
            highlights.append(f"{ic.region} integrity {ic.change:+.2f}")
        
        for pc in delta.policy_changes:
            parts.append(f"Policy {pc.policy_type} in {pc.region or 'global'}: set to {pc.new_value}.")
            highlights.append(f"{pc.policy_type} policy updated")
        
        for wc in delta.welfare_changes:
            parts.append(f"Welfare in {wc.region} ({wc.segment}): {wc.change:+.4f}.")
        
        if not parts:
            parts.append("No significant changes this tick.")
        
        return CivilSimNarrative(
            turn=delta.turn,
            summary=" ".join(parts),
            highlights=highlights,
        )