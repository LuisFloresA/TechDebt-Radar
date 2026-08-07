import { Bar, Line, Radar } from 'react-chartjs-2'
import type { BusFactorEntry, ChurnEntry, Hotspot, ScoreComponents } from '../types'

const TOP = 10

const AXIS_LABELS: Record<keyof ScoreComponents, string> = {
  bus_factor: 'Bus factor',
  hotspots: 'Hotspots',
  churn: 'Churn',
  tech_debt: 'Deuda técnica',
  cadence: 'Cadencia',
}

export function RadarChart({ components }: { components: ScoreComponents }) {
  return (
    <Radar
      data={{
        labels: Object.keys(AXIS_LABELS).map(
          (k) => AXIS_LABELS[k as keyof ScoreComponents],
        ),
        datasets: [
          {
            label: 'Salud por componente (0-100)',
            data: Object.values(components),
            borderColor: '#22d3ee',
            backgroundColor: 'rgba(34, 211, 238, 0.2)',
            pointBackgroundColor: '#22d3ee',
          },
        ],
      }}
      options={{
        scales: {
          r: {
            min: 0,
            max: 100,
            ticks: { stepSize: 25 },
            grid: { color: 'rgba(148, 163, 184, 0.2)' },
            angleLines: { color: 'rgba(148, 163, 184, 0.2)' },
          },
        },
        plugins: { legend: { display: false } },
        responsive: true,
        maintainAspectRatio: false,
      }}
      height={280}
    />
  )
}

function shortPath(path: string): string {
  const parts = path.split('/')
  return parts.length > 2 ? parts.slice(-2).join('/') : path
}

function riskColor(authors: number): string {
  if (authors <= 1) return '#ef4444'
  if (authors === 2) return '#f59e0b'
  return '#22c55e'
}

export function HotspotsChart({ hotspots }: { hotspots: Hotspot[] }) {
  const top = hotspots.slice(0, TOP).reverse()
  return (
    <Bar
      data={{
        labels: top.map((h) => shortPath(h.path)),
        datasets: [
          {
            label: 'Cambios (líneas)',
            data: top.map((h) => h.changes),
            backgroundColor: '#3b82f6',
          },
        ],
      }}
      options={{
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        responsive: true,
        maintainAspectRatio: false,
      }}
      height={280}
    />
  )
}

export function ChurnChart({ churn }: { churn: ChurnEntry[] }) {
  const top = churn.slice(0, TOP).reverse()
  return (
    <Bar
      data={{
        labels: top.map((c) => shortPath(c.path)),
        datasets: [
          {
            label: 'Añadidas',
            data: top.map((c) => c.added),
            backgroundColor: '#22c55e',
          },
          {
            label: 'Eliminadas',
            data: top.map((c) => c.deleted),
            backgroundColor: '#ef4444',
          },
        ],
      }}
      options={{
        indexAxis: 'y',
        scales: { x: { stacked: false } },
        responsive: true,
        maintainAspectRatio: false,
      }}
      height={280}
    />
  )
}

export function BusFactorChart({ entries }: { entries: BusFactorEntry[] }) {
  const top = entries.slice(0, TOP).reverse()
  return (
    <Bar
      data={{
        labels: top.map((b) => shortPath(b.path)),
        datasets: [
          {
            label: 'Autores por archivo',
            data: top.map((b) => b.authors),
            backgroundColor: top.map((b) => riskColor(b.authors)),
          },
        ],
      }}
      options={{
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { min: 0 } },
        responsive: true,
        maintainAspectRatio: false,
      }}
      height={280}
    />
  )
}

export function CadenceChart({ cadence }: { cadence: Record<string, number> }) {
  const days = Object.keys(cadence).sort()
  return (
    <Line
      data={{
        labels: days,
        datasets: [
          {
            label: 'Commits',
            data: days.map((d) => cadence[d]),
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.15)',
            fill: true,
            tension: 0.3,
          },
        ],
      }}
      options={{
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { maxTicksLimit: 8 } } },
        responsive: true,
        maintainAspectRatio: false,
      }}
      height={280}
    />
  )
}