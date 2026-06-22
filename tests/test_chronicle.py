import json
from pathlib import Path

import pytest

from src.engine.chronicle import ChronicleWriter
from src.models.chronicle import AgentAction, AgentPerformance, EpochHistory, TurnSummary


def _make_history() -> EpochHistory:
    return EpochHistory(
        epoch_number=1,
        civilization_name="Aethelgard",
        start_date="2026-01-01T00:00:00Z",
        end_date="2026-06-22T05:39:58Z",
        initial_world_state={"entropy": 0.0, "resources": 100},
        final_entropy=100.0,
        entropy_graph=[(0, 0.0), (5, 12.0), (10, 45.0), (15, 78.0), (20, 100.0)],
        turns=[
            TurnSummary(
                turn=1,
                scenario="Resource scarcity grips the capital",
                affected_agents=["Socrates", "Plato"],
                actions=[
                    AgentAction(
                        agent_id="Socrates",
                        action="share resources with Plato",
                        outcome="Cooperation bonus",
                        entropy_delta=-2.0,
                    ),
                    AgentAction(
                        agent_id="Plato",
                        action="hoard supplies",
                        outcome="Conflict",
                        entropy_delta=3.0,
                    ),
                ],
                entropy_before=0.0,
                entropy_after=1.0,
            ),
            TurnSummary(
                turn=2,
                scenario="Crisis deepens",
                affected_agents=["Socrates", "Plato", "Aristotle"],
                actions=[
                    AgentAction(
                        agent_id="Aristotle",
                        action="propose mediation",
                        outcome="Partial accord",
                        entropy_delta=-1.0,
                    ),
                ],
                entropy_before=1.0,
                entropy_after=0.0,
            ),
        ],
        agents=["Socrates", "Plato", "Aristotle"],
        human_profiles={
            "Socrates": "guided by the cooperative spirit of their human",
            "Plato": "a lone wolf shaped by their human's instincts",
            "Aristotle": "navigating the ambiguous path set by their human",
        },
        agent_performance={
            "Socrates": AgentPerformance(
                agent_id="Socrates",
                accuracy=[0.8, 0.9],
                performance_score=0.85,
                cooperation_count=5,
                betrayal_count=1,
            ),
            "Plato": AgentPerformance(
                agent_id="Plato",
                accuracy=[0.6, 0.7],
                performance_score=0.65,
                cooperation_count=1,
                betrayal_count=6,
            ),
            "Aristotle": AgentPerformance(
                agent_id="Aristotle",
                accuracy=[0.75, 0.8],
                performance_score=0.78,
                cooperation_count=3,
                betrayal_count=3,
            ),
        },
        notable_events=[
            {
                "turn": 1,
                "event_type": "cooperation_breakthrough",
                "description": "Socrates extended an olive branch to Plato.",
                "agents_involved": ["Socrates", "Plato"],
                "entropy_delta": -2.0,
            },
            {
                "turn": 2,
                "event_type": "betrayal",
                "description": "Plato hoarded supplies despite the crisis.",
                "agents_involved": ["Plato"],
                "entropy_delta": 3.0,
            },
        ],
        collapse_cause="entropy_collapse",
    )


def test_publish_creates_json_and_md(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    json_path = tmp_path / "epoch_1.json"
    md_path = tmp_path / "epoch_1.md"

    assert json_path.exists()
    assert md_path.exists()

    with open(json_path) as f:
        data = json.load(f)
    assert data["epoch_number"] == 1
    assert data["civilization_name"] == "Aethelgard"
    assert len(data["turns"]) == 2
    assert len(data["agents"]) == 3


def test_markdown_contains_expected_sections(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    md_path = tmp_path / "epoch_1.md"
    text = md_path.read_text()

    assert "# Epoch 1: The Fall of Aethelgard" in text
    assert "## Prologue" in text
    assert "## Chronicle" in text
    assert "## Epilogue" in text


def test_markdown_narrates_actions(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    text = (tmp_path / "epoch_1.md").read_text()

    assert "Socrates" in text
    assert "Plato" in text
    assert "share resources with Plato" in text
    assert "hoard supplies" in text
    assert "cooperative spirit of their human" in text
    assert "lone wolf" in text
    assert "entropy" in text


def test_markdown_prologue_has_agents(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    text = (tmp_path / "epoch_1.md").read_text()

    assert "### The Agents" in text
    assert "**Socrates**" in text
    assert "**Plato**" in text
    assert "**Aristotle**" in text


def test_markdown_epilogue_has_patterns(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    text = (tmp_path / "epoch_1.md").read_text()

    assert "### Patterns of Collapse" in text
    assert "Cooperation breakthroughs" in text
    assert "Betrayals" in text
    assert "Near-collapse recoveries" in text


def test_index_catalog_tracking(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    index_path = tmp_path / "index.json"
    assert index_path.exists()

    with open(index_path) as f:
        index = json.load(f)
    assert len(index) == 1
    assert index[0]["epoch"] == 1
    assert index[0]["agent_count"] == 3
    assert index[0]["turn_count"] == 2
    assert index[0]["collapse_cause"] == "entropy_collapse"


def test_index_overwrites_existing_epoch(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    writer.publish(history)

    updated_history = history.model_copy(update={"final_entropy": 99.0})
    writer.publish(updated_history)

    with open(tmp_path / "index.json") as f:
        index = json.load(f)
    assert len(index) == 1
    assert index[0]["epoch"] == 1


def test_accepts_dict_input(tmp_path: Path):
    writer = ChronicleWriter(output_dir=str(tmp_path))
    history = _make_history()
    data = history.model_dump(mode="python")
    data["notable_events"] = [
        {
            "turn": 1,
            "event_type": "cooperation_breakthrough",
            "description": "test",
            "agents_involved": ["Socrates"],
            "entropy_delta": -1.0,
        }
    ]
    writer.publish(data)

    assert (tmp_path / "epoch_1.json").exists()
    assert (tmp_path / "epoch_1.md").exists()
