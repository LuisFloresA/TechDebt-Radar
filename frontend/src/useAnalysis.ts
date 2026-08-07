import { useEffect, useRef, useState } from 'react'
import { fetchJob } from './api'
import type { Job, ReportMetrics } from './types'

interface UseAnalysis {
  metrics: ReportMetrics | null
  job: Job | null
  error: string | null
  loading: boolean
  start: (job: Job) => void
  setMetrics: (m: ReportMetrics) => void
  reset: () => void
}

const POLL_MS = 1500

export function useAnalysis(): UseAnalysis {
  const [metrics, setMetrics] = useState<ReportMetrics | null>(null)
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  function stop() {
    if (timer.current) {
      clearInterval(timer.current)
      timer.current = null
    }
  }

  function start(job: Job) {
    stop()
    setJob(job)
    setError(null)
    setLoading(true)
    timer.current = setInterval(async () => {
      try {
        const res = await fetchJob(job.id)
        setJob(res.job)
        if (res.job.status === 'succeeded' && res.report) {
          setMetrics(res.report.metrics)
          setLoading(false)
          stop()
        } else if (res.job.status === 'failed') {
          setError(res.job.error ?? 'El análisis falló')
          setLoading(false)
          stop()
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error consultando el job')
        setLoading(false)
        stop()
      }
    }, POLL_MS)
  }

  useEffect(() => stop, [])

  return { metrics, job, error, loading, start, setMetrics, reset: () => { stop(); setMetrics(null); setJob(null); setError(null); setLoading(false) } }
}