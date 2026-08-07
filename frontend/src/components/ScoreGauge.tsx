export function scoreColor(score: number): string {
  if (score < 40) return '#ef4444'
  if (score < 70) return '#f59e0b'
  return '#22c55e'
}

export function scoreLabel(score: number): string {
  if (score < 40) return 'Riesgo alto'
  if (score < 70) return 'Necesita atención'
  return 'Saludable'
}

export function ScoreGauge({ score }: { score: number }) {
  const color = scoreColor(score)
  return (
    <div
      className="score-gauge"
      role="img"
      aria-label={`Salud ${score} de 100, ${scoreLabel(score)}`}
      style={{ background: `conic-gradient(${color} ${score}%, #334155 0)` }}
    >
      <div className="score-gauge__inner">
        <span className="score-gauge__value" style={{ color }}>
          {score}
        </span>
        <span className="score-gauge__label">{scoreLabel(score)}</span>
      </div>
    </div>
  )
}
