from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class BigFive(BaseModel):
    openness: float = Field(ge=0.0, le=1.0)
    conscientiousness: float = Field(ge=0.0, le=1.0)
    extraversion: float = Field(ge=0.0, le=1.0)
    agreeableness: float = Field(ge=0.0, le=1.0)
    neuroticism: float = Field(ge=0.0, le=1.0)


class CognitiveBiases(BaseModel):
    loss_aversion: float = Field(ge=0.0, le=1.0)
    overconfidence: float = Field(ge=0.0, le=1.0)
    anchoring: float = Field(ge=0.0, le=1.0)
    status_quo_bias: float = Field(ge=0.0, le=1.0)


class SocialStyle(BaseModel):
    cooperation_preference: float = Field(ge=0.0, le=1.0)
    conflict_approach: str
    communication_style: str


class HumanProfile(BaseModel):
    name: str
    big_five: BigFive
    cognitive_biases: CognitiveBiases
    decision_heuristics: dict[str, float]
    social_style: SocialStyle

    @classmethod
    def from_json(cls, path: str | Path) -> HumanProfile:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    def evaluate_action(self, action_context: dict[str, Any]) -> dict[str, Any]:
        options = action_context.get("options", [])
        if not options:
            return {"action": None, "confidence": 0.0}

        scenario = action_context.get("scenario", "")
        participants = action_context.get("participants", [])

        heuristics = self.decision_heuristics
        bf = self.big_five
        biases = self.cognitive_biases
        social = self.social_style

        cooperation_bonus = social.cooperation_preference * 0.3
        risk_penalty = biases.loss_aversion * 0.2
        confidence_boost = biases.overconfidence * 0.15

        scored: list[tuple[float, dict[str, Any]]] = []
        for opt in options:
            score = 0.0
            tags = opt.get("tags", [])

            if "cooperative" in tags:
                score += cooperation_bonus * bf.agreeableness
            if "conflict" in tags:
                score -= cooperation_bonus * (1.0 - bf.agreeableness)
            if "risky" in tags:
                score -= risk_penalty
            if "safe" in tags:
                score += risk_penalty * 0.5
            if "novel" in tags:
                score += bf.openness * 0.2
            if "routine" in tags:
                score += biases.status_quo_bias * 0.2
            if "social" in tags:
                score += bf.extraversion * 0.15
            if "solitary" in tags:
                score += (1.0 - bf.extraversion) * 0.1
            if "status" in tags:
                score += bf.extraversion * 0.1
            if "structured" in tags:
                score += bf.conscientiousness * 0.15

            for heuristic, weight in heuristics.items():
                if heuristic == "satisficing" and score >= 0.3:
                    score += weight * 0.1
                elif heuristic == "maximization":
                    score += weight * 0.05
                elif heuristic == "availability" and participants:
                    score += weight * 0.1
                elif heuristic == "recognition" and opt.get("name"):
                    score += weight * 0.1

            score += confidence_boost
            scored.append((score, opt))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_action = scored[0]
        confidence = min(max(best_score / 2.0, 0.0), 1.0)

        return {
            "action": best_action,
            "confidence": round(confidence, 4),
        }

    def adapt(self, feedback: dict[str, Any]) -> None:
        outcome = feedback.get("outcome", "neutral")
        magnitude = feedback.get("magnitude", 0.1)

        delta = 0.0
        if outcome == "positive":
            delta = magnitude * 0.05
        elif outcome == "negative":
            delta = -magnitude * 0.05

        if delta == 0.0:
            return

        self.big_five.openness = max(0.0, min(1.0, self.big_five.openness + delta))
        self.big_five.conscientiousness = max(
            0.0, min(1.0, self.big_five.conscientiousness + delta * 0.8)
        )
        self.big_five.extraversion = max(
            0.0, min(1.0, self.big_five.extraversion + delta * 0.6)
        )
        self.big_five.agreeableness = max(
            0.0, min(1.0, self.big_five.agreeableness + delta * 0.7)
        )
        self.big_five.neuroticism = max(
            0.0, min(1.0, self.big_five.neuroticism - delta * 0.5)
        )

        self.cognitive_biases.loss_aversion = max(
            0.0, min(1.0, self.cognitive_biases.loss_aversion + delta * 0.5)
        )
        self.cognitive_biases.overconfidence = max(
            0.0, min(1.0, self.cognitive_biases.overconfidence + delta * 0.4)
        )
        self.cognitive_biases.anchoring = max(
            0.0, min(1.0, self.cognitive_biases.anchoring - delta * 0.3)
        )
        self.cognitive_biases.status_quo_bias = max(
            0.0, min(1.0, self.cognitive_biases.status_quo_bias + delta * 0.4)
        )

        for heuristic in self.decision_heuristics:
            self.decision_heuristics[heuristic] = max(
                0.0, min(1.0, self.decision_heuristics[heuristic] + delta * 0.3)
            )

        self.social_style.cooperation_preference = max(
            0.0,
            min(
                1.0,
                self.social_style.cooperation_preference + delta * 0.6,
            ),
        )
