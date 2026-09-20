from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 50


class ProvenanceSchema(BaseModel):
    generated_by: str = "user"
    source_context: str | None = None


class CurrentSynthesisSchema(BaseModel):
    summary: str | None = None
    confidence: float = 0.0
    pro_score: float = 0.0
    con_score: float = 0.0
    uncertainty: float = 0.0


class DebateMetadataSchema(BaseModel):
    created_by: str | None = None
    language: str = "en"
    development_fixture: bool = False
