const API_BASE = import.meta.env.VITE_API_URL || ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  health: () => request<{
    status: string
    demo_mode: boolean
    database: Record<string, unknown>
    change_streams?: { active: boolean; fallback_mode?: boolean }
  }>('/api/health'),

  getDebates: (params?: { domain?: string; status?: string }) => {
    const q = new URLSearchParams()
    if (params?.domain) q.set('domain', params.domain)
    if (params?.status) q.set('status', params.status)
    return request<{ items: import('../types').Debate[]; total: number }>(`/api/debates?${q}`)
  },

  getDebate: (id: string) => request<import('../types').Debate>(`/api/debates/${id}`),

  createDebate: (data: { question: string; domain: string; description?: string }) =>
    request<import('../types').Debate>('/api/debates', { method: 'POST', body: JSON.stringify(data) }),

  updateDebate: (id: string, data: Partial<{ question: string; domain: string; description: string; status: string }>) =>
    request<import('../types').Debate>(`/api/debates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  deleteDebate: (id: string) => request<{ deleted: boolean }>(`/api/debates/${id}`, { method: 'DELETE' }),

  getClaimsByDebate: (debateId: string) =>
    request<import('../types').Claim[]>(`/api/claims/debate/${debateId}`),

  getClaim: (id: string) => request<import('../types').Claim>(`/api/claims/${id}`),

  getEvidenceByClaim: (claimId: string) =>
    request<import('../types').Evidence[]>(`/api/evidence/claim/${claimId}`),

  getEvidenceByDebate: async (debateId: string) => {
    const claims = await api.getClaimsByDebate(debateId)
    const all = await Promise.all(claims.map((c) => api.getEvidenceByClaim(c.id)))
    return all.flat()
  },

  getHistory: (debateId: string) =>
    request<import('../types').HistoryEvent[]>(`/api/history/${debateId}`),

  getGraph: (debateId: string) =>
    request<{ nodes: import('../types').GraphNode[]; edges: import('../types').GraphEdge[] }>(
      `/api/analysis/debate/${debateId}/graph`
    ),

  analyzeDebate: (debateId: string) =>
    request<Record<string, unknown>>('/api/ai/analyze', {
      method: 'POST',
      body: JSON.stringify({ debate_id: debateId }),
    }),

  search: (q: string) => request<import('../types').SearchResult[]>(`/api/search?q=${encodeURIComponent(q)}`),

  semanticSearch: (q: string) =>
    request<{ results: import('../types').SearchResult[]; fallback_used: boolean; message?: string }>(
      `/api/semantic-search?q=${encodeURIComponent(q)}`
    ),

  getOverview: () => request<Record<string, unknown>>('/api/analytics/overview'),

  getDatabaseSummary: () => request<{ database: string; collections: Record<string, number> }>('/api/analytics/database-summary'),

  getDatabaseHealth: () => request<Record<string, unknown>>('/api/analytics/database-health'),

  getIndexes: () => request<Array<{ collection: string; name: string; keys: Record<string, number> }>>('/api/analytics/indexes'),

  runQuery: (name: string, debateId?: string) => {
    const q = debateId ? `?debate_id=${debateId}` : ''
    return request<Record<string, unknown>>(`/api/analytics/queries/${name}${q}`)
  },

  getAggregations: () => ({
    proCon: () => request<unknown[]>('/api/analytics/aggregations/pro-con-confidence'),
    evidenceQuality: () => request<unknown[]>('/api/analytics/aggregations/evidence-quality'),
    evidencePerClaim: () => request<unknown[]>('/api/analytics/aggregations/evidence-per-claim'),
    topClaims: () => request<unknown[]>('/api/analytics/aggregations/top-claims'),
    contradictions: () => request<unknown[]>('/api/analytics/aggregations/contradiction-distribution'),
    domainStats: () => request<unknown[]>('/api/analytics/aggregations/domain-stats'),
  }),

  getContradictions: (debateId?: string) => {
    const q = debateId ? `?debate_id=${debateId}` : ''
    return request<unknown[]>(`/api/contradictions${q}`)
  },
}
