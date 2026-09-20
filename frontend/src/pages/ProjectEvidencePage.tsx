import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'

const FEATURES = [
  { rubric: 'NoSQL Model', feature: '9 Collections', status: 'COMPLETED', location: 'docs/data-model.md' },
  { rubric: 'CRUD', feature: 'Debates, Claims, Evidence APIs', status: 'COMPLETED', location: 'backend/app/routes/' },
  { rubric: 'Queries', feature: '12+ MongoDB Queries', status: 'COMPLETED', location: 'backend/app/analytics/queries.py' },
  { rubric: 'Indexes', feature: '8 Index Definitions', status: 'COMPLETED', location: 'backend/scripts/indexes.py' },
  { rubric: 'Aggregations', feature: '5 Aggregation Pipelines', status: 'COMPLETED', location: 'backend/app/analytics/service.py' },
  { rubric: 'AI Pipeline', feature: 'Agent abstraction + fallback', status: 'COMPLETED', location: 'backend/app/agents/' },
  { rubric: 'Temporal', feature: 'Debate history snapshots', status: 'COMPLETED', location: 'backend/app/services/temporal.py' },
  { rubric: 'Frontend', feature: 'React dashboard + debate workspace', status: 'COMPLETED', location: 'frontend/src/pages/' },
  { rubric: 'Connectivity', feature: 'FastAPI ↔ MongoDB ↔ React', status: 'COMPLETED', location: '/database-health' },
  { rubric: 'Seed Data', feature: 'Development fixtures', status: 'COMPLETED', location: 'backend/scripts/seed.py' },
]

export function ProjectEvidencePage() {
  const { data: summary, isLoading } = useQuery({ queryKey: ['db-summary'], queryFn: api.getDatabaseSummary })
  const { data: health } = useQuery({ queryKey: ['db-health'], queryFn: api.getDatabaseHealth })

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Project Evidence</h1>
        <p className="text-muted mt-1">Academic implementation evidence summary</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-sm text-muted">Database</p>
          <p className="text-xl font-bold text-primary">{summary?.database}</p>
        </Card>
        <Card className="text-center">
          <p className="text-sm text-muted">Connection</p>
          <p className="text-xl font-bold text-success">{health?.connected ? 'CONNECTED' : 'DISCONNECTED'}</p>
        </Card>
        <Card className="text-center">
          <p className="text-sm text-muted">Total Records</p>
          <p className="text-xl font-bold text-primary">
            {Object.values(summary?.collections || {}).reduce((a, b) => a + b, 0)}
          </p>
        </Card>
      </div>

      <Card>
        <CardTitle className="mb-4">Collection Counts (live from MongoDB)</CardTitle>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(summary?.collections || {}).map(([name, count]) => (
            <div key={name} className="bg-surface-secondary rounded-lg p-3 text-center">
              <p className="text-lg font-bold">{count}</p>
              <p className="text-xs text-muted">{name}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <CardTitle className="mb-4">Feature Implementation Map</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left border-b border-primary/10">
                <th className="pb-2 pr-4">Rubric</th>
                <th className="pb-2 pr-4">Feature</th>
                <th className="pb-2 pr-4">Status</th>
                <th className="pb-2">Location</th>
              </tr>
            </thead>
            <tbody>
              {FEATURES.map((f) => (
                <tr key={f.feature} className="border-b border-primary/5">
                  <td className="py-2 pr-4">{f.rubric}</td>
                  <td className="py-2 pr-4">{f.feature}</td>
                  <td className="py-2 pr-4"><span className="text-success text-xs font-medium">{f.status}</span></td>
                  <td className="py-2 text-muted font-mono text-xs">{f.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div className="flex gap-4 flex-wrap">
        <Link to="/admin" className="text-primary text-sm hover:underline">Analytics →</Link>
        <Link to="/query-explorer" className="text-primary text-sm hover:underline">Query Explorer →</Link>
        <Link to="/database-health" className="text-primary text-sm hover:underline">Database Health →</Link>
      </div>

      <p className="text-xs text-muted">
        Full evidence mapping: docs/REVIEW_2_RUBRIC_MAPPING.md • docs/PROJECT_EVIDENCE_TABLE.md • docs/SCREENSHOT_CHECKLIST.md
      </p>
    </div>
  )
}
