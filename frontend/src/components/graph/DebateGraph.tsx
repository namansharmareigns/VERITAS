import { useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from 'reactflow'
import type { Node, Edge } from 'reactflow'
import 'reactflow/dist/style.css'
import type { GraphNode, GraphEdge } from '../../types'

interface DebateGraphProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const nodeColors: Record<string, string> = {
  question: '#67D9FF',
  PRO_claim: '#67D9FF',
  CON_claim: '#FF6B7A',
  evidence: '#8EA5B5',
  counterargument: '#FFD166',
}

export function DebateGraph({ nodes, edges }: DebateGraphProps) {
  const flowNodes: Node[] = useMemo(() => {
    const center = { x: 400, y: 200 }
    return nodes.map((n, i) => {
      let x = center.x
      let y = center.y
      if (n.type === 'question') {
        x = center.x; y = center.y
      } else if (n.type === 'PRO_claim') {
        x = 150; y = 100 + (i % 4) * 80
      } else if (n.type === 'CON_claim') {
        x = 650; y = 100 + (i % 4) * 80
      } else if (n.type === 'evidence') {
        x = 300 + (i % 3) * 100; y = 350 + (i % 2) * 60
      } else {
        x = 500 + (i % 3) * 80; y = 400 + (i % 2) * 50
      }
      return {
        id: n.id,
        data: { label: n.label },
        position: { x, y },
        style: {
          background: nodeColors[n.type] || '#111C27',
          color: n.type === 'evidence' ? '#060A10' : '#F2FAFF',
          border: '1px solid rgba(103,217,255,0.3)',
          borderRadius: 8,
          padding: 8,
          fontSize: 11,
          maxWidth: 160,
        },
      }
    })
  }, [nodes])

  const flowEdges: Edge[] = useMemo(() =>
    edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.type,
      animated: e.type === 'CONTRADICTS',
      style: {
        stroke: e.type === 'CONTRADICTS' ? '#FF6B7A' : e.type === 'SUPPORTS' ? '#70E0A4' : '#8EA5B5',
      },
      markerEnd: { type: MarkerType.ArrowClosed },
    })),
  [edges])

  const onInit = useCallback(() => {}, [])

  if (nodes.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-muted text-sm">
        No graph data. Run analysis to generate debate structure.
      </div>
    )
  }

  return (
    <div className="h-96 rounded-xl overflow-hidden border border-primary/10">
      <ReactFlow nodes={flowNodes} edges={flowEdges} onInit={onInit} fitView>
        <Background color="#1a2535" gap={20} />
        <Controls />
        <MiniMap nodeColor={(n) => (n.style?.background as string) || '#111C27'} />
      </ReactFlow>
    </div>
  )
}
