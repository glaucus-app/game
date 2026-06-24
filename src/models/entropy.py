from __future__ import annotations

from pydantic import BaseModel, Field


class MaterialEntropy(BaseModel):
    resource_entropy: float = Field(ge=0.0, le=1.0)
    infrastructure_entropy: float = Field(ge=0.0, le=1.0)
    climate_entropy: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)


class SocialEntropy(BaseModel):
    trust_entropy: float = Field(ge=0.0, le=1.0)
    coalition_entropy: float = Field(ge=0.0, le=1.0)
    info_asymmetry_entropy: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)


class EntropySnapshot(BaseModel):
    turn: int
    material: MaterialEntropy
    social: SocialEntropy


class EntropyConfig(BaseModel):
    w_R: float = 0.4
    w_I: float = 0.35
    w_C: float = 0.25
    w_T: float = 0.3
    w_K: float = 0.3
    w_A: float = 0.4