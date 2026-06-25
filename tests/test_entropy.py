import math

from src.engine.entropy import EntropySystem
from src.models import (
    Coalition,
    CoalitionState,
    WorldState,
)


def test_entropy_system_compute_example():
    world = WorldState(
        epoch=7,
        turn=42,
        resource_stocks={"water": 620.0, "food": 620.0},
        infrastructure={"north": 0.88, "south": 0.88, "east": 0.88, "west": 0.88},
        climate={"delta_T": 1.2},
        trust_graph={
            "a1": ["a2", "a3", "a4"],
            "a2": ["a1", "a3"],
            "a3": ["a1", "a2", "a4"],
            "a4": ["a1", "a3"],
        },
        coalitions=[
            Coalition(id="c1", members=["a1", "a2"], state=CoalitionState.PACT, formed_at_turn=40, trust_threshold=0.5)
        ],
        information_asymmetry=0.81,
    )

    system = EntropySystem()
    m_e, s_e = system.compute(world)

    r_e = 1.0 - (1240 / 2000)
    assert math.isclose(r_e, 0.38, abs_tol=0.01)

    i_e = 1.0 - 0.88
    assert math.isclose(i_e, 0.12, abs_tol=0.01)

    c_e = abs(1.2) / 5.0
    assert math.isclose(c_e, 0.24, abs_tol=0.01)

    assert math.isclose(m_e.composite, 0.254, abs_tol=0.01)
    assert math.isclose(s_e.composite, 0.476, abs_tol=0.01)


def test_infrastructure_repair_intervention():
    world = WorldState(
        resource_stocks={"materials": 100.0},
        infrastructure={"north": 0.5},
        climate={"delta_T": 0.0},
    )
    system = EntropySystem()

    result = system.apply_anti_entropy(world, {"type": "infrastructure_repair", "cost": 10.0})

    assert "before" in result
    assert "after" in result
    assert "delta" in result
    assert result["after"] < result["before"]
    assert result["delta"] < 0


def test_trust_investment_intervention():
    world = WorldState(
        resource_stocks={"energy": 100.0},
        trust_graph={"a1": ["a2"]},
        coalitions=[],
        information_asymmetry=0.5,
    )
    system = EntropySystem()

    result = system.apply_anti_entropy(world, {"type": "trust_investment", "cost": 5.0})

    assert result["after"] < result["before"]
    assert result["delta"] < 0


def test_information_sharing_intervention():
    world = WorldState(
        resource_stocks={"water": 100.0},
        trust_graph={"a1": ["a2"]},
        coalitions=[],
        information_asymmetry=0.8,
    )
    system = EntropySystem()

    result = system.apply_anti_entropy(world, {"type": "information_sharing", "cost": 1.0})

    assert result["after"] < result["before"]
    assert result["delta"] < 0


def test_determinism():
    world1 = WorldState(
        resource_stocks={"water": 500.0},
        infrastructure={"north": 0.75},
        climate={"delta_T": 2.0},
    )
    world2 = WorldState(
        resource_stocks={"water": 500.0},
        infrastructure={"north": 0.75},
        climate={"delta_T": 2.0},
    )

    system = EntropySystem()
    m_e1, s_e1 = system.compute(world1)
    m_e2, s_e2 = system.compute(world2)

    assert m_e1.composite == m_e2.composite
    assert s_e1.composite == s_e2.composite


def test_snapshot_returns_correct_turn():
    world = WorldState(turn=10, resource_stocks={"water": 500.0})
    system = EntropySystem()
    snapshot = system.snapshot(world)

    assert snapshot.turn == 10
