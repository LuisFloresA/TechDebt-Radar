import seed from './seed.json'
import type { ReportMetrics } from '../types'

export const DEMO_URL = 'https://github.com/expressjs/express'

export function getDemoMetrics(): ReportMetrics {
  return seed as ReportMetrics
}