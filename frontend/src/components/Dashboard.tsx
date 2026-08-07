import '../charts'
import { useAnalysis } from '../useAnalysis'
import type { Job } from '../types'
import { getDemoMetrics } from '../demo/demo'
import { AnalyzeForm } from './AnalyzeForm'
import { SummaryCards } from './SummaryCards'
import { BusFactorChart, CadenceChart, ChurnChart, HotspotsChart } from './charts'

export function Dashboard() {
  const { metrics, job, error, loading, start, setMetrics, reset } = useAnalysis()

  function handleStart(job: Job) {
    reset()
    start(job)
  }

  function handleDemo() {
    reset()
    setMetrics(getDemoMetrics())
  }

  return (
    <div className="dashboard">
      <AnalyzeForm onStart={handleStart} onDemo={handleDemo} disabled={!!job && loading} />

      {error && <p className="dashboard__error" role="alert">Error: {error}</p>}

      {job && !metrics && !error && (
        <p className="dashboard__status" role="status">
          Analizando <code>{job.url}</code>… {job.progress}%
        </p>
      )}

      {metrics && (
        <>
          <SummaryCards summary={metrics.summary} />
          <div className="grid">
            <section className="widget">
              <h2 className="widget__title">Hotspots — cambios</h2>
              <HotspotsChart hotspots={metrics.hotspots} />
            </section>
            <section className="widget">
              <h2 className="widget__title">Churn por archivo</h2>
              <ChurnChart churn={metrics.churn} />
            </section>
            <section className="widget">
              <h2 className="widget__title">Bus factor — autores por archivo</h2>
              <p className="widget__hint">
                Rojo = 1 autor (alto riesgo) · Ámbar = 2 · Verde = 3+.
              </p>
              <BusFactorChart entries={metrics.bus_factor} />
            </section>
            <section className="widget">
              <h2 className="widget__title">Cadencia de commits</h2>
              <CadenceChart cadence={metrics.cadence} />
            </section>
          </div>
        </>
      )}
    </div>
  )
}