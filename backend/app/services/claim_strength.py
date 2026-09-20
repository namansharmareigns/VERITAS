from bson import ObjectId

from app.database import get_db
from app.services.scoring import compute_claim_strength


def recalculate_claim_strength(claim_id: str) -> float:
    db = get_db()
    claim = db.claims.find_one({"_id": ObjectId(claim_id)})
    if not claim:
        return 0.0

    evidence = list(db.evidence.find({"claim_id": ObjectId(claim_id)}))
    supporting = [e for e in evidence if e.get("supports")]
    opposing = [e for e in evidence if not e.get("supports")]
    counterarguments = list(db.counterarguments.find({"claim_id": ObjectId(claim_id)}))

    contradictions = list(db.contradictions.find({
        "$or": [{"claim_a": ObjectId(claim_id)}, {"claim_b": ObjectId(claim_id)}]
    }))
    contradiction_penalty = sum(c.get("strength", 0.0) for c in contradictions) * 0.2

    strength, explanation = compute_claim_strength(supporting, opposing, counterarguments, contradiction_penalty)

    from datetime import datetime, timezone
    db.claims.update_one(
        {"_id": ObjectId(claim_id)},
        {
            "$set": {
                "confidence": strength,
                "strength_explanation": explanation,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return strength
