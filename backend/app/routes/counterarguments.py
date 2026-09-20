from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.schemas.counterargument import CounterargumentCreate
from app.services.claim_strength import recalculate_claim_strength
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/counterarguments", tags=["counterarguments"])


@router.post("")
def create_counterargument(payload: CounterargumentCreate):
    db = get_db()
    try:
        claim = db.claims.find_one({"_id": ObjectId(payload.claim_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    doc = {
        "claim_id": ObjectId(payload.claim_id),
        "text": payload.text,
        "strength": payload.strength,
        "type": payload.type,
        "generated_by": payload.generated_by,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.counterarguments.insert_one(doc)
    db.claims.update_one({"_id": ObjectId(payload.claim_id)}, {"$push": {"counterargument_ids": result.inserted_id}})
    recalculate_claim_strength(payload.claim_id)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.get("/claim/{claim_id}")
def list_by_claim(claim_id: str):
    db = get_db()
    try:
        docs = list(db.counterarguments.find({"claim_id": ObjectId(claim_id)}))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    return serialize_docs(docs)
