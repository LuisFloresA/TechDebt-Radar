import { useCallback, useEffect, useState } from 'react'
import { fetchHealth } from '../api'

type State = 'checking' | 'ok' | 'error'

export function HealthBadge() {
  const [state, setState] = useState<State>('checking')

  const check = useCallback(() => {
    let active = true
    setState('checking')
    fetchHealth()
      .then((h) => {
        if (active) setState(h.status === 'ok' ? 'ok' : 'error')
      })
      .catch(() => {
        if (active) setState('error')
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const cleanup = check()
    return cleanup
  }, [check])

  const label = state === 'checking' ? 'Checking…' : state === 'ok' ? 'API ok' : 'API down'

  return (
    <div className={`health-badge health-badge--${state}`} role="status">
      <span className="health-badge__dot" />
      <span>{label}</span>
    </div>
  )
}