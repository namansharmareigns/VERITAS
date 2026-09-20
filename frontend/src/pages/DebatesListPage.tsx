import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Loader2, Plus } from 'lucide-react'
import { formatDate, formatScore } from '../lib/utils'

export function DebatesListPage() {
  const { data, isLoading, isError, refetch } = useQuery({ queryKey: ['debates'], queryFn: () => api.getDebates() })

  if (isLoading) {
    return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Explore Debates</h1>
          <p className="text-muted mt-1">Browse persistent debate knowledge objects</p>
        </div>
        <Link to="/debates/new">
          <Button><Plus className="w-4 h-4" /> New Debate</Button>
        </Link>
      </div>

      {isError && (
        <Card className="border-danger/30">
          <p className="text-danger text-sm">Could not load debates. Is the backend running?</p>
          <Button variant="outline" size="sm" className="mt-3" onClick={() => refetch()}>Retry</Button>
        </Card>
      )}

      {!isError && !data?.items.length ? (
        <Card className="text-center py-12">
          <p className="text-muted mb-4">No debates yet.</p>
          <Link to="/debates/new" className="text-primary hover:underline">Start a Debate →</Link>
        </Card>
      ) : (
        <div className="grid gap-4">
          {(data?.items || []).map((d) => (
            <Link key={d.id} to={`/debates/${d.id}`}>
              <Card className="hover:border-primary/30 transition-colors cursor-pointer">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <span className="text-xs text-primary font-medium">{d.domain}</span>
                    <CardTitle className="text-base mt-1">{d.question}</CardTitle>
                    {d.description && <p className="text-xs text-muted mt-1 line-clamp-1">{d.description}</p>}
                    {d.metadata.development_fixture && (
                      <span className="text-xs text-warning mt-1 inline-block">Development fixture</span>
                    )}
                  </div>
                  <div className="flex gap-4 text-xs text-muted shrink-0">
                    <span>PRO {formatScore(d.current_synthesis.pro_score)}</span>
                    <span>CON {formatScore(d.current_synthesis.con_score)}</span>
                    <span>{formatDate(d.created_at)}</span>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
