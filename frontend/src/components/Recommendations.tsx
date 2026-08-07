import type { Recommendation } from '../types'

export function RecommendationsList({
  recommendations,
}: {
  recommendations: Recommendation[]
}) {
  if (recommendations.length === 0) {
    return <p className="widget__hint">Sin recomendaciones pendientes.</p>
  }
  return (
    <ul className="recs">
      {recommendations.map((rec) => (
        <li key={rec.title} className={`recs__item recs__item--${rec.severity}`}>
          <span className="recs__badge">{rec.severity}</span>
          <div>
            <p className="recs__title">{rec.title}</p>
            <p className="recs__detail">{rec.detail}</p>
          </div>
        </li>
      ))}
    </ul>
  )
}
