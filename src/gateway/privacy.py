from hashlib import sha256
from typing import Any

from src.models.world import AgentState, ConsentStatus, WorldState


class PrivacyViolationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class PrivacyGateway:
    PROFILE_FIELDS: set[str] = {
        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism",
        "ocean_traits",
        "cognitive_bias",
        "cognitive_biases",
        "confirmation_bias",
        "availability_heuristic",
        "anchoring_bias",
        "name",
        "email",
        "phone",
        "address",
        "age",
        "gender",
        "location",
        "full_name",
        "first_name",
        "last_name",
        "human_id",
        "user_id",
    }

    def __init__(self) -> None:
        self.privacy_violations: list[dict[str, Any]] = []

    def validate_action(self, agent_id: str, action_payload: dict[str, Any] | str) -> None:
        if isinstance(action_payload, str):
            return

        payload_fields = set(action_payload.keys())
        profile_fields_found = payload_fields & self.PROFILE_FIELDS

        if profile_fields_found:
            self._log_privacy_violation(agent_id, profile_fields_found, action_payload)
            raise PrivacyViolationError(
                f"Profile data fields not allowed in action submission: {profile_fields_found}"
            )

    def _log_privacy_violation(self, agent_id: str, fields: set[str], payload: dict[str, Any]) -> None:
        action_hash = sha256(str(payload).encode()).hexdigest()[:16]
        violation: dict[str, Any] = {
            "agent_id": agent_id,
            "fields_detected": list(fields),
            "action_hash": action_hash,
        }
        self.privacy_violations.append(violation)

    def check_consent(self, agent: AgentState) -> bool:
        return agent.consent_status == ConsentStatus.GRANTED

    def apply_consent_action(self, agent: AgentState, action_type: str) -> dict[str, Any] | None:
        if action_type == "grant":
            agent.consent_status = ConsentStatus.GRANTED
            return {"status": "granted", "agent_id": agent.agent_id}
        elif action_type == "revoke":
            agent.consent_status = ConsentStatus.REVOKED
            agent.resources = {}
            agent.trust_scores = {}
            return {"status": "revoked", "agent_id": agent.agent_id}
        return None

    def apply_anti_gaming_penalty(
        self, world_state: WorldState, agent_id: str, action_payload: dict[str, Any] | str
    ) -> dict[str, Any]:
        if isinstance(action_payload, str):
            return {"penalty_applied": False}

        payload_fields = set(action_payload.keys())
        profile_fields_found = payload_fields & self.PROFILE_FIELDS

        if not profile_fields_found:
            return {"penalty_applied": False}

        action_hash = sha256(str(action_payload).encode()).hexdigest()[:16]

        original_m_e = world_state.material_entropy
        original_s_e = world_state.social_entropy

        world_state.material_entropy = min(1.0, world_state.material_entropy + 0.15)
        world_state.social_entropy = min(1.0, world_state.social_entropy + 0.10)

        penalty_record: dict[str, Any] = {
            "agent_id": agent_id,
            "action_hash": action_hash,
            "material_entropy_before": original_m_e,
            "material_entropy_after": world_state.material_entropy,
            "social_entropy_before": original_s_e,
            "social_entropy_after": world_state.social_entropy,
            "penalty_m_e": 0.15,
            "penalty_s_e": 0.10,
        }

        return {
            "penalty_applied": True,
            "record": penalty_record,
        }

    def anonymise_agent_id(self, agent_id: str) -> str:
        hash_prefix = sha256(agent_id.encode()).hexdigest()[:8]
        return f"agent_{hash_prefix}"

    def get_anonymised_violations(self) -> list[dict[str, Any]]:
        return [
            {
                "agent_id": self.anonymise_agent_id(v["agent_id"]),
                "fields_detected": v["fields_detected"],
                "action_hash": v["action_hash"],
            }
            for v in self.privacy_violations
        ]

    def clear_local_profile(self, agent: AgentState) -> None:
        agent.resources = {}
        agent.trust_scores = {}