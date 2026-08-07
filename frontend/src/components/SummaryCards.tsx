import type { Summary } from '../types'

interface SummaryCardsProps {
  summary: Summary
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  const cards = [
    { label: 'Commits', value: summary.total_commits },
    { label: 'Autores', value: summary.total_authors },
    { label: 'Archivos analizados', value: summary.files_analyzed },
  ]
  return (
    <div className="summary-cards">
      {cards.map((c) => (
        <div className="summary-card" key={c.label}>
          <span className="summary-card__value">{c.value}</span>
          <span className="summary-card__label">{c.label}</span>
        </div>
      ))}
    </div>
  )
}