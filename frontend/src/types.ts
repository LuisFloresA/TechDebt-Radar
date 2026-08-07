export interface Hotspot {
  path: string
  changes: number
  added: number
  deleted: number
  commits: number
  authors: number
}

export interface ChurnEntry {
  path: string
  added: number
  deleted: number
  churn: number
}

export interface BusFactorEntry {
  path: string
  authors: number
  changes: number
}

export interface Summary {
  total_commits: number
  total_authors: number
  files_analyzed: number
}

export interface ReportMetrics {
  summary: Summary
  hotspots: Hotspot[]
  churn: ChurnEntry[]
  bus_factor: BusFactorEntry[]
  cadence: Record<string, number>
}

export interface Job {
  id: number
  url: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  progress: number
  error?: string | null
  created_at: string
  updated_at: string
}

export interface ReportResponse {
  job: Job
  report: { metrics: ReportMetrics } | null
}