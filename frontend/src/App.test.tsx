import { describe, expect, it, vi } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { App } from './App'

describe('App', () => {
  it('pinta el título de la app', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network')))
    render(<App />)
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByRole('heading', { name: /TechDebt Radar/i })).toBeInTheDocument()
    vi.unstubAllGlobals()
  })

  it('muestra el badge y cambia a ok cuando la API responde', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok', version: '0.1.0' }),
      }),
    )
    render(<App />)
    const badge = screen.getByRole('status')
    expect(badge).toBeInTheDocument()
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByText('API ok')).toBeInTheDocument()
    vi.unstubAllGlobals()
  })

  it('muestra API down cuando falla la petición', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('network')),
    )
    render(<App />)
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByText('API down')).toBeInTheDocument()
    vi.unstubAllGlobals()
  })
})