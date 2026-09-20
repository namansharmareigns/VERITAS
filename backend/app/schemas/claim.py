from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ProvenanceSchema


class ClaimCreate(BaseModel):
    debate_id: str
    position: str = Field(..., pattern="^(PRO|CON)$")
    text: str = Field(..., min_length=3)
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    tags: list[str] = []
    provenance: ProvenanceSchema | None = None


class ClaimUpdate(BaseModel):
    text: str | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    status: str | None = None
    tags: list[str] | None = None


class ClaimResponse(BaseModel):
    id: str
    debate_id: str
    position: str
    text: str
    normalized_text: str
    confidence: float
    status: str
    tags: list[str]
    evidence_ids: list[str]
    counterargument_ids: list[str]
    created_at: datetime | str
    updated_at: datetime | str
    provenance: dict
    strength_explanation: dict | None = None
