"""Seed development fixture data for VERITAS."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bson import ObjectId

from app.database import get_db
from app.services.contradiction_engine import find_and_store_contradictions
from app.services.scoring import compute_debate_scores, compute_evidence_score
from app.services.temporal import record_history_event

DEBATES = [
    {"question": "Should AI be used for medical diagnosis?", "domain": "Healthcare", "description": "Examining AI-assisted diagnostic tools in clinical settings."},
    {"question": "Should autonomous vehicles be widely deployed in cities?", "domain": "Transportation", "description": "Urban AV deployment feasibility and safety."},
    {"question": "Should generative AI be used in university education?", "domain": "Education", "description": "AI in higher education teaching and assessment."},
    {"question": "Should cities impose stricter restrictions on private vehicles?", "domain": "Environment", "description": "Urban mobility policy and emissions reduction."},
    {"question": "Should AI-generated content require mandatory disclosure?", "domain": "Technology", "description": "Transparency requirements for synthetic media."},
]

SOURCE_TYPES = ["research_paper", "institutional", "news", "dataset", "web"]


def clear_fixtures() -> None:
    db = get_db()
    debate_ids = [d["_id"] for d in db.debates.find({"metadata.development_fixture": True}, {"_id": 1})]
    if not debate_ids:
        print("No fixtures to clear.")
        return
    claim_ids = [c["_id"] for c in db.claims.find({"debate_id": {"$in": debate_ids}}, {"_id": 1})]
    db.evidence.delete_many({"claim_id": {"$in": claim_ids}})
    db.counterarguments.delete_many({"claim_id": {"$in": claim_ids}})
    db.contradictions.delete_many({"$or": [{"claim_a": {"$in": claim_ids}}, {"claim_b": {"$in": claim_ids}}]})
    db.claims.delete_many({"debate_id": {"$in": debate_ids}})
    db.debate_history.delete_many({"debate_id": {"$in": debate_ids}})
    db.debates.delete_many({"_id": {"$in": debate_ids}})
    print(f"Cleared {len(debate_ids)} fixture debates.")


def seed() -> None:
    db = get_db()
    now = datetime.now(timezone.utc)
    stats = {"debates": 0, "claims": 0, "evidence": 0, "counterarguments": 0, "contradictions": 0, "sources": 0, "history": 0}

    # Sources
    sources = []
    for i in range(22):
        src = {
            "title": f"Development fixture source {i + 1}",
            "authors": [f"Author {i}"],
            "publisher": "VERITAS Dev Corpus",
            "source_type": SOURCE_TYPES[i % len(SOURCE_TYPES)],
            "url": None,
            "published_at": now - timedelta(days=30 * (i + 1)),
            "reliability": round(0.5 + (i % 5) * 0.1, 2),
            "metadata": {"development_fixture": True},
            "created_at": now,
        }
        sources.append(src)
    src_results = db.sources.insert_many(sources)
    stats["sources"] = len(src_results.inserted_ids)

    pro_templates = [
        "Evidence suggests significant benefits in {domain} contexts when properly validated.",
        "Institutional reports indicate measurable improvements from adoption.",
        "Peer-reviewed studies support cautious but affirmative deployment.",
        "Pilot programs demonstrate feasibility with appropriate safeguards.",
    ]
    con_templates = [
        "Significant risks remain unaddressed including bias and accountability gaps.",
        "Regulatory frameworks are insufficient for safe widespread adoption.",
        "Equity concerns may worsen existing disparities in {domain}.",
        "Long-term effects require further empirical evaluation before deployment.",
    ]

    for di, debate_data in enumerate(DEBATES):
        debate_doc = {
            **debate_data,
            "status": "active",
            "created_at": now - timedelta(days=10 - di),
            "updated_at": now,
            "current_synthesis": {"summary": None, "confidence": 0.0, "pro_score": 0.0, "con_score": 0.0, "uncertainty": 1.0},
            "metadata": {"created_by": "seed_script", "language": "en", "development_fixture": True},
        }
        d_result = db.debates.insert_one(debate_doc)
        debate_id = d_result.inserted_id
        stats["debates"] += 1

        record_history_event(str(debate_id), "debate_created", "Development fixture debate seeded.")
        stats["history"] += 1

        claims = []
        for pi, tmpl in enumerate(pro_templates[:2 + di % 2]):
            text = tmpl.format(domain=debate_data["domain"])
            claims.append({"position": "PRO", "text": text, "confidence": round(0.6 + pi * 0.05, 2)})
        for ci, tmpl in enumerate(con_templates[:2 + di % 2]):
            text = tmpl.format(domain=debate_data["domain"])
            claims.append({"position": "CON", "text": text, "confidence": round(0.58 + ci * 0.06, 2)})

        for ci, c in enumerate(claims):
            claim_doc = {
                "debate_id": debate_id,
                "position": c["position"],
                "text": c["text"],
                "normalized_text": c["text"].lower(),
                "confidence": c["confidence"],
                "status": "active",
                "tags": [debate_data["domain"].lower()],
                "evidence_ids": [],
                "counterargument_ids": [],
                "created_at": now - timedelta(hours=ci),
                "updated_at": now,
                "provenance": {"generated_by": "retrieval", "source_context": "seed_script", "development_fixture": True},
            }
            cr = db.claims.insert_one(claim_doc)
            stats["claims"] += 1
            claim_id = cr.inserted_id

            for ei in range(2):
                rel = round(0.55 + ei * 0.1, 2)
                rel_score = round(0.5 + (ci + ei) % 4 * 0.1, 2)
                ind = round(0.55 + ei * 0.08, 2)
                rec = round(0.6 + ei * 0.05, 2)
                score = compute_evidence_score(rel_score, rel, ind, rec)
                src_id = src_results.inserted_ids[(di * 4 + ci * 2 + ei) % len(src_results.inserted_ids)]
                ev_doc = {
                    "claim_id": claim_id,
                    "source_id": src_id,
                    "title": f"Fixture evidence for {c['position']} claim {ci + 1}",
                    "content": f"Development fixture evidence content supporting analysis in {debate_data['domain']}. Not experimental evidence.",
                    "source_type": SOURCE_TYPES[(ci + ei) % len(SOURCE_TYPES)],
                    "supports": ei == 0,
                    "relevance": rel,
                    "reliability_score": rel_score,
                    "independence_score": ind,
                    "recency_score": rec,
                    "evidence_score": score,
                    "url": None,
                    "published_at": now - timedelta(days=60 + ei * 10),
                    "added_at": now - timedelta(hours=ei),
                    "provenance": {"generated_by": "retrieval", "development_fixture": True},
                }
                er = db.evidence.insert_one(ev_doc)
                db.claims.update_one({"_id": claim_id}, {"$push": {"evidence_ids": er.inserted_id}})
                stats["evidence"] += 1

            ca_doc = {
                "claim_id": claim_id,
                "text": f"Counterargument: the claim may not generalize across all {debate_data['domain']} contexts.",
                "strength": round(0.4 + ci * 0.05, 2),
                "type": "qualification" if ci % 2 else "rebuttal",
                "generated_by": "ai",
                "created_at": now,
            }
            car = db.counterarguments.insert_one(ca_doc)
            db.claims.update_one({"_id": claim_id}, {"$push": {"counterargument_ids": car.inserted_id}})
            stats["counterarguments"] += 1

        contradictions = find_and_store_contradictions(str(debate_id))
        stats["contradictions"] += len(contradictions)

        pro_scores = [c["confidence"] for c in claims if c["position"] == "PRO"]
        con_scores = [c["confidence"] for c in claims if c["position"] == "CON"]
        scores = compute_debate_scores(pro_scores, con_scores)
        db.debates.update_one(
            {"_id": debate_id},
            {"$set": {
                "current_synthesis.pro_score": scores["pro_score"],
                "current_synthesis.con_score": scores["con_score"],
                "current_synthesis.confidence": scores["confidence"],
                "current_synthesis.uncertainty": scores["uncertainty"],
                "current_synthesis.summary": "Development fixture synthesis — to be evaluated with real evidence corpus.",
            }},
        )

        for hi, event in enumerate(["evidence_added", "claim_challenged", "contradiction_detected", "confidence_updated", "synthesis_updated"]):
            record_history_event(str(debate_id), event, f"Fixture history event: {event}")
            stats["history"] += 1

    print("Seed complete:", stats)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from embed_seed import seed_embeddings
    seed_embeddings()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()
    if args.clear:
        clear_fixtures()
    seed()
