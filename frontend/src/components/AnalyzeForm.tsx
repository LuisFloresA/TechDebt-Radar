import { useEffect, useState, type FormEvent } from 'react'
import { analyzeRepo, fetchBranches } from '../api'
import { DEMO_URL } from '../demo/demo'
import type { Job } from '../types'
import {
  ALL_BRANCHES,
  FALLBACK_OPTIONS,
  branchOptions,
  defaultBranch,
  parseGithubUrl,
  type BranchOption,
} from '../urls'

interface AnalyzeFormProps {
  onStart: (job: Job) => void
  onDemo: () => void
  disabled?: boolean
}

const DEBOUNCE_MS = 400

export function AnalyzeForm({ onStart, onDemo, disabled }: AnalyzeFormProps) {
  const [url, setUrl] = useState('')
  const [branch, setBranch] = useState(ALL_BRANCHES)
  const [options, setOptions] = useState<BranchOption[]>(FALLBACK_OPTIONS)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [loadingBranches, setLoadingBranches] = useState(false)

  useEffect(() => {
    setError(null)
    const ref = parseGithubUrl(url.trim())
    if (!ref) {
      setOptions(FALLBACK_OPTIONS)
      setBranch(ALL_BRANCHES)
      return
    }
    setLoadingBranches(true)
    const timer = setTimeout(async () => {
      try {
        const info = await fetchBranches(ref)
        const list = Array.isArray(info.branches) ? info.branches : []
        setOptions(branchOptions(list))
        if (info.default && list.includes(info.default)) {
          setBranch(info.default)
        } else {
          setBranch(defaultBranch(list))
        }
      } catch {
        setOptions(FALLBACK_OPTIONS)
        setBranch(ALL_BRANCHES)
      } finally {
        setLoadingBranches(false)
      }
    }, DEBOUNCE_MS)
    return () => {
      clearTimeout(timer)
      setLoadingBranches(false)
    }
  }, [url])

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
      const job = await analyzeRepo(trimmed, branch)
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
        <label className="analyze-form__branch">
          <span className="analyze-form__branch-label">Rama</span>
          <select
            className="analyze-form__select"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            disabled={disabled || submitting}
            aria-label="Rama a analizar"
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </label>
        <button className="btn btn--primary" type="submit" disabled={disabled || submitting}>
          {submitting ? 'Enviando…' : 'Analizar'}
        </button>
        <button className="btn btn--ghost" type="button" onClick={onDemo} disabled={disabled}>
          Ver demo
        </button>
      </div>
      {loadingBranches && <p className="analyze-form__hint">Cargando ramas…</p>}
      {branch === ALL_BRANCHES && !loadingBranches && (
        <p className="analyze-form__hint">
          Incluye todas las ramas; el análisis puede tardar más.
        </p>
      )}
      {error && <p className="analyze-form__error" role="alert">{error}</p>}
      {!url && (
        <p className="analyze-form__hint">
          Ejemplo: {DEMO_URL}
        </p>
      )}
    </form>
  )
}