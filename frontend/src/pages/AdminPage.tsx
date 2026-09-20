import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

export function AdminPage() {
  const { data: overview, isLoading } = useQuery({ queryKey: ['overview'], queryFn: api.getOverview })
  const { data: indexes } = useQuery({ queryKey: ['indexes'], queryFn: api.getIndexes })
  const { data: proCon } = useQuery({ queryKey: ['agg-procon'], queryFn: api.getAggregations().proCon })
  const { data: evidenceQuality } = useQuery({ queryKey: ['agg-eq'], queryFn: api.getAggregations().evidenceQuality })
  const { data: contradictions } = useQuery({ queryKey: ['agg-con'], queryFn: api.getAggregations().contradictions })

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics & Database</h1>
          <p className="text-muted mt-1">Internal analytics for academic demonstration</p>
        </div>
        <Link to="/database-health"><Button variant="outline">Database Health</Button></Link>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries((overview?.collections as Record<string, number>) || {}).map(([name, count]) => (
          <Card key={name} className="text-center">
            <p className="text-2xl font-bold text-primary">{count}</p>
            <p className="text-xs text-muted capitalize">{name.replace('_', ' ')}</p>
          </Card>
        ))}
      </div>

      <Card>
        <CardTitle className="mb-4">Indexes</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left border-b border-primary/10">
                <th className="pb-2 pr-4">Collection</th>
                <th className="pb-2 pr-4">Index</th>
                <th className="pb-2">Fields</th>
              </tr>
            </thead>
            <tbody>
              {(indexes || []).map((idx, i) => (
                <tr key={i} className="border-b border-primary/5">
                  <td className="py-2 pr-4">{idx.collection}</td>
                  <td className="py-2 pr-4 text-primary">{idx.name}</td>
                  <td className="py-2 text-muted font-mono text-xs">{JSON.stringify(idx.keys)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card>
          <CardTitle className="text-base mb-3">A1: PRO vs CON Confidence</CardTitle>
          <pre className="text-xs text-muted overflow-auto max-h-40">{JSON.stringify(proCon, null, 2)}</pre>
        </Card>
        <Card>
          <CardTitle className="text-base mb-3">A2: Evidence Quality by Source</CardTitle>
          <pre className="text-xs text-muted overflow-auto max-h-40">{JSON.stringify(evidenceQuality, null, 2)}</pre>
        </Card>
        <Card>
          <CardTitle className="text-base mb-3">A5: Contradiction Distribution</CardTitle>
          <pre className="text-xs text-muted overflow-auto max-h-40">{JSON.stringify(contradictions, null, 2)}</pre>
        </Card>
      </div>

      <Link to="/query-explorer"><Button variant="outline">Open Query Explorer →</Button></Link>
    </div>
  )
}
