import { HealthBadge } from './components/HealthBadge'
import { Dashboard } from './components/Dashboard'
import './styles.css'

export function App() {
  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-top">
          <div>
            <h1 className="app__title">TechDebt Radar</h1>
            <p className="app__subtitle">
              Salud técnica de repositorios: hotspots, churn, bus factor y cadencia.
            </p>
          </div>
          <HealthBadge />
        </div>
      </header>
      <main className="app__main">
        <Dashboard />
      </main>
    </div>
  )
}