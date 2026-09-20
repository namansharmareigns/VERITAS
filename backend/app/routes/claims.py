from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.schemas.claim import ClaimCreate, ClaimUpdate
from app.services.claim_strength import recalculate_claim_strength
from app.services.temporal import recalculate_debate_scores, record_history_event
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("")
def create_claim(payload: ClaimCreate):
    db = get_db()
    try:
        debate = db.debates.find_one({"_id": ObjectId(payload.debate_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    now = datetime.now(timezone.utc)
    provenance = payload.provenance.model_dump() if payload.provenance else {"generated_by": "user", "source_context": None}
    doc = {
        "debate_id": ObjectId(payload.debate_id),
        "position": payload.position,
        "text": payload.text,
        "normalized_text": payload.text.lower().strip(),
        "confidence": payload.confidence,
        "status": "active",
        "tags": payload.tags,
        "evidence_ids": [],
        "counterargument_ids": [],
        "created_at": now,
        "updated_at": now,
        "provenance": provenance,
    }
    result = db.claims.insert_one(doc)
    claim_id = str(result.inserted_id)
    recalculate_claim_strength(claim_id)
    recalculate_debate_scores(payload.debate_id)
    record_history_event(payload.debate_id, "claim_added", f"New {payload.position} claim added.")
    doc["_id"] = result.inserted_id
    return serialize_doc(db.claims.find_one({"_id": result.inserted_id}))


@router.get("/debate/{debate_id}")
def get_claims_by_debate(debate_id: str):
    db = get_db()
    try:
        docs = list(db.claims.find({"debate_id": ObjectId(debate_id)}).sort("confidence", -1))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    return serialize_docs(docs)


@router.get("/{claim_id}")
def get_claim(claim_id: str):
    db = get_db()
    try:
        doc = db.claims.find_one({"_id": ObjectId(claim_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Claim not found")
    return serialize_doc(doc)


@router.put("/{claim_id}")
def update_claim(claim_id: str, payload: ClaimUpdate):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "text" in updates:
        updates["normalized_text"] = updates["text"].lower().strip()
    updates["updated_at"] = datetime.now(timezone.utc)
    try:
        claim = db.claims.find_one({"_id": ObjectId(claim_id)})
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": updates})
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    recalculate_claim_strength(claim_id)
    recalculate_debate_scores(str(claim["debate_id"]))
    return get_claim(claim_id)


@router.delete("/{claim_id}")
def delete_claim(claim_id: str):
    db = get_db()
    try:
        oid = ObjectId(claim_id)
        claim = db.claims.find_one({"_id": oid})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    db.evidence.delete_many({"claim_id": oid})
    db.counterarguments.delete_many({"claim_id": oid})
    db.claims.delete_one({"_id": oid})
    return {"deleted": True, "id": claim_id}
