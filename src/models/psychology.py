import json
import random
from pathlib import Path
from typing import Dict

import numpy as np
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    openness: float = Field(ge=0.0, le=1.0)
    conscientiousness: float = Field(ge=0.0, le=1.0)
    extraversion: float = Field(ge=0.0, le=1.0)
    agreeableness: float = Field(ge=0.0, le=1.0)
    neuroticism: float = Field(ge=0.0, le=1.0)
    risk_tolerance: float = Field(ge=0.0, le=1.0)
    cognitive_biases: Dict[str, float] = Field(default_factory=dict)
    decision_heuristics: Dict[str, float] = Field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str | Path) -> "UserProfile":
        with open(path, "r") as f:
            data = json.load(f)
        return cls(**data)

    def compute_choice_distribution(
        self, scenario: dict
    ) -> Dict[str, float]:
        choices = scenario.get("choices", [])
        if not choices:
            return {}

        behavior_dims = scenario.get("behavioral_dimensions", {})
        weights = np.array([1.0] * len(choices))

        for i, choice in enumerate(choices):
            choice_attrs = choice.get("attributes", {})
            w = 1.0

            if "risk_level" in behavior_dims:
                risk_attr = choice_attrs.get("risk_level", 0.5)
                w *= 1.0 - abs(risk_attr - self.risk_tolerance)

            if "collaboration_level" in behavior_dims:
                collab_attr = choice_attrs.get("collaboration_level", 0.5)
                w *= collab_attr * self.agreeableness + (1 - collab_attr) * (1 - self.agreeableness)

            if "novelty_level" in behavior_dims:
                novelty_attr = choice_attrs.get("novelty_level", 0.5)
                w *= novelty_attr * self.openness + (1 - novelty_attr) * (1 - self.openness)

            if "time_pressure" in behavior_dims:
                time_attr = choice_attrs.get("time_pressure", 0.5)
                w *= (1 - time_attr) * self.conscientiousness + time_attr * (1 - self.conscientiousness)

            if self.cognitive_biases.get("loss_aversion", 0.0) > 0:
                loss_risk = choice_attrs.get("potential_loss", 0)
                w *= 1.0 - self.cognitive_biases["loss_aversion"] * loss_risk

            if self.cognitive_biases.get("status_quo_bias", 0.0) > 0:
                default_bias = self.cognitive_biases["status_quo_bias"]
                if choice.get("is_default", False):
                    w *= (1 + default_bias)
                else:
                    w *= (1 - default_bias * 0.5)

            weights[i] = max(w, 0.01)

        weights = weights ** 1.5
        probabilities = weights / weights.sum()

        heuristics = self.decision_heuristics
        if "familiarity" in heuristics:
            for i, choice in enumerate(choices):
                if choice.get("is_familiar", False):
                    probabilities[i] *= (1 + heuristics["familiarity"])
            probabilities = probabilities / probabilities.sum()

        result = {}
        for i, choice in enumerate(choices):
            result[choice["id"]] = float(probabilities[i])

        return result

    def simulate_decision(self, scenario: dict) -> str:
        distribution = self.compute_choice_distribution(scenario)
        choice_ids = list(distribution.keys())
        probabilities = list(distribution.values())

        cumulative = np.cumsum(probabilities)
        rand_val = random.random()
        for i, cum_prob in enumerate(cumulative):
            if rand_val <= cum_prob:
                return choice_ids[i]

        return choice_ids[-1]