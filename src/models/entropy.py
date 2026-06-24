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
    w_R: float = Field(default=0.4, ge=0.0, le=1.0)
    w_I: float = Field(default=0.35, ge=0.0, le=1.0)
    w_C: float = Field(default=0.25, ge=0.0, le=1.0)
    w_T: float = Field(default=0.3, ge=0.0, le=1.0)
    w_K: float = Field(default=0.3, ge=0.0, le=1.0)
    w_A: float = Field(default=0.4, ge=0.0, le=1.0)