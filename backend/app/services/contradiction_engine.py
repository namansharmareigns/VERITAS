"""Two-stage contradiction workflow: semantic similarity + conflict analysis."""

import re
from typing import Any

from bson import ObjectId

from app.database import get_db


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _detect_negation_conflict(text_a: str, text_b: str) -> bool:
    neg_words = {"not", "never", "no", "cannot", "shouldn't", "won't", "unlikely", "harmful", "risky"}
    pos_words = {"should", "beneficial", "effective", "safe", "recommended", "necessary", "improves"}
    ta, tb = text_a.lower(), text_b.lower()
    a_neg = any(w in ta for w in neg_words)
    b_neg = any(w in tb for w in neg_words)
    a_pos = any(w in ta for w in pos_words)
    b_pos = any(w in tb for w in pos_words)
    return (a_neg and b_pos) or (b_neg and a_pos)


def analyze_contradiction(claim_a: dict[str, Any], claim_b: dict[str, Any]) -> dict[str, Any] | None:
    if claim_a.get("position") == claim_b.get("position"):
        return None

    sim = _jaccard(_tokenize(claim_a["text"]), _tokenize(claim_b["text"]))
    if sim < 0.05 and not _detect_negation_conflict(claim_a["text"], claim_b["text"]):
        return None

    direct = _detect_negation_conflict(claim_a["text"], claim_b["text"]) and sim > 0.1
    if direct:
        ctype = "direct_contradiction"
        strength = min(0.5 + sim, 0.95)
        explanation = (
            f"Claims from {claim_a['position']} and {claim_b['position']} positions appear to "
            f"directly contradict on the same topic (similarity={sim:.2f})."
        )
    elif sim > 0.15:
        ctype = "contextual_disagreement"
        strength = min(0.3 + sim * 0.5, 0.7)
        explanation = (
            "Claims share topical overlap but may reflect contextual differences in population, "
            "methodology, or assumptions rather than outright contradiction."
        )
    else:
        ctype = "potential_conflict"
        strength = 0.35
        explanation = "Potential conflict detected based on opposing positions and partial topical overlap."

    return {
        "claim_a": claim_a["_id"],
        "claim_b": claim_b["_id"],
        "strength": round(strength, 4),
        "type": ctype,
        "explanation": explanation,
        "context_dimensions": {
            "population": None,
            "geography": None,
            "methodology": None,
            "time_period": None,
            "dataset": None,
        },
    }


def find_and_store_contradictions(debate_id: str) -> list[dict[str, Any]]:
    db = get_db()
    claims = list(db.claims.find({"debate_id": ObjectId(debate_id), "status": {"$ne": "superseded"}}))
    pro_claims = [c for c in claims if c["position"] == "PRO"]
    con_claims = [c for c in claims if c["position"] == "CON"]
    created = []

    for pa in pro_claims:
        for cb in con_claims:
            existing = db.contradictions.find_one({
                "$or": [
                    {"claim_a": pa["_id"], "claim_b": cb["_id"]},
                    {"claim_a": cb["_id"], "claim_b": pa["_id"]},
                ]
            })
            if existing:
                continue
            result = analyze_contradiction(pa, cb)
            if result:
                from datetime import datetime, timezone
                result["created_at"] = datetime.now(timezone.utc)
                ins = db.contradictions.insert_one(result)
                result["_id"] = ins.inserted_id
                created.append(result)
    return created
