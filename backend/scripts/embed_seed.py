"""Generate local fallback embeddings for claims and evidence (development)."""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.database import get_db


def local_embed(text: str, dim: int = 64) -> list[float]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        vec[i % dim] += hash(tok) % 100 / 100.0
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [round(v / norm, 6) for v in vec]


def seed_embeddings() -> None:
    db = get_db()
    settings = get_settings()
    model = settings.embedding_model
    now = datetime.now(timezone.utc)
    created = 0

    for claim in db.claims.find({}, {"text": 1}):
        existing = db.embeddings.find_one({"entity_type": "claim", "entity_id": claim["_id"]})
        if existing:
            continue
        db.embeddings.insert_one({
            "entity_type": "claim",
            "entity_id": claim["_id"],
            "embedding": local_embed(claim["text"]),
            "model": f"{model}-local-fallback",
            "created_at": now,
        })
        created += 1

    for ev in db.evidence.find({}, {"title": 1, "content": 1}):
        existing = db.embeddings.find_one({"entity_type": "evidence", "entity_id": ev["_id"]})
        if existing:
            continue
        text = f"{ev.get('title', '')} {ev.get('content', '')}"
        db.embeddings.insert_one({
            "entity_type": "evidence",
            "entity_id": ev["_id"],
            "embedding": local_embed(text),
            "model": f"{model}-local-fallback",
            "created_at": now,
        })
        created += 1

    print(f"Embeddings created: {created}")


if __name__ == "__main__":
    seed_embeddings()
