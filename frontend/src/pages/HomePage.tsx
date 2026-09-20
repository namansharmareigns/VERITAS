import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardDescription, CardTitle } from '../components/ui/card'
import { ArrowRight, Database, GitBranch, Clock, Shield } from 'lucide-react'

const capabilities = [
  { icon: Database, title: 'Evidence-Aware Storage', desc: 'Persistent argument structures with provenance and scoring.' },
  { icon: GitBranch, title: 'Debate Graph', desc: 'Visualize claims, evidence, and contradictions as a knowledge graph.' },
  { icon: Clock, title: 'Temporal Evolution', desc: 'Track how positions and confidence change over time.' },
  { icon: Shield, title: 'Explainable Scoring', desc: 'Transparent evidence-weighted synthesis with uncertainty.' },
]

export function HomePage() {
  return (
    <div className="space-y-16">
      <section className="text-center py-12">
        <p className="text-primary text-sm font-medium tracking-wider uppercase mb-4">Research Platform</p>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
          <span className="gradient-text">VERITAS</span>
        </h1>
        <p className="text-xl text-muted max-w-2xl mx-auto mb-2">
          An Evidence-Aware, Temporal and Explainable Database for Evolving AI Debates
        </p>
        <p className="text-lg text-primary-light/80 max-w-xl mx-auto mb-8">
          Turn a debate into a living knowledge object.
        </p>
        <p className="text-muted max-w-2xl mx-auto mb-10">
          From answering questions to understanding how positions evolve.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/debates/new">
            <Button size="lg">Start a Debate <ArrowRight className="w-4 h-4" /></Button>
          </Link>
          <Link to="/debates">
            <Button variant="outline" size="lg">Explore Debates</Button>
          </Link>
        </div>
      </section>

      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {capabilities.map(({ icon: Icon, title, desc }) => (
          <Card key={title}>
            <Icon className="w-8 h-8 text-primary mb-3" />
            <CardTitle className="text-base">{title}</CardTitle>
            <CardDescription>{desc}</CardDescription>
          </Card>
        ))}
      </section>

      <section className="glass rounded-2xl p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Proposed Framework</h2>
        <p className="text-muted max-w-3xl mx-auto">
          VERITAS represents debates as persistent, evidence-aware knowledge structures rather than
          temporary AI conversations. The proposed scoring framework weights evidence by reliability,
          relevance, independence, and recency — to be evaluated in academic review.
        </p>
      </section>
    </div>
  )
}
