from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.schemas.source import SourceCreate
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("")
def create_source(payload: SourceCreate):
    db = get_db()
    doc = {
        "title": payload.title,
        "authors": payload.authors,
        "publisher": payload.publisher,
        "source_type": payload.source_type,
        "url": payload.url,
        "published_at": payload.published_at,
        "reliability": payload.reliability,
        "metadata": payload.metadata,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.sources.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.get("")
def list_sources(source_type: str | None = None, limit: int = 50):
    db = get_db()
    filt = {"source_type": source_type} if source_type else {}
    docs = list(db.sources.find(filt).sort("published_at", -1).limit(limit))
    return serialize_docs(docs)


@router.get("/{source_id}")
def get_source(source_id: str):
    db = get_db()
    try:
        doc = db.sources.find_one({"_id": ObjectId(source_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid source ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Source not found")
    return serialize_doc(doc)
