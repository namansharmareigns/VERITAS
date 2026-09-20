import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { Card, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Loader2 } from 'lucide-react'

const schema = z.object({
  question: z.string().min(5, 'Question must be at least 5 characters'),
  domain: z.string().min(2, 'Domain is required'),
  description: z.string().optional(),
})

type FormData = z.infer<typeof schema>

const domains = ['Healthcare', 'Education', 'Transportation', 'Environment', 'Technology']

export function CreateDebatePage() {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { domain: 'Education' },
  })

  const mutation = useMutation({
    mutationFn: api.createDebate,
    onSuccess: (data) => navigate(`/debates/${data.id}`),
  })

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardTitle className="text-2xl mb-2">Create New Debate</CardTitle>
        <CardDescription>Submit a question to begin building a persistent argument structure.</CardDescription>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="mt-6 space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">Question</label>
            <textarea
              {...register('question')}
              rows={3}
              placeholder="Should generative AI be used in university education?"
              className="w-full bg-surface-secondary border border-primary/20 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 resize-none"
            />
            {errors.question && <p className="text-danger text-xs mt-1">{errors.question.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Domain</label>
            <select
              {...register('domain')}
              className="w-full bg-surface-secondary border border-primary/20 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50"
            >
              {domains.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Description (optional)</label>
            <textarea
              {...register('description')}
              rows={2}
              className="w-full bg-surface-secondary border border-primary/20 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 resize-none"
            />
          </div>

          {mutation.isError && (
            <p className="text-danger text-sm">{(mutation.error as Error).message}</p>
          )}

          <Button type="submit" size="lg" disabled={mutation.isPending} className="w-full">
            {mutation.isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating...</> : 'Start Debate'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
