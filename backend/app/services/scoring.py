"""VERITAS proposed evidence-scoring framework."""

from typing import Any


def compute_evidence_score(
    reliability: float,
    relevance: float,
    independence: float,
    recency: float,
) -> float:
    """Evidence Score = Reliability × Relevance × Independence × Recency (normalized 0-1)."""
    score = reliability * relevance * independence * recency
    return round(min(max(score, 0.0), 1.0), 4)


def compute_claim_strength(
    supporting_evidence: list[dict[str, Any]],
    opposing_evidence: list[dict[str, Any]],
    counterarguments: list[dict[str, Any]],
    contradiction_penalty: float = 0.0,
) -> tuple[float, dict[str, Any]]:
    """Claim Strength = Supporting Evidence Contribution - Counterargument Penalty - Contradiction Penalty."""
    support_contrib = sum(e.get("evidence_score", 0.0) for e in supporting_evidence)
    oppose_contrib = sum(e.get("evidence_score", 0.0) for e in opposing_evidence) * 0.5
    counter_penalty = sum(c.get("strength", 0.0) for c in counterarguments) * 0.3

    raw = support_contrib - oppose_contrib - counter_penalty - contradiction_penalty
    normalized = min(max(0.5 + raw * 0.15, 0.0), 1.0)

    explanation = {
        "framework": "VERITAS proposed claim-strength framework",
        "supporting_evidence_count": len(supporting_evidence),
        "supporting_contribution": round(support_contrib, 4),
        "opposing_contribution": round(oppose_contrib, 4),
        "counterargument_penalty": round(counter_penalty, 4),
        "contradiction_penalty": round(contradiction_penalty, 4),
        "factors_positive": [
            f"+ {len(supporting_evidence)} supporting evidence item(s)"
        ] if supporting_evidence else [],
        "factors_negative": [],
    }
    if opposing_evidence:
        explanation["factors_negative"].append(f"- {len(opposing_evidence)} opposing evidence item(s)")
    if counterarguments:
        explanation["factors_negative"].append(f"- {len(counterarguments)} counterargument(s)")
    if contradiction_penalty > 0:
        explanation["factors_negative"].append("- Contextual disagreement or contradiction detected")

    return round(normalized, 4), explanation


def compute_debate_scores(pro_scores: list[float], con_scores: list[float]) -> dict[str, float]:
    pro_avg = sum(pro_scores) / len(pro_scores) if pro_scores else 0.0
    con_avg = sum(con_scores) / len(con_scores) if con_scores else 0.0
    confidence = min(max((pro_avg + con_avg) / 2, 0.0), 1.0)
    uncertainty = round(1.0 - abs(pro_avg - con_avg), 4) if pro_scores and con_scores else round(1.0 - confidence, 4)
    return {
        "pro_score": round(pro_avg, 4),
        "con_score": round(con_avg, 4),
        "confidence": round(confidence, 4),
        "uncertainty": round(min(max(uncertainty, 0.0), 1.0), 4),
    }
