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

export interface StaticEntry {
  path: string
  lines: number
  todos: number
  fixmes: number
  complexity: number
}

export interface StaticMetrics {
  files: StaticEntry[]
  total_todos: number
  total_fixmes: number
  total_lines: number
  large_files: number
  duplicate_units: number
}

export interface ScoreComponents {
  bus_factor: number
  hotspots: number
  churn: number
  tech_debt: number
  cadence: number
}

export interface Score {
  score: number
  components: ScoreComponents
}

export interface Recommendation {
  severity: 'high' | 'medium' | 'low'
  title: string
  detail: string
}

export interface ReportMetrics {
  summary: Summary
  hotspots: Hotspot[]
  churn: ChurnEntry[]
  bus_factor: BusFactorEntry[]
  cadence: Record<string, number>
  static: StaticMetrics
  score: Score
  recommendations: Recommendation[]
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