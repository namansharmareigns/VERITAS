from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import CurrentSynthesisSchema, DebateMetadataSchema


class DebateCreate(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    domain: str = Field(..., min_length=2, max_length=100)
    description: str | None = None


class DebateUpdate(BaseModel):
    question: str | None = None
    domain: str | None = None
    description: str | None = None
    status: str | None = None


class DebateResponse(BaseModel):
    id: str
    question: str
    domain: str
    description: str | None = None
    status: str
    created_at: datetime | str
    updated_at: datetime | str
    current_synthesis: CurrentSynthesisSchema
    metadata: DebateMetadataSchema
