# Indexing Strategy

Created by `python scripts/indexes.py`

| Collection | Index | Purpose |
|------------|-------|---------|
| debates | (domain, created_at) | Domain-filtered listing |
| claims | (debate_id, position, confidence) | Debate workspace queries |
| evidence | (claim_id, supports, reliability_score, relevance) | Evidence ranking |
| contradictions | (strength) | High-strength queries |
| debate_history | (debate_id, timestamp) | Temporal timeline |
| sources | (source_type, published_at) | Source filtering |
| embeddings | (entity_type, entity_id) | Semantic lookup |
| counterarguments | (claim_id) | Per-claim lookup |
