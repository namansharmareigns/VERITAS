"""Create MongoDB indexes for VERITAS collections."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db

INDEXES = [
    ("debates", [("domain", 1), ("created_at", -1)], "Domain-filtered debate listing"),
    ("claims", [("debate_id", 1), ("position", 1), ("confidence", -1)], "Debate claims by position and confidence"),
    ("evidence", [("claim_id", 1), ("supports", 1), ("reliability_score", -1), ("relevance", -1)], "Evidence lookup and ranking"),
    ("contradictions", [("strength", -1)], "High-strength contradiction queries"),
    ("debate_history", [("debate_id", 1), ("timestamp", 1)], "Temporal evolution timeline"),
    ("sources", [("source_type", 1), ("published_at", -1)], "Source type and recency filtering"),
    ("embeddings", [("entity_type", 1), ("entity_id", 1)], "Embedding lookup by entity"),
    ("counterarguments", [("claim_id", 1)], "Counterarguments per claim"),
]


def create_indexes() -> None:
    db = get_db()
    for collection, keys, reason in INDEXES:
        name = db[collection].create_index(keys)
        print(f"  [{collection}] {name} — {reason}")
    print("Indexes created successfully.")


if __name__ == "__main__":
    create_indexes()
