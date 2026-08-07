import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Dashboard } from './Dashboard'

vi.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="chart-bar" />,
  Line: () => <div data-testid="chart-line" />,
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('muestra el resumen y los widgets al cargar el demo', () => {
    render(<Dashboard />)
    fireEvent.click(screen.getByRole('button', { name: 'Ver demo' }))

    expect(screen.getByText('Commits')).toBeInTheDocument()
    expect(screen.getByText('Autores')).toBeInTheDocument()
    expect(screen.getByText('Hotspots — cambios')).toBeInTheDocument()
    expect(screen.getByText('Churn por archivo')).toBeInTheDocument()
    expect(screen.getByText('Bus factor — autores por archivo')).toBeInTheDocument()
    expect(screen.getByText('Cadencia de commits')).toBeInTheDocument()
    expect(screen.getAllByTestId('chart-bar').length).toBeGreaterThanOrEqual(3)
    expect(screen.getAllByTestId('chart-line').length).toBe(1)
  })

  it('envía el análisis al pulsar Analizar y muestra estado', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ id: 42, url: 'https://github.com/o/r', status: 'queued', progress: 5 }),
      }),
    )
    render(<Dashboard />)
    const input = screen.getByLabelText('URL del repositorio')
    fireEvent.change(input, { target: { value: 'https://github.com/octocat/Hello-World' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analizar' }))

    await waitFor(() => {
      expect(screen.getByText(/Analizando/)).toBeInTheDocument()
    })
    vi.unstubAllGlobals()
  })

  it('muestra error si la URL no es válida', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'Solo se admiten URLs de github.com' }),
    }))
    render(<Dashboard />)
    const input = screen.getByLabelText('URL del repositorio')
    fireEvent.change(input, { target: { value: 'http://gitlab.com/x' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analizar' }))

    await waitFor(() => {
      expect(screen.getByText('Solo se admiten URLs de github.com')).toBeInTheDocument()
    })
    vi.unstubAllGlobals()
  })
})