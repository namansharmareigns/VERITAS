import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.agents.fallback import (
    get_fallback_claims,
    get_fallback_counterargument,
    get_fallback_evidence,
    get_fallback_synthesis,
)
from app.agents.llm_provider import LLMProvider
from app.database import get_db
from app.services.claim_strength import recalculate_claim_strength
from app.services.contradiction_engine import find_and_store_contradictions
from app.services.scoring import compute_evidence_score
from app.services.temporal import recalculate_debate_scores, record_history_event

logger = logging.getLogger(__name__)


class DebateAnalysisPipeline:
    def __init__(self) -> None:
        self.llm = LLMProvider()

    async def analyze_debate(self, debate_id: str) -> dict[str, Any]:
        db = get_db()
        debate = db.debates.find_one({"_id": ObjectId(debate_id)})
        if not debate:
            raise ValueError("Debate not found")

        fallback_used = not self.llm.is_available
        claims_created = 0
        evidence_created = 0
        counterarguments_created = 0

        existing_claims = db.claims.count_documents({"debate_id": ObjectId(debate_id)})
        if existing_claims == 0:
            claims_data = await self._generate_claims(debate, fallback_used)
            for c in claims_data:
                doc = self._build_claim_doc(debate_id, c)
                result = db.claims.insert_one(doc)
                claims_created += 1
                claim_id = str(result.inserted_id)
                ev = get_fallback_evidence(c["text"], supports=True)
                self._insert_evidence(claim_id, ev, debate)
                evidence_created += 1
                ca = get_fallback_counterargument(c["text"])
                ca_doc = {
                    "claim_id": ObjectId(claim_id),
                    "text": ca["text"],
                    "strength": ca["strength"],
                    "type": ca["type"],
                    "generated_by": "ai" if not fallback_used else "fallback",
                    "created_at": datetime.now(timezone.utc),
                }
                ca_result = db.counterarguments.insert_one(ca_doc)
                db.claims.update_one(
                    {"_id": ObjectId(claim_id)},
                    {"$push": {"counterargument_ids": ca_result.inserted_id}},
                )
                counterarguments_created += 1
                recalculate_claim_strength(claim_id)

        contradictions = find_and_store_contradictions(debate_id)
        scores = recalculate_debate_scores(debate_id)
        synthesis = get_fallback_synthesis(debate["question"], scores["pro_score"], scores["con_score"])

        if self.llm.is_available:
            llm_synthesis = await self.llm.generate_json(
                "You are a synthesis agent for VERITAS debate framework. Return JSON with keys: "
                "synthesis, confidence, supporting_factors, weaknesses, unresolved_questions. "
                "Never claim objective truth. Represent uncertainty.",
                f"Question: {debate['question']}\nPRO score: {scores['pro_score']}\nCON score: {scores['con_score']}",
            )
            if llm_synthesis:
                synthesis.update({
                    "synthesis": llm_synthesis.get("synthesis", synthesis["synthesis"]),
                    "supporting_factors": llm_synthesis.get("supporting_factors", synthesis["supporting_factors"]),
                    "weaknesses": llm_synthesis.get("weaknesses", synthesis["weaknesses"]),
                    "unresolved_questions": llm_synthesis.get("unresolved_questions", synthesis["unresolved_questions"]),
                    "fallback_used": False,
                })

        db.debates.update_one(
            {"_id": ObjectId(debate_id)},
            {
                "$set": {
                    "current_synthesis.summary": synthesis["synthesis"],
                    "current_synthesis.confidence": synthesis["confidence"],
                    "current_synthesis.pro_score": synthesis["pro_score"],
                    "current_synthesis.con_score": synthesis["con_score"],
                    "current_synthesis.uncertainty": synthesis["uncertainty"],
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        record_history_event(
            debate_id,
            "analysis_completed",
            "AI-assisted analysis completed; scores and synthesis updated.",
        )

        return {
            "claims_created": claims_created,
            "evidence_created": evidence_created,
            "counterarguments_created": counterarguments_created,
            "contradictions_detected": len(contradictions),
            "synthesis": synthesis,
            "fallback_used": fallback_used or synthesis.get("fallback_used", False),
        }

    async def _generate_claims(self, debate: dict, fallback: bool) -> list[dict[str, Any]]:
        if fallback:
            return get_fallback_claims(debate.get("domain", ""), debate["question"])
        prompt = await self.llm.generate_json(
            "Generate debate claims as JSON with key 'claims' array. Each item: position (PRO|CON), text, confidence (0-1).",
            f"Question: {debate['question']}\nDomain: {debate.get('domain')}",
        )
        if prompt and "claims" in prompt:
            return prompt["claims"]
        return get_fallback_claims(debate.get("domain", ""), debate["question"])

    def _build_claim_doc(self, debate_id: str, claim: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        text = claim["text"]
        return {
            "debate_id": ObjectId(debate_id),
            "position": claim["position"],
            "text": text,
            "normalized_text": text.lower().strip(),
            "confidence": claim.get("confidence", 0.5),
            "status": "active",
            "tags": [],
            "evidence_ids": [],
            "counterargument_ids": [],
            "created_at": now,
            "updated_at": now,
            "provenance": {"generated_by": "ai", "source_context": "debate_analysis_pipeline"},
        }

    def _insert_evidence(self, claim_id: str, ev: dict[str, Any], debate: dict) -> None:
        db = get_db()
        score = compute_evidence_score(
            ev["reliability_score"], ev["relevance"], ev["independence_score"], ev["recency_score"]
        )
        doc = {
            "claim_id": ObjectId(claim_id),
            "source_id": None,
            "title": ev["title"],
            "content": ev["content"],
            "source_type": ev.get("source_type", "user_provided"),
            "supports": ev.get("supports", True),
            "relevance": ev["relevance"],
            "reliability_score": ev["reliability_score"],
            "independence_score": ev["independence_score"],
            "recency_score": ev["recency_score"],
            "evidence_score": score,
            "url": ev.get("url"),
            "published_at": None,
            "added_at": datetime.now(timezone.utc),
            "provenance": {
                "generated_by": "agent",
                "development_fixture": debate.get("metadata", {}).get("development_fixture", False),
            },
        }
        result = db.evidence.insert_one(doc)
        db.claims.update_one({"_id": ObjectId(claim_id)}, {"$push": {"evidence_ids": result.inserted_id}})
