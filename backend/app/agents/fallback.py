"""Deterministic local fallback when LLM provider is unavailable."""

from typing import Any


FALLBACK_CLAIMS: dict[str, list[dict[str, Any]]] = {
    "education": [
        {"position": "PRO", "text": "Generative AI can personalize learning pathways and provide scalable tutoring support.", "confidence": 0.72},
        {"position": "PRO", "text": "AI writing assistants can help students brainstorm and revise while preserving instructor oversight.", "confidence": 0.68},
        {"position": "CON", "text": "Generative AI increases academic integrity risks and may reduce authentic skill development.", "confidence": 0.75},
        {"position": "CON", "text": "Unequal access to premium AI tools may widen educational disparities.", "confidence": 0.70},
    ],
    "healthcare": [
        {"position": "PRO", "text": "AI diagnostic systems can augment clinician decision-making and improve early detection rates.", "confidence": 0.74},
        {"position": "CON", "text": "AI diagnostic tools may exhibit bias across demographic groups and require rigorous validation.", "confidence": 0.78},
    ],
    "transportation": [
        {"position": "PRO", "text": "Autonomous vehicles could reduce human-error accidents in controlled urban environments.", "confidence": 0.71},
        {"position": "CON", "text": "Wide urban deployment faces unresolved safety, liability, and infrastructure readiness challenges.", "confidence": 0.76},
    ],
    "environment": [
        {"position": "PRO", "text": "Stricter private vehicle restrictions can reduce emissions and improve urban air quality.", "confidence": 0.73},
        {"position": "CON", "text": "Restrictions may disproportionately affect commuters lacking viable public transit alternatives.", "confidence": 0.69},
    ],
    "technology": [
        {"position": "PRO", "text": "Mandatory AI content disclosure improves transparency and helps audiences evaluate information sources.", "confidence": 0.77},
        {"position": "CON", "text": "Disclosure requirements may be difficult to enforce and could be circumvented.", "confidence": 0.66},
    ],
}


def get_fallback_claims(domain: str, question: str) -> list[dict[str, Any]]:
    domain_key = domain.lower()
    for key, claims in FALLBACK_CLAIMS.items():
        if key in domain_key or key in question.lower():
            return claims
    return [
        {"position": "PRO", "text": f"There are evidence-informed reasons supporting affirmative positions on: {question}", "confidence": 0.65},
        {"position": "CON", "text": f"There are evidence-informed reasons supporting skeptical positions on: {question}", "confidence": 0.65},
    ]


def get_fallback_evidence(claim_text: str, supports: bool) -> dict[str, Any]:
    direction = "supporting" if supports else "opposing"
    return {
        "title": f"Development fixture: {direction} evidence for claim analysis",
        "content": (
            f"This development fixture represents {direction} evidence related to the claim. "
            "External source metadata unavailable in fallback mode. "
            f"Claim context: {claim_text[:120]}"
        ),
        "source_type": "user_provided",
        "supports": supports,
        "relevance": 0.65,
        "reliability_score": 0.55,
        "independence_score": 0.60,
        "recency_score": 0.70,
        "url": None,
    }


def get_fallback_counterargument(claim_text: str) -> dict[str, Any]:
    return {
        "text": f"A credible challenge to this claim is that the evidence base may be context-dependent: {claim_text[:80]}...",
        "strength": 0.55,
        "type": "qualification",
    }


def get_fallback_synthesis(question: str, pro_score: float, con_score: float) -> dict[str, Any]:
    if pro_score > con_score + 0.05:
        favor = "PRO position"
    elif con_score > pro_score + 0.05:
        favor = "CON position"
    else:
        favor = "balanced uncertainty between positions"

    confidence = (pro_score + con_score) / 2
    return {
        "synthesis": (
            f"Current evidence moderately supports analysis of: '{question}'. "
            f"The proposed framework currently favors the {favor}, but significant uncertainty remains. "
            "This synthesis was generated using deterministic fallback logic (no external LLM)."
        ),
        "confidence": round(confidence, 4),
        "pro_score": pro_score,
        "con_score": con_score,
        "uncertainty": round(1.0 - abs(pro_score - con_score), 4),
        "supporting_factors": ["Development fixture evidence weighted by VERITAS scoring framework"],
        "weaknesses": ["Fallback mode — external evidence retrieval not configured"],
        "unresolved_questions": ["Requires external validation with real source corpus"],
        "fallback_used": True,
    }
