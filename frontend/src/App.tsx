import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/layout/Layout'
import { HomePage } from './pages/HomePage'
import { DashboardPage } from './pages/DashboardPage'
import { CreateDebatePage } from './pages/CreateDebatePage'
import { DebateWorkspacePage } from './pages/DebateWorkspacePage'
import { SearchPage } from './pages/SearchPage'
import { AdminPage } from './pages/AdminPage'
import { DatabaseHealthPage } from './pages/DatabaseHealthPage'
import { QueryExplorerPage } from './pages/QueryExplorerPage'
import { ProjectEvidencePage } from './pages/ProjectEvidencePage'
import { DebatesListPage } from './pages/DebatesListPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/debates/new" element={<CreateDebatePage />} />
            <Route path="/debates" element={<DebatesListPage />} />
            <Route path="/debates/:id" element={<DebateWorkspacePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/database-health" element={<DatabaseHealthPage />} />
            <Route path="/query-explorer" element={<QueryExplorerPage />} />
            <Route path="/projects/evidence" element={<ProjectEvidencePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
