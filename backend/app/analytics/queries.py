"""12+ meaningful project-specific MongoDB queries (Q1-Q12)."""

from typing import Any

from bson import ObjectId

from app.database import get_db


class QueryService:
    def __init__(self) -> None:
        self.db = get_db()

    # Q1 — Fetch all debates
    def q1_all_debates(self, limit: int = 50) -> list[dict]:
        return list(self.db.debates.find().sort("created_at", -1).limit(limit))

    # Q2 — Fetch claims for a debate
    def q2_claims_for_debate(self, debate_id: str) -> list[dict]:
        return list(self.db.claims.find({"debate_id": ObjectId(debate_id)}).sort("confidence", -1))

    # Q3 — Compare PRO vs CON confidence
    def q3_pro_con_confidence(self, debate_id: str) -> list[dict]:
        pipeline = [
            {"$match": {"debate_id": ObjectId(debate_id), "status": {"$ne": "superseded"}}},
            {"$group": {"_id": "$position", "avg_confidence": {"$avg": "$confidence"}, "count": {"$sum": 1}}},
        ]
        return list(self.db.claims.aggregate(pipeline))

    # Q4 — Strongest supporting evidence for a claim
    def q4_strongest_supporting_evidence(self, claim_id: str, limit: int = 5) -> list[dict]:
        return list(
            self.db.evidence.find({"claim_id": ObjectId(claim_id), "supports": True})
            .sort("evidence_score", -1).limit(limit)
        )

    # Q5 — Strongest opposing evidence
    def q5_strongest_opposing_evidence(self, claim_id: str, limit: int = 5) -> list[dict]:
        return list(
            self.db.evidence.find({"claim_id": ObjectId(claim_id), "supports": False})
            .sort("evidence_score", -1).limit(limit)
        )

    # Q6 — High-strength contradictions
    def q6_high_strength_contradictions(self, min_strength: float = 0.5, limit: int = 20) -> list[dict]:
        return list(self.db.contradictions.find({"strength": {"$gte": min_strength}}).sort("strength", -1).limit(limit))

    # Q7 — Average evidence reliability by source type
    def q7_avg_reliability_by_source_type(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$source_type", "avg_reliability": {"$avg": "$reliability_score"}, "count": {"$sum": 1}}},
            {"$sort": {"avg_reliability": -1}},
        ]
        return list(self.db.evidence.aggregate(pipeline))

    # Q8 — Debate evolution over time
    def q8_debate_evolution(self, debate_id: str) -> list[dict]:
        return list(self.db.debate_history.find({"debate_id": ObjectId(debate_id)}).sort("timestamp", 1))

    # Q9 — Low-confidence claims
    def q9_low_confidence_claims(self, threshold: float = 0.4, limit: int = 20) -> list[dict]:
        return list(
            self.db.claims.find({"confidence": {"$lt": threshold}, "status": "active"})
            .sort("confidence", 1).limit(limit)
        )

    # Q10 — Rank claims by confidence
    def q10_rank_claims_by_confidence(self, debate_id: str | None = None, limit: int = 20) -> list[dict]:
        filt: dict[str, Any] = {"status": {"$ne": "superseded"}}
        if debate_id:
            filt["debate_id"] = ObjectId(debate_id)
        return list(self.db.claims.find(filt).sort("confidence", -1).limit(limit))

    # Q11 — Evidence-weighted claim score
    def q11_evidence_weighted_claim_scores(self, debate_id: str) -> list[dict]:
        pipeline = [
            {"$match": {"debate_id": ObjectId(debate_id)}},
            {"$lookup": {
                "from": "evidence",
                "localField": "_id",
                "foreignField": "claim_id",
                "as": "evidence_items",
            }},
            {"$addFields": {
                "weighted_score": {
                    "$sum": {
                        "$map": {
                            "input": "$evidence_items",
                            "as": "e",
                            "in": {"$cond": ["$$e.supports", "$$e.evidence_score", {"$multiply": ["$$e.evidence_score", -0.5]}]},
                        }
                    }
                }
            }},
            {"$project": {"text": 1, "position": 1, "confidence": 1, "weighted_score": 1}},
            {"$sort": {"weighted_score": -1}},
        ]
        return list(self.db.claims.aggregate(pipeline))

    # Q12 — Debate/domain statistics
    def q12_domain_statistics(self) -> list[dict]:
        pipeline = [
            {"$group": {
                "_id": "$domain",
                "debate_count": {"$sum": 1},
                "avg_confidence": {"$avg": "$current_synthesis.confidence"},
                "avg_pro": {"$avg": "$current_synthesis.pro_score"},
                "avg_con": {"$avg": "$current_synthesis.con_score"},
            }},
            {"$sort": {"debate_count": -1}},
        ]
        return list(self.db.debates.aggregate(pipeline))

    def run_named_query(self, name: str, **kwargs: Any) -> dict[str, Any]:
        import inspect
        import time
        mapping = {
            "q1": self.q1_all_debates,
            "q2": self.q2_claims_for_debate,
            "q3": self.q3_pro_con_confidence,
            "q4": self.q4_strongest_supporting_evidence,
            "q5": self.q5_strongest_opposing_evidence,
            "q6": self.q6_high_strength_contradictions,
            "q7": self.q7_avg_reliability_by_source_type,
            "q8": self.q8_debate_evolution,
            "q9": self.q9_low_confidence_claims,
            "q10": self.q10_rank_claims_by_confidence,
            "q11": self.q11_evidence_weighted_claim_scores,
            "q12": self.q12_domain_statistics,
        }
        if name not in mapping:
            raise ValueError(f"Unknown query: {name}")
        fn = mapping[name]
        sig = inspect.signature(fn)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters and v is not None}
        start = time.perf_counter()
        result = fn(**valid_kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        return {"query": name, "execution_time_ms": round(elapsed, 2), "result_count": len(result), "results": result}
