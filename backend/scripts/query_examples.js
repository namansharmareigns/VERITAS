// VERITAS MongoDB Query Examples (run in mongosh against veritas_db)

// Q1 — Fetch all debates
db.debates.find().sort({ created_at: -1 }).limit(50);

// Q2 — Fetch claims for a debate
db.claims.find({ debate_id: ObjectId("DEBATE_ID") }).sort({ confidence: -1 });

// Q3 — Compare PRO vs CON confidence
db.claims.aggregate([
  { $match: { debate_id: ObjectId("DEBATE_ID"), status: { $ne: "superseded" } } },
  { $group: { _id: "$position", avg_confidence: { $avg: "$confidence" }, count: { $sum: 1 } } }
]);

// Q4 — Strongest supporting evidence for a claim
db.evidence.find({ claim_id: ObjectId("CLAIM_ID"), supports: true }).sort({ evidence_score: -1 }).limit(5);

// Q5 — Strongest opposing evidence
db.evidence.find({ claim_id: ObjectId("CLAIM_ID"), supports: false }).sort({ evidence_score: -1 }).limit(5);

// Q6 — High-strength contradictions
db.contradictions.find({ strength: { $gte: 0.5 } }).sort({ strength: -1 });

// Q7 — Average evidence reliability by source type
db.evidence.aggregate([
  { $group: { _id: "$source_type", avg_reliability: { $avg: "$reliability_score" }, count: { $sum: 1 } } },
  { $sort: { avg_reliability: -1 } }
]);

// Q8 — Debate evolution over time
db.debate_history.find({ debate_id: ObjectId("DEBATE_ID") }).sort({ timestamp: 1 });

// Q9 — Low-confidence claims
db.claims.find({ confidence: { $lt: 0.4 }, status: "active" }).sort({ confidence: 1 });

// Q10 — Rank claims by confidence
db.claims.find({ status: { $ne: "superseded" } }).sort({ confidence: -1 }).limit(20);

// Q11 — Evidence-weighted claim score
db.claims.aggregate([
  { $match: { debate_id: ObjectId("DEBATE_ID") } },
  { $lookup: { from: "evidence", localField: "_id", foreignField: "claim_id", as: "evidence_items" } },
  { $addFields: { weighted_score: { $sum: { $map: { input: "$evidence_items", as: "e", in: { $cond: ["$$e.supports", "$$e.evidence_score", { $multiply: ["$$e.evidence_score", -0.5] }] } } } } } },
  { $sort: { weighted_score: -1 } }
]);

// Q12 — Debate/domain statistics
db.debates.aggregate([
  { $group: { _id: "$domain", debate_count: { $sum: 1 }, avg_confidence: { $avg: "$current_synthesis.confidence" } } },
  { $sort: { debate_count: -1 } }
]);
