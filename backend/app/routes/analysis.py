from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.analytics.queries import QueryService
from app.database import get_db
from app.services.contradiction_engine import find_and_store_contradictions
from app.utils.serialization import serialize_doc, serialize_docs

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/debate/{debate_id}")
def analyze_debate(debate_id: str):
    db = get_db()
    try:
        debate = db.debates.find_one({"_id": ObjectId(debate_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    qs = QueryService()
    claims = serialize_docs(qs.q2_claims_for_debate(debate_id))
    pro_con = qs.q3_pro_con_confidence(debate_id)
    weighted = serialize_docs(qs.q11_evidence_weighted_claim_scores(debate_id))
    contradictions = serialize_docs(qs.q6_high_strength_contradictions())

    claim_ids = [c["_id"] for c in db.claims.find({"debate_id": ObjectId(debate_id)}, {"_id": 1})]
    debate_contradictions = [c for c in contradictions if c.get("claim_a") in [str(i) for i in claim_ids] or c.get("claim_b") in [str(i) for i in claim_ids]]

    return {
        "debate": serialize_doc(debate),
        "claims": claims,
        "pro_con_confidence": pro_con,
        "weighted_scores": weighted,
        "contradictions": debate_contradictions,
    }


@router.get("/claim/{claim_id}")
def analyze_claim(claim_id: str):
    db = get_db()
    try:
        claim = db.claims.find_one({"_id": ObjectId(claim_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid claim ID")
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    qs = QueryService()
    supporting = serialize_docs(qs.q4_strongest_supporting_evidence(claim_id))
    opposing = serialize_docs(qs.q5_strongest_opposing_evidence(claim_id))
    counterarguments = serialize_docs(list(db.counterarguments.find({"claim_id": ObjectId(claim_id)})))

    return {
        "claim": serialize_doc(claim),
        "supporting_evidence": supporting,
        "opposing_evidence": opposing,
        "counterarguments": counterarguments,
    }


@router.post("/debate/{debate_id}/detect-contradictions")
def detect_contradictions(debate_id: str):
    created = find_and_store_contradictions(debate_id)
    return {"detected": len(created), "contradictions": serialize_docs(created)}


@router.get("/debate/{debate_id}/graph")
def get_debate_graph(debate_id: str):
    db = get_db()
    try:
        oid = ObjectId(debate_id)
        debate = db.debates.find_one({"_id": oid})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid debate ID")
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    nodes = [{"id": debate_id, "type": "question", "label": debate["question"][:80]}]
    edges = []

    claims = list(db.claims.find({"debate_id": oid}))
    for c in claims:
        cid = str(c["_id"])
        nodes.append({"id": cid, "type": f"{c['position']}_claim", "label": c["text"][:60], "position": c["position"], "confidence": c.get("confidence", 0)})
        edges.append({"source": debate_id, "target": cid, "type": "DERIVED_FROM"})

        for e in db.evidence.find({"claim_id": c["_id"]}):
            eid = str(e["_id"])
            nodes.append({"id": eid, "type": "evidence", "label": e["title"][:40], "score": e.get("evidence_score", 0)})
            edges.append({"source": eid, "target": cid, "type": "SUPPORTS" if e.get("supports") else "OPPOSES"})

        for ca in db.counterarguments.find({"claim_id": c["_id"]}):
            caid = str(ca["_id"])
            nodes.append({"id": caid, "type": "counterargument", "label": ca["text"][:40]})
            edges.append({"source": caid, "target": cid, "type": "ATTACKS"})

    claim_ids = [c["_id"] for c in claims]
    for ct in db.contradictions.find({"$or": [{"claim_a": {"$in": claim_ids}}, {"claim_b": {"$in": claim_ids}}]}):
        edges.append({
            "source": str(ct["claim_a"]),
            "target": str(ct["claim_b"]),
            "type": "CONTRADICTS",
            "strength": ct.get("strength", 0),
        })

    return {"nodes": nodes, "edges": edges}
