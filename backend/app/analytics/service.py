from typing import Any

from bson import ObjectId

from app.database import get_db, ping_db


class AnalyticsService:
    def __init__(self) -> None:
        self.db = get_db()

    def database_summary(self) -> dict[str, Any]:
        collections = ["debates", "claims", "evidence", "counterarguments", "contradictions", "sources", "debate_history"]
        counts = {c: self.db[c].count_documents({}) for c in collections}
        return {"database": self.db.name, "collections": counts}

    def overview(self) -> dict[str, Any]:
        ping = ping_db()
        return {
            **self.database_summary(),
            "health": ping,
            "total_debates": self.db.debates.count_documents({}),
            "active_debates": self.db.debates.count_documents({"status": "active"}),
            "total_claims": self.db.claims.count_documents({}),
            "total_evidence": self.db.evidence.count_documents({}),
            "total_contradictions": self.db.contradictions.count_documents({}),
            "avg_confidence": self._avg_field("debates", "current_synthesis.confidence"),
        }

    def _avg_field(self, collection: str, field: str) -> float:
        pipeline = [{"$group": {"_id": None, "avg": {"$avg": f"${field}"}}}]
        result = list(self.db[collection].aggregate(pipeline))
        return round(result[0]["avg"], 4) if result and result[0].get("avg") else 0.0

    # A1 — PRO vs CON average confidence
    def pro_con_avg_confidence(self, debate_id: str | None = None) -> list[dict]:
        match = {"debate_id": ObjectId(debate_id)} if debate_id else {}
        pipeline = [
            {"$match": {**match, "status": {"$ne": "superseded"}}},
            {"$group": {"_id": "$position", "avg_confidence": {"$avg": "$confidence"}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        return list(self.db.claims.aggregate(pipeline))

    # A2 — Evidence quality by source type
    def evidence_quality_by_source_type(self) -> list[dict]:
        pipeline = [
            {"$group": {
                "_id": "$source_type",
                "avg_reliability": {"$avg": "$reliability_score"},
                "avg_evidence_score": {"$avg": "$evidence_score"},
                "count": {"$sum": 1},
            }},
            {"$sort": {"avg_evidence_score": -1}},
        ]
        return list(self.db.evidence.aggregate(pipeline))

    # A3 — Evidence count per claim
    def evidence_count_per_claim(self, debate_id: str | None = None) -> list[dict]:
        match: dict[str, Any] = {}
        if debate_id:
            claim_ids = [c["_id"] for c in self.db.claims.find({"debate_id": ObjectId(debate_id)}, {"_id": 1})]
            match = {"claim_id": {"$in": claim_ids}}
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$claim_id", "evidence_count": {"$sum": 1}, "avg_score": {"$avg": "$evidence_score"}}},
            {"$sort": {"evidence_count": -1}},
            {"$limit": 20},
        ]
        return list(self.db.evidence.aggregate(pipeline))

    # A4 — Highest-scoring claims
    def highest_scoring_claims(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"status": {"$ne": "superseded"}}},
            {"$sort": {"confidence": -1}},
            {"$limit": limit},
            {"$project": {"text": 1, "position": 1, "confidence": 1, "debate_id": 1}},
        ]
        return list(self.db.claims.aggregate(pipeline))

    # A5 — Contradiction distribution
    def contradiction_distribution(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}, "avg_strength": {"$avg": "$strength"}}},
            {"$sort": {"count": -1}},
        ]
        return list(self.db.contradictions.aggregate(pipeline))

    def debate_analytics(self, debate_id: str) -> dict[str, Any]:
        oid = ObjectId(debate_id)
        debate = self.db.debates.find_one({"_id": oid})
        if not debate:
            return {}
        return {
            "debate_id": debate_id,
            "pro_con_confidence": self.pro_con_avg_confidence(debate_id),
            "evidence_per_claim": self.evidence_count_per_claim(debate_id),
            "contradiction_count": self.db.contradictions.count_documents({
                "$or": [
                    {"claim_a": {"$in": [c["_id"] for c in self.db.claims.find({"debate_id": oid}, {"_id": 1})]}},
                    {"claim_b": {"$in": [c["_id"] for c in self.db.claims.find({"debate_id": oid}, {"_id": 1})]}},
                ]
            }),
            "history_events": self.db.debate_history.count_documents({"debate_id": oid}),
        }

    def domain_statistics(self) -> list[dict]:
        pipeline = [
            {"$group": {
                "_id": "$domain",
                "debate_count": {"$sum": 1},
                "avg_pro_score": {"$avg": "$current_synthesis.pro_score"},
                "avg_con_score": {"$avg": "$current_synthesis.con_score"},
            }},
            {"$sort": {"debate_count": -1}},
        ]
        return list(self.db.debates.aggregate(pipeline))

    def list_indexes(self) -> list[dict]:
        result = []
        for coll_name in self.db.list_collection_names():
            for idx in self.db[coll_name].list_indexes():
                result.append({
                    "collection": coll_name,
                    "name": idx["name"],
                    "keys": idx["key"],
                })
        return result
