from datetime import datetime

from pydantic import BaseModel, Field


class CounterargumentCreate(BaseModel):
    claim_id: str
    text: str = Field(..., min_length=3)
    strength: float = Field(0.5, ge=0.0, le=1.0)
    type: str = "rebuttal"
    generated_by: str = "ai"


class CounterargumentResponse(BaseModel):
    id: str
    claim_id: str
    text: str
    strength: float
    type: str
    generated_by: str
    created_at: datetime | str
