# Temporal Debate Evolution

Every major state change creates a `debate_history` snapshot:

- evidence_added
- claim_added
- contradiction_detected
- confidence_updated
- synthesis_updated
- analysis_completed

Snapshots store pro_score, con_score, confidence, evidence_count, contradiction_count.

History is never deleted — enabling temporal visualization in the debate workspace.
