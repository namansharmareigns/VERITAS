from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.database import get_db
from app.schemas.contradiction import ContradictionCreate
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/contradictions", tags=["contradictions"])


@router.post("")
def create_contradiction(payload: ContradictionCreate):
    db = get_db()
    ctx = payload.context_dimensions.model_dump() if payload.context_dimensions else {}
    doc = {
        "claim_a": ObjectId(payload.claim_a),
        "claim_b": ObjectId(payload.claim_b),
        "strength": payload.strength,
        "type": payload.type,
        "explanation": payload.explanation,
        "context_dimensions": ctx,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.contradictions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.get("")
def list_contradictions(
    debate_id: str | None = None,
    min_strength: float = Query(0.0, ge=0.0, le=1.0),
):
    db = get_db()
    filt: dict = {"strength": {"$gte": min_strength}}
    if debate_id:
        claim_ids = [c["_id"] for c in db.claims.find({"debate_id": ObjectId(debate_id)}, {"_id": 1})]
        filt["$or"] = [{"claim_a": {"$in": claim_ids}}, {"claim_b": {"$in": claim_ids}}]
    docs = list(db.contradictions.find(filt).sort("strength", -1))
    return serialize_docs(docs)
