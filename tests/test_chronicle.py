import json
import tempfile
from pathlib import Path

import pytest

from src.engine.chronicle import ChronicleWriter
from src.models.chronicle import AgentAction, AgentPerformance, EpochHistory, NotableEvent, TurnSummary


@pytest.fixture
def temp_chronicles_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_epoch_history():
    return EpochHistory(
        epoch_number=1,
        civilization_name="Testopia",
        start_date="2024-01-01",
        end_date="2024-01-02",
        initial_world_state={"entropy": 10.0},
        final_entropy=100.0,
        entropy_graph=[(0, 10.0), (1, 15.0)],
        turns=[
            TurnSummary(
                turn=1,
                scenario="Resource shortage",
                affected_agents=["Socrates", "Plato"],
                actions=[
                    AgentAction(agent_id="Socrates", action="share_resources", outcome="cooperation", entropy_delta=-2.0),
                    AgentAction(agent_id="Plato", action="hoard_resources", outcome="conflict", entropy_delta=5.0),
                ],
                entropy_before=10.0,
                entropy_after=13.0,
            ),
        ],
        agents=["Socrates", "Plato"],
        human_profiles={
            "Socrates": "guided by the cooperative spirit of their human",
            "Plato": "a lone wolf shaped by their human's instincts",
        },
        agent_performance={
            "Socrates": AgentPerformance(
                agent_id="Socrates",
                accuracy=[0.9, 0.85],
                performance_score=0.87,
                cooperation_count=1,
                betrayal_count=0,
            ),
            "Plato": AgentPerformance(
                agent_id="Plato",
                accuracy=[0.7, 0.75],
                performance_score=0.72,
                cooperation_count=0,
                betrayal_count=1,
            ),
        },
        notable_events=[
            NotableEvent(
                turn=1,
                event_type="betrayal",
                description="Plato betrayed the trust of the group",
                agents_involved=["Plato"],
                entropy_delta=5.0,
            ),
        ],
        collapse_cause="entropy_collapse",
    )


def test_publish_creates_json_file(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history)

    json_path = Path(temp_chronicles_dir) / "epoch_1.json"
    assert json_path.exists()

    with open(json_path) as f:
        data = json.load(f)
    assert data["epoch_number"] == 1
    assert data["civilization_name"] == "Testopia"


def test_publish_creates_markdown_file(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history)

    md_path = Path(temp_chronicles_dir) / "epoch_1.md"
    assert md_path.exists()

    content = md_path.read_text()
    assert "# Epoch 1: The Fall of Testopia" in content
    assert "## Prologue" in content
    assert "## Chronicle" in content
    assert "## Epilogue" in content


def test_markdown_contains_narrative_sections(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history)

    md_path = Path(temp_chronicles_dir) / "epoch_1.md"
    content = md_path.read_text()

    assert "Socrates" in content
    assert "Plato" in content
    assert "share_resources" in content
    assert "hoard_resources" in content
    assert "cooperation" in content.lower() or "cooperative" in content


def test_index_json_tracks_epochs(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history)

    index_path = Path(temp_chronicles_dir) / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    assert len(index) == 1
    assert index[0]["epoch"] == 1
    assert index[0]["civilization_name"] == "Testopia"
    assert index[0]["agent_count"] == 2


def test_publish_overwrites_existing_epoch(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history)

    new_history = sample_epoch_history.model_copy()
    new_history.epoch_number = 1
    new_history.civilization_name = "Updatedopia"
    writer.publish(new_history)

    index_path = Path(temp_chronicles_dir) / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    assert len(index) == 1
    assert index[0]["civilization_name"] == "Updatedopia"


def test_accept_dict_for_publish(temp_chronicles_dir, sample_epoch_history):
    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(sample_epoch_history.model_dump())

    json_path = Path(temp_chronicles_dir) / "epoch_1.json"
    assert json_path.exists()


def test_profile_anonymization_falls_back_to_behavior(temp_chronicles_dir):
    history = EpochHistory(
        epoch_number=2,
        civilization_name="NoProfileLand",
        start_date="2024-01-01",
        end_date="2024-01-02",
        initial_world_state={"entropy": 0.0},
        final_entropy=100.0,
        entropy_graph=[],
        turns=[],
        agents=["Cooperator", "Betrayer"],
        human_profiles={},
        agent_performance={
            "Cooperator": AgentPerformance(
                agent_id="Cooperator",
                cooperation_count=5,
                betrayal_count=0,
                performance_score=0.9,
            ),
            "Betrayer": AgentPerformance(
                agent_id="Betrayer",
                cooperation_count=0,
                betrayal_count=3,
                performance_score=0.3,
            ),
        },
    )

    writer = ChronicleWriter(output_dir=temp_chronicles_dir)
    writer.publish(history)

    md_path = Path(temp_chronicles_dir) / "epoch_2.md"
    content = md_path.read_text()

    assert "guided by the cooperative spirit of their human" in content
    assert "lone wolf shaped by their human" in content