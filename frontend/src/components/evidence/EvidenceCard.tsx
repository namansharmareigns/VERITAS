import type { Evidence } from '../../types'
import { formatDate, formatScore } from '../../lib/utils'
import { ExternalLink } from 'lucide-react'

interface EvidenceCardProps {
  evidence: Evidence
  claimText?: string
}

export function EvidenceCard({ evidence, claimText }: EvidenceCardProps) {
  return (
    <div className="glass rounded-xl p-4 border border-primary/5 hover:border-primary/20 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <h4 className="font-medium text-sm">{evidence.title}</h4>
        <span className={`text-xs px-2 py-0.5 rounded shrink-0 ${evidence.supports ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'}`}>
          {evidence.supports ? 'Supports' : 'Opposes'}
        </span>
      </div>
      <p className="text-xs text-muted mt-2 line-clamp-2">{evidence.content}</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 text-xs">
        <div><span className="text-muted">Reliability</span><p>{formatScore(evidence.reliability_score)}</p></div>
        <div><span className="text-muted">Relevance</span><p>{formatScore(evidence.relevance)}</p></div>
        <div><span className="text-muted">Score</span><p className="text-primary font-semibold">{formatScore(evidence.evidence_score)}</p></div>
        <div><span className="text-muted">Type</span><p className="capitalize">{evidence.source_type.replace('_', ' ')}</p></div>
      </div>
      {claimText && <p className="text-xs text-muted mt-2">Related claim: {claimText.slice(0, 60)}...</p>}
      <div className="flex items-center justify-between mt-3 text-xs text-muted">
        <span>{formatDate(evidence.published_at || evidence.added_at)}</span>
        {evidence.url ? (
          <a href={evidence.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-primary hover:underline">
            Source <ExternalLink className="w-3 h-3" />
          </a>
        ) : (
          <span>URL unavailable</span>
        )}
      </div>
    </div>
  )
}
