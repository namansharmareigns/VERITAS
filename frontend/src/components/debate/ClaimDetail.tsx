import type { Claim } from '../../types'
import { Card, CardTitle } from '../ui/card'
import { formatDate, formatScore } from '../../lib/utils'
import { X } from 'lucide-react'

interface ClaimDetailProps {
  claim: Claim
  onClose: () => void
}

export function ClaimDetail({ claim, onClose }: ClaimDetailProps) {
  const exp = claim.strength_explanation

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 p-4">
      <Card className="w-full max-w-lg max-h-[80vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${claim.position === 'PRO' ? 'bg-pro/20 text-pro' : 'bg-con/20 text-con'}`}>
              {claim.position}
            </span>
            <CardTitle className="mt-2">{claim.text}</CardTitle>
          </div>
          <button onClick={onClose} className="text-muted hover:text-text p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm mb-4">
          <div><span className="text-muted">Confidence</span><p className="font-semibold">{formatScore(claim.confidence)}</p></div>
          <div><span className="text-muted">Evidence</span><p className="font-semibold">{claim.evidence_ids.length}</p></div>
          <div><span className="text-muted">Counterarguments</span><p className="font-semibold">{claim.counterargument_ids.length}</p></div>
          <div><span className="text-muted">Status</span><p className="font-semibold capitalize">{claim.status}</p></div>
        </div>

        {exp && (
          <div className="border-t border-primary/10 pt-4">
            <p className="text-xs text-muted mb-2">{exp.framework}</p>
            <p className="text-sm font-medium mb-2">Why?</p>
            {exp.factors_positive?.map((f, i) => (
              <p key={i} className="text-sm text-success">{f}</p>
            ))}
            {exp.factors_negative?.map((f, i) => (
              <p key={i} className="text-sm text-warning">{f}</p>
            ))}
          </div>
        )}

        <p className="text-xs text-muted mt-4">
          Created {formatDate(claim.created_at)} • {claim.provenance?.generated_by as string || 'unknown'}
        </p>
      </Card>
    </div>
  )
}
