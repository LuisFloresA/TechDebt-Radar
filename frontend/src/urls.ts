export interface GithubRef {
  owner: string
  repo: string
}

export interface BranchOption {
  value: string
  label: string
}

export const ALL_BRANCHES = 'all'

/** Extrae {owner, repo} de una URL de GitHub, o null si no es válida. */
export function parseGithubUrl(url: string): GithubRef | null {
  try {
    const u = new URL(url)
    if (u.protocol !== 'https:' || !/^(www\.)?github\.com$/.test(u.hostname)) {
      return null
    }
    const parts = u.pathname.split('/').filter(Boolean)
    if (parts.length < 2 || !parts[0] || !parts[1]) return null
    return {
      owner: parts[0],
      repo: parts[1].replace(/\.git$/, ''),
    }
  } catch {
    return null
  }
}

/** Ordena opciones: "all" primero, luego "main", después el resto alfabético. */
export function branchOptions(branches: string[]): BranchOption[] {
  const rest = branches.filter((b) => b !== ALL_BRANCHES && b !== 'main').sort()
  return [
    { value: ALL_BRANCHES, label: 'Todas las ramas' },
    ...(branches.includes('main') ? [{ value: 'main', label: 'main' }] : []),
    ...rest.map((b) => ({ value: b, label: b })),
  ] as BranchOption[]
}

/** Rama por defecto: "main" si existe, si no "all". */
export function defaultBranch(branches: string[]): string {
  return branches.includes('main') ? 'main' : ALL_BRANCHES
}

export const FALLBACK_OPTIONS: BranchOption[] = [
  { value: ALL_BRANCHES, label: 'Todas las ramas' },
]