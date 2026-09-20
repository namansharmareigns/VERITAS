from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.database import get_db
from app.services.scoring import compute_debate_scores


def record_history_event(
    debate_id: str,
    event_type: str,
    change_summary: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    db = get_db()
    debate = db.debates.find_one({"_id": ObjectId(debate_id)})
    if not debate:
        return {}

    claims = list(db.claims.find({"debate_id": ObjectId(debate_id), "status": {"$ne": "superseded"}}))
    evidence_count = db.evidence.count_documents({"claim_id": {"$in": [c["_id"] for c in claims]}})
    contradiction_count = db.contradictions.count_documents({
        "$or": [
            {"claim_a": {"$in": [c["_id"] for c in claims]}},
            {"claim_b": {"$in": [c["_id"] for c in claims]}},
        ]
    })

    synthesis = debate.get("current_synthesis", {})
    doc = {
        "debate_id": ObjectId(debate_id),
        "timestamp": datetime.now(timezone.utc),
        "pro_score": synthesis.get("pro_score", 0.0),
        "con_score": synthesis.get("con_score", 0.0),
        "confidence": synthesis.get("confidence", 0.0),
        "evidence_count": evidence_count,
        "contradiction_count": contradiction_count,
        "event_type": event_type,
        "change_summary": change_summary,
    }
    if extra:
        doc.update(extra)
    result = db.debate_history.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def recalculate_debate_scores(debate_id: str) -> dict[str, float]:
    db = get_db()
    claims = list(db.claims.find({"debate_id": ObjectId(debate_id), "status": {"$ne": "superseded"}}))
    pro_scores = [c.get("confidence", 0.0) for c in claims if c.get("position") == "PRO"]
    con_scores = [c.get("confidence", 0.0) for c in claims if c.get("position") == "CON"]
    scores = compute_debate_scores(pro_scores, con_scores)
    db.debates.update_one(
        {"_id": ObjectId(debate_id)},
        {
            "$set": {
                "current_synthesis.pro_score": scores["pro_score"],
                "current_synthesis.con_score": scores["con_score"],
                "current_synthesis.confidence": scores["confidence"],
                "current_synthesis.uncertainty": scores["uncertainty"],
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return scores
