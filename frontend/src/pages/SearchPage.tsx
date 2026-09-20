import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Card, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Search, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'

export function SearchPage() {
  const [query, setQuery] = useState('')
  const [submitted, setSubmitted] = useState('')
  const [mode, setMode] = useState<'keyword' | 'semantic'>('keyword')

  const { data: keywordResults, isLoading: kwLoading } = useQuery({
    queryKey: ['search', submitted],
    queryFn: () => api.search(submitted),
    enabled: !!submitted && mode === 'keyword',
  })

  const { data: semanticData, isLoading: semLoading } = useQuery({
    queryKey: ['semantic', submitted],
    queryFn: () => api.semanticSearch(submitted),
    enabled: !!submitted && mode === 'semantic',
  })

  const results = mode === 'keyword' ? keywordResults : semanticData?.results
  const isLoading = mode === 'keyword' ? kwLoading : semLoading

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) setSubmitted(query.trim())
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Search</h1>
        <p className="text-muted mt-1">Search debates, claims, evidence, and sources</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What evidence discusses AI bias in medical diagnosis?"
            className="w-full bg-surface-secondary border border-primary/20 rounded-lg pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-primary/50"
          />
        </div>
        <Button type="submit">Search</Button>
      </form>

      <div className="flex gap-2">
        <button onClick={() => setMode('keyword')} className={`text-xs px-3 py-1 rounded-full ${mode === 'keyword' ? 'bg-primary/20 text-primary' : 'text-muted'}`}>Keyword</button>
        <button onClick={() => setMode('semantic')} className={`text-xs px-3 py-1 rounded-full ${mode === 'semantic' ? 'bg-primary/20 text-primary' : 'text-muted'}`}>Semantic</button>
      </div>

      {semanticData?.fallback_used && mode === 'semantic' && (
        <p className="text-warning text-xs">{semanticData.message || 'Semantic search fallback active'}</p>
      )}

      {isLoading && <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>}

      {submitted && !isLoading && (
        <Card>
          <CardTitle className="mb-4">{results?.length || 0} results for "{submitted}"</CardTitle>
          {!results?.length ? (
            <p className="text-muted text-sm">No results found.</p>
          ) : (
            <div className="space-y-3">
              {results.map((r) => (
                <div key={`${r.type}-${r.id}`} className="p-4 rounded-lg bg-surface-secondary/50">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs px-2 py-0.5 rounded bg-primary/20 text-primary capitalize">{r.type}</span>
                    {r.similarity && <span className="text-xs text-muted">sim: {r.similarity}</span>}
                  </div>
                  <p className="font-medium text-sm">{r.title}</p>
                  <p className="text-xs text-muted mt-1 line-clamp-2">{r.snippet}</p>
                  <p className="text-xs text-primary/70 mt-2">{r.match_reason}</p>
                  {r.type === 'debate' && <Link to={`/debates/${r.id}`} className="text-xs text-primary hover:underline mt-1 inline-block">Open debate →</Link>}
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
