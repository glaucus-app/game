import pytest

from src.gateway.privacy import PrivacyGateway, PrivacyViolationError
from src.models.world import AgentState, ConsentStatus, WorldState


def test_profile_field_detection_ocean_traits():
    gateway = PrivacyGateway()
    payload = {"openness": 0.8, "cooperate": True}

    with pytest.raises(PrivacyViolationError) as exc_info:
        gateway.validate_action("agent_1", payload)

    assert "openness" in str(exc_info.value)
    assert len(gateway.privacy_violations) == 1


def test_profile_field_detection_cognitive_bias():
    gateway = PrivacyGateway()
    payload = {"confirmation_bias": "high", "defect": True}

    with pytest.raises(PrivacyViolationError) as exc_info:
        gateway.validate_action("agent_2", payload)

    assert "confirmation_bias" in str(exc_info.value)


def test_profile_field_detection_pii():
    gateway = PrivacyGateway()
    payload = {"name": "John Doe", "email": "john@example.com"}

    with pytest.raises(PrivacyViolationError) as exc_info:
        gateway.validate_action("agent_3", payload)

    assert "name" in str(exc_info.value) or "email" in str(exc_info.value)


def test_valid_action_no_profile_fields():
    gateway = PrivacyGateway()
    payload = {"action": "cooperate", "target": "agent_2"}

    gateway.validate_action("agent_1", payload)

    assert len(gateway.privacy_violations) == 0


def test_string_payload_accepted():
    gateway = PrivacyGateway()
    payload = "I choose to cooperate"

    gateway.validate_action("agent_1", payload)

    assert len(gateway.privacy_violations) == 0


def test_anti_gaming_penalty_applied():
    gateway = PrivacyGateway()
    world_state = WorldState(epoch=1, turn=1, material_entropy=0.3, social_entropy=0.4)
    payload = {"openness": 0.8, "action": "cooperate"}

    result = gateway.apply_anti_gaming_penalty(world_state, "agent_1", payload)

    assert result["penalty_applied"] is True
    assert result["record"]["penalty_m_e"] == 0.15
    assert result["record"]["penalty_s_e"] == 0.10
    assert abs(world_state.material_entropy - 0.45) < 0.001
    assert world_state.social_entropy == 0.5


def test_anti_gaming_penalty_caps_at_one():
    gateway = PrivacyGateway()
    world_state = WorldState(epoch=1, turn=1, material_entropy=0.95, social_entropy=0.95)
    payload = {"name": "test"}

    result = gateway.apply_anti_gaming_penalty(world_state, "agent_1", payload)

    assert world_state.material_entropy == 1.0
    assert world_state.social_entropy == 1.0


def test_anti_gaming_penalty_no_profile_fields():
    gateway = PrivacyGateway()
    world_state = WorldState(epoch=1, turn=1, material_entropy=0.3, social_entropy=0.4)
    payload = {"action": "cooperate"}

    result = gateway.apply_anti_gaming_penalty(world_state, "agent_1", payload)

    assert result["penalty_applied"] is False


def test_consent_check_granted():
    gateway = PrivacyGateway()
    agent = AgentState(agent_id="agent_1", consent_status=ConsentStatus.GRANTED)

    assert gateway.check_consent(agent) is True


def test_consent_check_not_granted():
    gateway = PrivacyGateway()
    agent = AgentState(agent_id="agent_1", consent_status=ConsentStatus.PENDING)

    assert gateway.check_consent(agent) is False


def test_consent_grant():
    gateway = PrivacyGateway()
    agent = AgentState(agent_id="agent_1", consent_status=ConsentStatus.PENDING)

    result = gateway.apply_consent_action(agent, "grant")

    assert result["status"] == "granted"
    assert agent.consent_status == ConsentStatus.GRANTED


def test_consent_revoke_clears_profile():
    gateway = PrivacyGateway()
    agent = AgentState(
        agent_id="agent_1",
        consent_status=ConsentStatus.GRANTED,
        resources={"water": 100.0, "energy": 50.0},
        trust_scores={"agent_2": 0.8},
    )

    result = gateway.apply_consent_action(agent, "revoke")

    assert result["status"] == "revoked"
    assert agent.consent_status == ConsentStatus.REVOKED
    assert agent.resources == {}
    assert agent.trust_scores == {}


def test_anonymise_agent_id():
    gateway = PrivacyGateway()

    anon_id = gateway.anonymise_agent_id("agent_12345")

    assert anon_id.startswith("agent_")
    assert anon_id != "agent_12345"
    assert len(anon_id) == 14


def test_anonymise_consistent():
    gateway = PrivacyGateway()

    anon_id_1 = gateway.anonymise_agent_id("agent_12345")
    anon_id_2 = gateway.anonymise_agent_id("agent_12345")

    assert anon_id_1 == anon_id_2


def test_get_anonymised_violations():
    gateway = PrivacyGateway()
    agent = AgentState(agent_id="agent_sensitive", consent_status=ConsentStatus.GRANTED)

    gateway.privacy_violations.append({
        "agent_id": "agent_sensitive",
        "fields_detected": ["openness", "name"],
        "action_hash": "abc123",
    })

    anon_violations = gateway.get_anonymised_violations()

    assert len(anon_violations) == 1
    assert "agent_sensitive" not in anon_violations[0]["agent_id"]
    assert anon_violations[0]["agent_id"].startswith("agent_")
    assert anon_violations[0]["fields_detected"] == ["openness", "name"]


def test_clear_local_profile():
    gateway = PrivacyGateway()
    agent = AgentState(
        agent_id="agent_1",
        resources={"water": 100.0, "energy": 50.0},
        trust_scores={"agent_2": 0.8, "agent_3": 0.6},
    )

    gateway.clear_local_profile(agent)

    assert agent.resources == {}
    assert agent.trust_scores == {}


def test_privacy_violation_error_has_message():
    gateway = PrivacyGateway()
    payload = {"openness": 0.8}

    try:
        gateway.validate_action("agent_1", payload)
        assert False, "Should have raised PrivacyViolationError"
    except PrivacyViolationError as e:
        assert e.message is not None
        assert "openness" in e.message