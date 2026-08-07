import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ScoreGauge } from './ScoreGauge'
import { TechDebtList } from './TechDebtList'
import { RecommendationsList } from './Recommendations'
import type { StaticEntry, Recommendation } from '../types'

describe('ScoreGauge', () => {
  it('muestra el valor y la etiqueta', () => {
    render(<ScoreGauge score={62} />)
    expect(screen.getByText('62')).toBeInTheDocument()
    expect(screen.getByText('Necesita atención')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /62 de 100/ })).toBeInTheDocument()
  })

  it('clasifica valores extremos', () => {
    const { rerender } = render(<ScoreGauge score={20} />)
    expect(screen.getByText('Riesgo alto')).toBeInTheDocument()
    rerender(<ScoreGauge score={85} />)
    expect(screen.getByText('Saludable')).toBeInTheDocument()
  })
})

describe('TechDebtList', () => {
  it('renderiza filas con marcadores', () => {
    const files: StaticEntry[] = [
      { path: 'lib/http.js', lines: 900, todos: 3, fixmes: 1, complexity: 42 },
    ]
    render(<TechDebtList files={files} />)
    expect(screen.getByText('lib/http.js')).toBeInTheDocument()
    expect(screen.getByText('900')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })
})

describe('RecommendationsList', () => {
  it('muestra aviso si no hay recomendaciones', () => {
    render(<RecommendationsList recommendations={[]} />)
    expect(screen.getByText('Sin recomendaciones pendientes.')).toBeInTheDocument()
  })

  it('renderiza recomendaciones ordenadas por severidad', () => {
    const recs: Recommendation[] = [
      { severity: 'high', title: 'Hotspot', detail: 'Un autor' },
      { severity: 'low', title: 'Duplicados', detail: 'Extraer lógica' },
    ]
    render(<RecommendationsList recommendations={recs} />)
    expect(screen.getByText('Hotspot')).toBeInTheDocument()
    expect(screen.getByText('Duplicados')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })
})
