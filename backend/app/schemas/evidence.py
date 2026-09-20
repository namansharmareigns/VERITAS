from datetime import datetime

from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    claim_id: str
    source_id: str | None = None
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=5)
    source_type: str = "web"
    supports: bool = True
    relevance: float = Field(0.5, ge=0.0, le=1.0)
    reliability_score: float = Field(0.5, ge=0.0, le=1.0)
    independence_score: float = Field(0.5, ge=0.0, le=1.0)
    recency_score: float = Field(0.5, ge=0.0, le=1.0)
    url: str | None = None
    published_at: datetime | None = None
    provenance: dict = {}


class EvidenceUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    supports: bool | None = None
    relevance: float | None = Field(None, ge=0.0, le=1.0)
    reliability_score: float | None = Field(None, ge=0.0, le=1.0)
    independence_score: float | None = Field(None, ge=0.0, le=1.0)
    recency_score: float | None = Field(None, ge=0.0, le=1.0)
    url: str | None = None


class EvidenceResponse(BaseModel):
    id: str
    claim_id: str
    source_id: str | None = None
    title: str
    content: str
    source_type: str
    supports: bool
    relevance: float
    reliability_score: float
    independence_score: float
    recency_score: float
    evidence_score: float
    url: str | None = None
    published_at: datetime | str | None = None
    added_at: datetime | str
    provenance: dict
