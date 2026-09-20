import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'

export function Layout() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.health,
    refetchInterval: 30000,
  })

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      {health?.demo_mode && (
        <div className="bg-warning/10 border-b border-warning/20 text-warning text-center text-xs py-1.5">
          Demo Mode — Development fixtures may be displayed. Not experimental evidence.
        </div>
      )}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
