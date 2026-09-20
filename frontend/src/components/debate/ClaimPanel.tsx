import type { Claim } from '../../types'
import { Card, CardHeader, CardTitle } from '../ui/card'
import { formatScore } from '../../lib/utils'
import { cn } from '../../lib/utils'

interface ClaimPanelProps {
  position: 'PRO' | 'CON'
  claims: Claim[]
  score: number
  onSelectClaim: (claim: Claim) => void
}

export function ClaimPanel({ position, claims, score, onSelectClaim }: ClaimPanelProps) {
  const isPro = position === 'PRO'
  const filtered = claims.filter((c) => c.position === position)

  return (
    <Card className={cn('border-t-2', isPro ? 'border-t-pro' : 'border-t-con')}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className={isPro ? 'text-pro' : 'text-con'}>{position}</CardTitle>
          <span className="text-2xl font-bold">{formatScore(score)}</span>
        </div>
        <p className="text-xs text-muted">{filtered.length} claims</p>
      </CardHeader>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {filtered.length === 0 ? (
          <p className="text-sm text-muted italic">No claims yet.</p>
        ) : (
          filtered.map((claim) => (
            <button
              key={claim.id}
              onClick={() => onSelectClaim(claim)}
              className="w-full text-left p-3 rounded-lg bg-surface-secondary/50 hover:bg-surface-secondary transition-colors border border-transparent hover:border-primary/20"
            >
              <p className="text-sm line-clamp-2">{claim.text}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted">Confidence: {formatScore(claim.confidence)}</span>
                <span className="text-xs text-muted">• {claim.evidence_ids.length} evidence</span>
              </div>
            </button>
          ))
        )}
      </div>
    </Card>
  )
}
