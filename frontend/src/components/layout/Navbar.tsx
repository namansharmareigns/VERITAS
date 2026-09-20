import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Search, Database, FileText, Home, Scale } from 'lucide-react'
import { cn } from '../../lib/utils'

const links = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/debates', label: 'Debates', icon: Scale },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/admin', label: 'Analytics', icon: Database },
  { to: '/projects/evidence', label: 'Evidence', icon: FileText },
]

export function Navbar() {
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 glass border-b border-primary/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <Scale className="w-5 h-5 text-primary" />
            </div>
            <span className="font-bold text-lg gradient-text">VERITAS</span>
          </Link>
          <div className="hidden md:flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors',
                  location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
                    ? 'bg-primary/15 text-primary'
                    : 'text-muted hover:text-text hover:bg-surface-secondary'
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
