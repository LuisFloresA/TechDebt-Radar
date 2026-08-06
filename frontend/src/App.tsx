import { HealthBadge } from './components/HealthBadge'
import './styles.css'

export function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">TechDebt Radar</h1>
        <p className="app__subtitle">
          Analítica de salud técnica de repositorios — F0 esqueleto self-host
        </p>
      </header>
      <main className="app__main">
        <HealthBadge />
      </main>
    </div>
  )
}