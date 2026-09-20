import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_db():
    db = get_db()
    for coll in ["debates", "claims", "evidence", "counterarguments", "contradictions", "sources", "debate_history", "embeddings"]:
        db[coll].delete_many({})
    yield


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "status" in r.json()


def test_create_and_get_debate():
    r = client.post("/api/debates", json={
        "question": "Should AI be used for medical diagnosis?",
        "domain": "Healthcare",
        "description": "Test debate",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["question"].startswith("Should AI")
    debate_id = data["id"]

    r2 = client.get(f"/api/debates/{debate_id}")
    assert r2.status_code == 200
    assert r2.json()["id"] == debate_id


def test_list_debates():
    client.post("/api/debates", json={"question": "Test Q1?", "domain": "Tech", "description": None})
    r = client.get("/api/debates")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_update_debate():
    r = client.post("/api/debates", json={"question": "Update test?", "domain": "Tech", "description": None})
    debate_id = r.json()["id"]
    r2 = client.put(f"/api/debates/{debate_id}", json={"status": "completed"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "completed"


def test_delete_debate():
    r = client.post("/api/debates", json={"question": "Delete test?", "domain": "Tech", "description": None})
    debate_id = r.json()["id"]
    r2 = client.delete(f"/api/debates/{debate_id}")
    assert r2.status_code == 200
    assert client.get(f"/api/debates/{debate_id}").status_code == 404


def test_create_claim():
    debate_id = client.post("/api/debates", json={"question": "Claim test?", "domain": "Tech", "description": None}).json()["id"]
    r = client.post("/api/claims", json={
        "debate_id": debate_id,
        "position": "PRO",
        "text": "AI improves diagnostic accuracy in controlled trials.",
        "confidence": 0.7,
    })
    assert r.status_code == 200
    assert r.json()["position"] == "PRO"


def test_get_claims_by_debate():
    debate_id = client.post("/api/debates", json={"question": "Claims list?", "domain": "Tech", "description": None}).json()["id"]
    client.post("/api/claims", json={"debate_id": debate_id, "position": "PRO", "text": "Pro claim", "confidence": 0.6})
    client.post("/api/claims", json={"debate_id": debate_id, "position": "CON", "text": "Con claim", "confidence": 0.55})
    r = client.get(f"/api/claims/debate/{debate_id}")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_create_evidence():
    debate_id = client.post("/api/debates", json={"question": "Evidence test?", "domain": "Tech", "description": None}).json()["id"]
    claim_id = client.post("/api/claims", json={"debate_id": debate_id, "position": "PRO", "text": "Claim", "confidence": 0.6}).json()["id"]
    r = client.post("/api/evidence", json={
        "claim_id": claim_id,
        "title": "Test evidence",
        "content": "Evidence content for testing scoring framework.",
        "source_type": "research_paper",
        "supports": True,
        "relevance": 0.8,
        "reliability_score": 0.7,
        "independence_score": 0.6,
        "recency_score": 0.9,
    })
    assert r.status_code == 200
    assert r.json()["evidence_score"] > 0


def test_aggregation_endpoints():
    r = client.get("/api/analytics/aggregations/evidence-quality")
    assert r.status_code == 200


def test_history_retrieval():
    debate_id = client.post("/api/debates", json={"question": "History test?", "domain": "Tech", "description": None}).json()["id"]
    r = client.get(f"/api/history/{debate_id}")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_database_summary():
    r = client.get("/api/analytics/database-summary")
    assert r.status_code == 200
    assert "collections" in r.json()
