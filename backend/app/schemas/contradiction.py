from datetime import datetime

from pydantic import BaseModel, Field


class ContextDimensions(BaseModel):
    population: str | None = None
    geography: str | None = None
    methodology: str | None = None
    time_period: str | None = None
    dataset: str | None = None


class ContradictionCreate(BaseModel):
    claim_a: str
    claim_b: str
    strength: float = Field(0.5, ge=0.0, le=1.0)
    type: str = "potential_conflict"
    explanation: str
    context_dimensions: ContextDimensions | None = None


class ContradictionResponse(BaseModel):
    id: str
    claim_a: str
    claim_b: str
    strength: float
    type: str
    explanation: str
    context_dimensions: dict
    created_at: datetime | str
