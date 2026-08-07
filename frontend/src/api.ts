import type { Job, ReportResponse } from './types'
import type { GithubRef } from './urls'

export interface BranchesInfo {
  branches: string[]
  default: string
}

export interface Health {
  status: string
  version: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail ?? `Request failed: ${res.status}`)
  }
  return res.json() as Promise<T>
}

export function fetchHealth(signal?: AbortSignal): Promise<Health> {
  return request<Health>('/api/health', { signal })
}

export function analyzeRepo(url: string, branch: string): Promise<Job> {
  return request<Job>('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, branch }),
  })
}

export async function fetchBranches(ref: GithubRef): Promise<BranchesInfo> {
  return request<BranchesInfo>(
    `/api/repos/${encodeURIComponent(ref.owner)}/${encodeURIComponent(ref.repo)}/branches`,
  )
}

export function fetchJob(jobId: number): Promise<ReportResponse> {
  return request<ReportResponse>(`/api/jobs/${jobId}`)
}