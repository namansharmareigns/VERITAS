from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.database import get_db
from app.schemas.debate import DebateCreate, DebateUpdate
from app.services.temporal import record_history_event
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/debates", tags=["debates"])


@router.post("")
def create_debate(payload: DebateCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {
        "question": payload.question,
        "domain": payload.domain,
        "description": payload.description,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "current_synthesis": {
            "summary": None,
            "confidence": 0.0,
            "pro_score": 0.0,
            "con_score": 0.0,
            "uncertainty": 1.0,
        },
        "metadata": {"created_by": None, "language": "en", "development_fixture": False},
    }
    result = db.debates.insert_one(doc)
    debate_id = str(result.inserted_id)
    record_history_event(debate_id, "debate_created", f"Debate created: {payload.question[:80]}")
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.get("")
def list_debates(
    domain: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    db = get_db()
    filt: dict = {}
    if domain:
        filt["domain"] = domain
    if status:
        filt["status"] = status
    skip = (page - 1) * page_size
    docs = list(db.debates.find(filt).sort("created_at", -1).skip(skip).limit(page_size))
    total = db.debates.count_documents(filt)
    return {"items": serialize_docs(docs), "total": total, "page": page, "page_size": page_size}


@router.get("/{debate_id}")
def get_debate(debate_id: str):
    db = get_db()
    try:
        doc = db.debates.find_one({"_id": ObjectId(debate_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Debate not found")
    return serialize_doc(doc)


@router.put("/{debate_id}")
def update_debate(debate_id: str, payload: DebateUpdate):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    updates["updated_at"] = datetime.now(timezone.utc)
    try:
        result = db.debates.update_one({"_id": ObjectId(debate_id)}, {"$set": updates})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Debate not found")
    return get_debate(debate_id)


@router.delete("/{debate_id}")
def delete_debate(debate_id: str):
    db = get_db()
    try:
        oid = ObjectId(debate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    result = db.debates.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Debate not found")
    for coll in ["claims", "debate_history"]:
        if coll == "claims":
            claim_ids = [c["_id"] for c in db.claims.find({"debate_id": oid}, {"_id": 1})]
            db.evidence.delete_many({"claim_id": {"$in": claim_ids}})
            db.counterarguments.delete_many({"claim_id": {"$in": claim_ids}})
            db.claims.delete_many({"debate_id": oid})
        else:
            db[coll].delete_many({"debate_id": oid})
    return {"deleted": True, "id": debate_id}


@router.get("/{debate_id}/export")
def export_debate(debate_id: str):
    db = get_db()
    try:
        oid = ObjectId(debate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    debate = db.debates.find_one({"_id": oid})
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    claims = list(db.claims.find({"debate_id": oid}))
    claim_ids = [c["_id"] for c in claims]
    return {
        "debate": serialize_doc(debate),
        "claims": serialize_docs(claims),
        "evidence": serialize_docs(list(db.evidence.find({"claim_id": {"$in": claim_ids}}))),
        "counterarguments": serialize_docs(list(db.counterarguments.find({"claim_id": {"$in": claim_ids}}))),
        "contradictions": serialize_docs(list(db.contradictions.find({
            "$or": [{"claim_a": {"$in": claim_ids}}, {"claim_b": {"$in": claim_ids}}]
        }))),
        "history": serialize_docs(list(db.debate_history.find({"debate_id": oid}).sort("timestamp", 1))),
    }


@router.get("/{debate_id}/export/summary")
def export_debate_summary(debate_id: str):
    data = export_debate(debate_id)
    debate = data["debate"]
    return {
        "question": debate["question"],
        "domain": debate["domain"],
        "status": debate["status"],
        "synthesis": debate["current_synthesis"],
        "claim_count": len(data["claims"]),
        "evidence_count": len(data["evidence"]),
        "contradiction_count": len(data["contradictions"]),
        "history_events": len(data["history"]),
    }
