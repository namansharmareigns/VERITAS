import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Loader2 } from 'lucide-react'

const QUERIES = [
  { id: 'q1', name: 'Q1 — Fetch all debates', needsDebate: false },
  { id: 'q2', name: 'Q2 — Claims for debate', needsDebate: true },
  { id: 'q3', name: 'Q3 — PRO vs CON confidence', needsDebate: true },
  { id: 'q6', name: 'Q6 — High-strength contradictions', needsDebate: false },
  { id: 'q7', name: 'Q7 — Avg reliability by source type', needsDebate: false },
  { id: 'q9', name: 'Q9 — Low-confidence claims', needsDebate: false },
  { id: 'q10', name: 'Q10 — Rank claims by confidence', needsDebate: false },
  { id: 'q11', name: 'Q11 — Evidence-weighted claim scores', needsDebate: true },
  { id: 'q12', name: 'Q12 — Domain statistics', needsDebate: false },
]

export function QueryExplorerPage() {
  const [selected, setSelected] = useState('q1')
  const [debateId, setDebateId] = useState('')
  const [run, setRun] = useState(false)

  const { data: debates } = useQuery({ queryKey: ['debates'], queryFn: () => api.getDebates() })

  const { data: result, isLoading } = useQuery({
    queryKey: ['query', selected, debateId, run],
    queryFn: () => api.runQuery(selected, q?.needsDebate ? debateId : undefined),
    enabled: run,
  })

  const q = QUERIES.find((q) => q.id === selected)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Query Explorer</h1>
        <p className="text-muted mt-1">Prebuilt safe academic MongoDB queries</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardTitle className="mb-4">Queries</CardTitle>
          <div className="space-y-1">
            {QUERIES.map((q) => (
              <button
                key={q.id}
                onClick={() => { setSelected(q.id); setRun(false) }}
                className={`w-full text-left text-sm px-3 py-2 rounded-lg transition-colors ${selected === q.id ? 'bg-primary/15 text-primary' : 'hover:bg-surface-secondary text-muted'}`}
              >
                {q.name}
              </button>
            ))}
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <CardTitle className="mb-4">{q?.name}</CardTitle>

          {q?.needsDebate && (
            <select
              value={debateId}
              onChange={(e) => setDebateId(e.target.value)}
              className="w-full bg-surface-secondary border border-primary/20 rounded-lg px-4 py-2 text-sm mb-4"
            >
              <option value="">Select debate...</option>
              {(debates?.items || []).map((d) => (
                <option key={d.id} value={d.id}>{d.question.slice(0, 60)}</option>
              ))}
            </select>
          )}

          <Button onClick={() => setRun(true)} disabled={q?.needsDebate && !debateId}>
            Run Query
          </Button>

          {isLoading && <Loader2 className="w-5 h-5 animate-spin text-primary mt-4" />}

          {result && (
            <div className="mt-4 space-y-2">
              <div className="flex gap-4 text-xs text-muted">
                <span>Execution: {result.execution_time_ms as number} ms</span>
                <span>Results: {result.result_count as number}</span>
              </div>
              <pre className="bg-surface-secondary rounded-lg p-4 text-xs overflow-auto max-h-96 text-muted">
                {JSON.stringify(result.results, null, 2)}
              </pre>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
