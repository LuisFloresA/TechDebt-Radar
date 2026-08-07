import '../charts'
import { useAnalysis } from '../useAnalysis'
import type { Job } from '../types'
import { getDemoMetrics } from '../demo/demo'
import { AnalyzeForm } from './AnalyzeForm'
import { SummaryCards } from './SummaryCards'
import {
  BusFactorChart,
  CadenceChart,
  ChurnChart,
  HotspotsChart,
  RadarChart,
} from './charts'
import { RecommendationsList } from './Recommendations'
import { ScoreGauge } from './ScoreGauge'
import { TechDebtList } from './TechDebtList'

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
            <section className="widget widget--gauge">
              <h2 className="widget__title">Score de salud</h2>
              <ScoreGauge score={metrics.score.score} />
              <p className="widget__hint">
                Promedio ponderado de los 5 componentes del radar.
              </p>
            </section>
            <section className="widget">
              <h2 className="widget__title">Radar de componentes</h2>
              <RadarChart components={metrics.score.components} />
            </section>
          </div>
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
          <div className="grid">
            <section className="widget">
              <h2 className="widget__title">Deuda técnica estática</h2>
              <p className="widget__hint">
                {metrics.static.total_todos} TODO · {metrics.static.total_fixmes}{' '}
                FIXME · {metrics.static.large_files} archivos &gt;500 líneas ·{' '}
                {metrics.static.duplicate_units} duplicados.
              </p>
              <TechDebtList files={metrics.static.files} />
            </section>
            <section className="widget">
              <h2 className="widget__title">Recomendaciones</h2>
              <RecommendationsList recommendations={metrics.recommendations} />
            </section>
          </div>
        </>
      )}
    </div>
  )
}