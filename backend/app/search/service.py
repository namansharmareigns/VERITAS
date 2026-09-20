import math
import re
from typing import Any

from bson import ObjectId

from app.agents.llm_provider import EmbeddingProvider
from app.database import get_db


class SearchService:
    def __init__(self) -> None:
        self.db = get_db()
        self.embedder = EmbeddingProvider()

    def keyword_search(
        self,
        query: str,
        entity_types: list[str] | None = None,
        domain: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        types = entity_types or ["debates", "claims", "evidence", "sources"]

        if "debates" in types:
            filt: dict[str, Any] = {"$or": [
                {"question": pattern}, {"description": pattern}, {"domain": pattern}
            ]}
            if domain:
                filt["domain"] = re.compile(domain, re.IGNORECASE)
            for d in self.db.debates.find(filt).limit(limit):
                results.append({"type": "debate", "id": str(d["_id"]), "title": d["question"],
                                "snippet": d.get("description", "")[:200], "match_reason": "Keyword match in debate fields"})

        if "claims" in types:
            for c in self.db.claims.find({"text": pattern}).limit(limit):
                results.append({"type": "claim", "id": str(c["_id"]), "title": c["text"][:100],
                                "snippet": c["text"], "match_reason": "Keyword match in claim text"})

        if "evidence" in types:
            for e in self.db.evidence.find({"$or": [{"title": pattern}, {"content": pattern}]}).limit(limit):
                results.append({"type": "evidence", "id": str(e["_id"]), "title": e["title"],
                                "snippet": e["content"][:200], "match_reason": "Keyword match in evidence"})

        if "sources" in types:
            for s in self.db.sources.find({"title": pattern}).limit(limit):
                results.append({"type": "source", "id": str(s["_id"]), "title": s["title"],
                                "snippet": s.get("publisher", ""), "match_reason": "Keyword match in source title"})

        return results[:limit]

    async def semantic_search(
        self,
        query: str,
        min_reliability: float = 0.0,
        source_type: str | None = None,
        supports: bool | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        query_vec = await self.embedder.embed(query)
        if not query_vec:
            return {"results": [], "fallback_used": True, "message": "Semantic search unavailable"}

        embeddings = list(self.db.embeddings.find({"entity_type": {"$in": ["claim", "evidence"]}}))
        if not embeddings:
            return {
                "results": self.keyword_search(query, entity_types=["evidence", "claims"], limit=limit),
                "fallback_used": True,
                "message": "No embeddings indexed; keyword fallback used",
            }

        scored = []
        for emb in embeddings:
            sim = _cosine_similarity(query_vec, emb.get("embedding", []))
            if sim > 0.1:
                scored.append((sim, emb))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for sim, emb in scored[:limit * 2]:
            entity = None
            if emb["entity_type"] == "evidence":
                entity = self.db.evidence.find_one({"_id": emb["entity_id"]})
            elif emb["entity_type"] == "claim":
                entity = self.db.claims.find_one({"_id": emb["entity_id"]})
            if not entity:
                continue
            if source_type and entity.get("source_type") != source_type:
                continue
            if min_reliability and entity.get("reliability_score", 0) < min_reliability:
                continue
            if supports is not None and entity.get("supports") != supports:
                continue
            title = entity.get("title") or entity.get("text", "")[:100]
            results.append({
                "type": emb["entity_type"],
                "id": str(emb["entity_id"]),
                "title": title,
                "snippet": (entity.get("content") or entity.get("text", ""))[:200],
                "similarity": round(sim, 4),
                "match_reason": f"Semantic similarity ({sim:.2f})",
            })
            if len(results) >= limit:
                break

        return {"results": results, "fallback_used": False}


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        min_len = min(len(a), len(b)) if a and b else 0
        if min_len == 0:
            return 0.0
        a, b = a[:min_len], b[:min_len]
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)
