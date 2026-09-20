import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

export function DatabaseHealthPage() {
  const { data: health, isLoading, refetch } = useQuery({
    queryKey: ['db-health'],
    queryFn: api.getDatabaseHealth,
    refetchInterval: 10000,
  })

  const { data: apiHealth } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 15000,
  })

  if (isLoading) return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>

  const connected = health?.connected

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Database Health</h1>
        <p className="text-muted mt-1">MongoDB connectivity demonstration</p>
      </div>

      <Card className="text-center py-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          {connected ? <CheckCircle className="w-10 h-10 text-success" /> : <XCircle className="w-10 h-10 text-danger" />}
          <span className="text-2xl font-bold">{connected ? 'CONNECTED' : 'DISCONNECTED'}</span>
        </div>
        <p className="text-muted">Database: <span className="text-primary font-mono">{health?.database as string}</span></p>
      </Card>

      <div className="grid sm:grid-cols-2 gap-4">
        <Card>
          <CardTitle className="text-base mb-2">Collections</CardTitle>
          <p className="text-3xl font-bold text-primary">{health?.collections as number ?? 0}</p>
        </Card>
        <Card>
          <CardTitle className="text-base mb-2">Total Records</CardTitle>
          <p className="text-3xl font-bold text-primary">{health?.total_records as number ?? 0}</p>
        </Card>
        <Card>
          <CardTitle className="text-base mb-2">Index Count</CardTitle>
          <p className="text-3xl font-bold text-primary">{health?.index_count as number ?? 0}</p>
        </Card>
        <Card>
          <CardTitle className="text-base mb-2">Response Latency</CardTitle>
          <p className="text-3xl font-bold text-primary">{health?.latency_ms as number ?? '—'} ms</p>
        </Card>
      </div>

      <Card>
        <CardTitle className="mb-4">Collection Counts</CardTitle>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {Object.entries((health?.collection_counts as Record<string, number>) || {}).map(([name, count]) => (
            <div key={name} className="bg-surface-secondary rounded-lg p-3 text-center">
              <p className="text-lg font-bold">{count}</p>
              <p className="text-xs text-muted capitalize">{name.replace('_', ' ')}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <CardTitle className="text-base mb-2">Last Successful Query</CardTitle>
        <p className="text-sm text-muted font-mono">{(health?.last_successful_query as string) || 'None'}</p>
      </Card>

      {apiHealth?.change_streams && (
        <Card>
          <CardTitle className="text-base mb-2">Change Streams</CardTitle>
          <p className="text-sm">
            Status:{' '}
            <span className={(apiHealth.change_streams as { active?: boolean }).active ? 'text-success' : 'text-warning'}>
              {(apiHealth.change_streams as { active?: boolean }).active ? 'Active' : 'Fallback mode'}
            </span>
          </p>
        </Card>
      )}

      {!connected && (
        <Card className="border-danger/30">
          <p className="text-danger text-sm">{health?.error as string || 'MongoDB unavailable'}</p>
        </Card>
      )}

      <button onClick={() => refetch()} className="text-primary text-sm hover:underline">Refresh status</button>
    </div>
  )
}
