export interface CurrentSynthesis {
  summary: string | null
  confidence: number
  pro_score: number
  con_score: number
  uncertainty: number
}

export interface Debate {
  id: string
  question: string
  domain: string
  description: string | null
  status: string
  created_at: string
  updated_at: string
  current_synthesis: CurrentSynthesis
  metadata: {
    created_by: string | null
    language: string
    development_fixture?: boolean
  }
}

export interface Claim {
  id: string
  debate_id: string
  position: 'PRO' | 'CON'
  text: string
  normalized_text: string
  confidence: number
  status: string
  tags: string[]
  evidence_ids: string[]
  counterargument_ids: string[]
  created_at: string
  updated_at: string
  provenance: Record<string, unknown>
  strength_explanation?: {
    framework: string
    factors_positive: string[]
    factors_negative: string[]
  }
}

export interface Evidence {
  id: string
  claim_id: string
  source_id: string | null
  title: string
  content: string
  source_type: string
  supports: boolean
  relevance: number
  reliability_score: number
  independence_score: number
  recency_score: number
  evidence_score: number
  url: string | null
  published_at: string | null
  added_at: string
  provenance: Record<string, unknown>
}

export interface HistoryEvent {
  id: string
  debate_id: string
  timestamp: string
  pro_score: number
  con_score: number
  confidence: number
  evidence_count: number
  contradiction_count: number
  event_type: string
  change_summary: string
}

export interface GraphNode {
  id: string
  type: string
  label: string
  position?: string
  confidence?: number
  score?: number
}

export interface GraphEdge {
  source: string
  target: string
  type: string
  strength?: number
}

export interface SearchResult {
  type: string
  id: string
  title: string
  snippet: string
  match_reason: string
  similarity?: number
}
