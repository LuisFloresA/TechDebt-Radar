import { useState, type FormEvent } from 'react'
import { analyzeRepo } from '../api'
import { DEMO_URL } from '../demo/demo'
import type { Job } from '../types'

interface AnalyzeFormProps {
  onStart: (job: Job) => void
  onDemo: () => void
  disabled?: boolean
}

export function AnalyzeForm({ onStart, onDemo, disabled }: AnalyzeFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) {
      setError('Introduce una URL de un repositorio de GitHub.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      const job = await analyzeRepo(trimmed)
      onStart(job)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo iniciar el análisis.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="analyze-form" onSubmit={handleSubmit}>
      <div className="analyze-form__row">
        <input
          className="analyze-form__input"
          type="url"
          placeholder="https://github.com/owner/repo"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={disabled || submitting}
          aria-label="URL del repositorio"
        />
        <button className="btn btn--primary" type="submit" disabled={disabled || submitting}>
          {submitting ? 'Enviando…' : 'Analizar'}
        </button>
        <button className="btn btn--ghost" type="button" onClick={onDemo} disabled={disabled}>
          Ver demo
        </button>
      </div>
      {error && <p className="analyze-form__error" role="alert">{error}</p>}
      {!url && (
        <p className="analyze-form__hint">
          Ejemplo: {DEMO_URL}
        </p>
      )}
    </form>
  )
}