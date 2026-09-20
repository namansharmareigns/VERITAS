from datetime import datetime

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    title: str = Field(..., min_length=3)
    authors: list[str] = []
    publisher: str | None = None
    source_type: str = "web"
    url: str | None = None
    published_at: datetime | None = None
    reliability: float = Field(0.5, ge=0.0, le=1.0)
    metadata: dict = {}


class SourceResponse(BaseModel):
    id: str
    title: str
    authors: list[str]
    publisher: str | None = None
    source_type: str
    url: str | None = None
    published_at: datetime | str | None = None
    reliability: float
    metadata: dict
