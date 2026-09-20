import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid } from 'recharts'
import { formatScore } from '../lib/utils'
import { Loader2 } from 'lucide-react'

const COLORS = ['#67D9FF', '#FF6B7A', '#70E0A4', '#FFD166', '#A8E9FF']

export function DashboardPage() {
  const { data: overview, isLoading } = useQuery({ queryKey: ['overview'], queryFn: api.getOverview })
  const { data: domainStats } = useQuery({ queryKey: ['domainStats'], queryFn: api.getAggregations().domainStats })
  const { data: proCon } = useQuery({ queryKey: ['proCon'], queryFn: api.getAggregations().proCon })
  const { data: evidenceQuality } = useQuery({ queryKey: ['evidenceQuality'], queryFn: api.getAggregations().evidenceQuality })
  const { data: debates } = useQuery({ queryKey: ['debates'], queryFn: () => api.getDebates() })

  if (isLoading) {
    return <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
  }

  const stats: { label: string; value: string | number }[] = [
    { label: 'Total Debates', value: Number(overview?.total_debates ?? 0) },
    { label: 'Active Debates', value: Number(overview?.active_debates ?? 0) },
    { label: 'Claims', value: Number(overview?.total_claims ?? 0) },
    { label: 'Evidence', value: Number(overview?.total_evidence ?? 0) },
    { label: 'Contradictions', value: Number(overview?.total_contradictions ?? 0) },
    { label: 'Avg Confidence', value: formatScore(Number(overview?.avg_confidence ?? 0) || 0) },
  ]

  const domainChart = (domainStats as Array<{ _id: string; debate_count: number }> || []).map((d) => ({
    name: d._id,
    count: d.debate_count,
  }))

  const proConChart = (proCon as Array<{ _id: string; avg_confidence: number; count: number }> || []).map((d) => ({
    name: d._id,
    confidence: Math.round(d.avg_confidence * 100),
    count: d.count,
  }))

  const sourceChart = (evidenceQuality as Array<{ _id: string; count: number }> || []).map((d) => ({
    name: d._id?.replace('_', ' ') || 'unknown',
    value: d.count,
  }))

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted mt-1">Overview of debate activity and evidence landscape</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((s) => (
          <Card key={s.label} className="text-center">
            <p className="text-2xl font-bold text-primary">{s.value}</p>
            <p className="text-xs text-muted mt-1">{s.label}</p>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardTitle className="mb-4">Debate Domains</CardTitle>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={domainChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2535" />
              <XAxis dataKey="name" tick={{ fill: '#8EA5B5', fontSize: 11 }} />
              <YAxis tick={{ fill: '#8EA5B5', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0C131D', border: '1px solid #67D9FF33' }} />
              <Bar dataKey="count" fill="#67D9FF" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardTitle className="mb-4">PRO / CON Distribution</CardTitle>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={proConChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2535" />
              <XAxis dataKey="name" tick={{ fill: '#8EA5B5' }} />
              <YAxis tick={{ fill: '#8EA5B5' }} />
              <Tooltip contentStyle={{ background: '#0C131D', border: '1px solid #67D9FF33' }} />
              <Bar dataKey="confidence" fill="#A8E9FF" name="Avg Confidence %" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardTitle className="mb-4">Evidence Source Distribution</CardTitle>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={sourceChart} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {sourceChart.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#0C131D', border: '1px solid #67D9FF33' }} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardTitle className="mb-4">Recent Debates</CardTitle>
          <div className="space-y-2 max-h-[250px] overflow-y-auto">
            {(debates?.items || []).slice(0, 8).map((d) => (
              <Link key={d.id} to={`/debates/${d.id}`} className="block p-3 rounded-lg bg-surface-secondary/50 hover:bg-surface-secondary transition-colors">
                <p className="text-sm font-medium line-clamp-1">{d.question}</p>
                <p className="text-xs text-muted">{d.domain} • {d.status}</p>
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
