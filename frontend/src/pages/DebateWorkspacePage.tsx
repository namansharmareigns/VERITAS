import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import type { Claim } from '../types'
import { Card, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { ClaimPanel } from '../components/debate/ClaimPanel'
import { ClaimDetail } from '../components/debate/ClaimDetail'
import { DebateGraph } from '../components/graph/DebateGraph'
import { EvidenceCard } from '../components/evidence/EvidenceCard'
import { formatDate, formatScore } from '../lib/utils'
import { Loader2, Sparkles, AlertCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'

export function DebateWorkspacePage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null)
  const [evidenceFilter, setEvidenceFilter] = useState<string>('all')

  const { data: debate, isLoading } = useQuery({
    queryKey: ['debate', id],
    queryFn: () => api.getDebate(id!),
    enabled: !!id,
  })

  const { data: claims = [] } = useQuery({
    queryKey: ['claims', id],
    queryFn: () => api.getClaimsByDebate(id!),
    enabled: !!id,
  })

  const { data: evidence = [] } = useQuery({
    queryKey: ['evidence', id],
    queryFn: () => api.getEvidenceByDebate(id!),
    enabled: !!id,
  })

  const { data: history = [] } = useQuery({
    queryKey: ['history', id],
    queryFn: () => api.getHistory(id!),
    enabled: !!id,
  })

  const { data: graph } = useQuery({
    queryKey: ['graph', id],
    queryFn: () => api.getGraph(id!),
    enabled: !!id,
  })

  const analyzeMutation = useMutation({
    mutationFn: () => api.analyzeDebate(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['debate', id] })
      queryClient.invalidateQueries({ queryKey: ['claims', id] })
      queryClient.invalidateQueries({ queryKey: ['evidence', id] })
      queryClient.invalidateQueries({ queryKey: ['history', id] })
      queryClient.invalidateQueries({ queryKey: ['graph', id] })
    },
  })

  if (isLoading) {
    return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
  }

  if (!debate) {
    return <div className="text-center py-20 text-muted">Debate not found.</div>
  }

  const synth = debate.current_synthesis
  const filteredEvidence = evidence.filter((e) => {
    if (evidenceFilter === 'supports') return e.supports
    if (evidenceFilter === 'opposes') return !e.supports
    if (evidenceFilter !== 'all') return e.source_type === evidenceFilter
    return true
  })

  const historyChart = history.map((h) => ({
    time: new Date(h.timestamp).toLocaleDateString(),
    PRO: Math.round(h.pro_score * 100),
    CON: Math.round(h.con_score * 100),
    Confidence: Math.round(h.confidence * 100),
  }))

  const claimMap = Object.fromEntries(claims.map((c) => [c.id, c.text]))

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <span className="text-xs text-primary font-medium uppercase tracking-wider">{debate.domain}</span>
          <h1 className="text-2xl font-bold mt-1">{debate.question}</h1>
          <p className="text-sm text-muted mt-2">
            {debate.status} • Created {formatDate(debate.created_at)}
            {debate.metadata.development_fixture && ' • Development fixture'}
          </p>
        </div>
        <Button onClick={() => analyzeMutation.mutate()} disabled={analyzeMutation.isPending}>
          {analyzeMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          Generate Analysis
        </Button>
      </div>

      {analyzeMutation.isError && (
        <div className="flex items-center gap-2 text-danger text-sm bg-danger/10 p-3 rounded-lg">
          <AlertCircle className="w-4 h-4" /> {(analyzeMutation.error as Error).message}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        <ClaimPanel position="PRO" claims={claims} score={synth.pro_score} onSelectClaim={setSelectedClaim} />
        <ClaimPanel position="CON" claims={claims} score={synth.con_score} onSelectClaim={setSelectedClaim} />
      </div>

      <Card>
        <CardTitle className="mb-4">Debate Graph</CardTitle>
        <DebateGraph nodes={graph?.nodes || []} edges={graph?.edges || []} />
      </Card>

      <Card>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <CardTitle>Evidence Explorer</CardTitle>
          <div className="flex gap-2 flex-wrap">
            {['all', 'supports', 'opposes', 'research_paper', 'institutional', 'news'].map((f) => (
              <button
                key={f}
                onClick={() => setEvidenceFilter(f)}
                className={`text-xs px-3 py-1 rounded-full transition-colors ${evidenceFilter === f ? 'bg-primary/20 text-primary' : 'bg-surface-secondary text-muted hover:text-text'}`}
              >
                {f.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
        {filteredEvidence.length === 0 ? (
          <div className="text-center py-8 text-muted">
            <p>No evidence has been added yet.</p>
            <Button variant="outline" size="sm" className="mt-3" onClick={() => analyzeMutation.mutate()}>
              Find Evidence
            </Button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {filteredEvidence.map((e) => (
              <EvidenceCard key={e.id} evidence={e} claimText={claimMap[e.claim_id]} />
            ))}
          </div>
        )}
      </Card>

      <Card>
        <CardTitle className="mb-4">Temporal Evolution</CardTitle>
        {historyChart.length > 1 ? (
          <>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={historyChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2535" />
                <XAxis dataKey="time" tick={{ fill: '#8EA5B5', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8EA5B5', fontSize: 11 }} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: '#0C131D', border: '1px solid #67D9FF33' }} />
                <Legend />
                <Line type="monotone" dataKey="PRO" stroke="#67D9FF" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="CON" stroke="#FF6B7A" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Confidence" stroke="#70E0A4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
              {history.slice().reverse().map((h) => (
                <div key={h.id} className="flex items-start gap-3 text-xs border-l-2 border-primary/30 pl-3">
                  <span className="text-muted shrink-0">{formatDate(h.timestamp)}</span>
                  <div>
                    <span className="text-primary font-medium">{h.event_type.replace('_', ' ')}</span>
                    <p className="text-muted">{h.change_summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-muted text-sm">History will appear after evidence and analysis events.</p>
        )}
      </Card>

      <Card className="border border-primary/20">
        <CardTitle className="mb-4">Evidence-Weighted Synthesis</CardTitle>
        {synth.summary ? (
          <div className="space-y-4">
            <p className="text-sm leading-relaxed">{synth.summary}</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div><span className="text-xs text-muted">PRO Score</span><p className="text-xl font-bold text-pro">{formatScore(synth.pro_score)}</p></div>
              <div><span className="text-xs text-muted">CON Score</span><p className="text-xl font-bold text-con">{formatScore(synth.con_score)}</p></div>
              <div><span className="text-xs text-muted">Confidence</span><p className="text-xl font-bold text-success">{formatScore(synth.confidence)}</p></div>
              <div><span className="text-xs text-muted">Uncertainty</span><p className="text-xl font-bold text-warning">{formatScore(synth.uncertainty)}</p></div>
            </div>
            <p className="text-xs text-muted italic">
              Model-generated values represent proposed framework estimates, not objective truth.
            </p>
          </div>
        ) : (
          <p className="text-muted text-sm">Run analysis to generate evidence-weighted synthesis.</p>
        )}
      </Card>

      {selectedClaim && <ClaimDetail claim={selectedClaim} onClose={() => setSelectedClaim(null)} />}
    </div>
  )
}
