from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate
from app.services.claim_strength import recalculate_claim_strength
from app.services.scoring import compute_evidence_score
from app.services.temporal import recalculate_debate_scores, record_history_event
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("")
def create_evidence(payload: EvidenceCreate):
    db = get_db()
    try:
        claim = db.claims.find_one({"_id": ObjectId(payload.claim_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    score = compute_evidence_score(
        payload.reliability_score, payload.relevance,
        payload.independence_score, payload.recency_score,
    )
    doc = {
        "claim_id": ObjectId(payload.claim_id),
        "source_id": ObjectId(payload.source_id) if payload.source_id else None,
        "title": payload.title,
        "content": payload.content,
        "source_type": payload.source_type,
        "supports": payload.supports,
        "relevance": payload.relevance,
        "reliability_score": payload.reliability_score,
        "independence_score": payload.independence_score,
        "recency_score": payload.recency_score,
        "evidence_score": score,
        "url": payload.url,
        "published_at": payload.published_at,
        "added_at": datetime.now(timezone.utc),
        "provenance": payload.provenance,
    }
    result = db.evidence.insert_one(doc)
    db.claims.update_one({"_id": ObjectId(payload.claim_id)}, {"$push": {"evidence_ids": result.inserted_id}})
    recalculate_claim_strength(payload.claim_id)
    debate_id = str(claim["debate_id"])
    recalculate_debate_scores(debate_id)
    record_history_event(debate_id, "evidence_added", f"Evidence added: {payload.title[:60]}")
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@router.get("/claim/{claim_id}")
def get_evidence_by_claim(claim_id: str):
    db = get_db()
    try:
        docs = list(db.evidence.find({"claim_id": ObjectId(claim_id)}).sort("evidence_score", -1))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    return serialize_docs(docs)


@router.get("/{evidence_id}")
def get_evidence(evidence_id: str):
    db = get_db()
    try:
        doc = db.evidence.find_one({"_id": ObjectId(evidence_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid evidence ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return serialize_doc(doc)


@router.put("/{evidence_id}")
def update_evidence(evidence_id: str, payload: EvidenceUpdate):
    db = get_db()
    try:
        existing = db.evidence.find_one({"_id": ObjectId(evidence_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid evidence ID")
    if not existing:
        raise HTTPException(status_code=404, detail="Evidence not found")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    rel = updates.get("reliability_score", existing["reliability_score"])
    rev = updates.get("relevance", existing["relevance"])
    ind = updates.get("independence_score", existing["independence_score"])
    rec = updates.get("recency_score", existing["recency_score"])
    updates["evidence_score"] = compute_evidence_score(rel, rev, ind, rec)
    db.evidence.update_one({"_id": ObjectId(evidence_id)}, {"$set": updates})
    claim_id = str(existing["claim_id"])
    recalculate_claim_strength(claim_id)
    claim = db.claims.find_one({"_id": existing["claim_id"]})
    if claim:
        recalculate_debate_scores(str(claim["debate_id"]))
    return get_evidence(evidence_id)


@router.delete("/{evidence_id}")
def delete_evidence(evidence_id: str):
    db = get_db()
    try:
        oid = ObjectId(evidence_id)
        doc = db.evidence.find_one({"_id": oid})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid evidence ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Evidence not found")
    db.evidence.delete_one({"_id": oid})
    db.claims.update_one({"_id": doc["claim_id"]}, {"$pull": {"evidence_ids": oid}})
    return {"deleted": True, "id": evidence_id}
