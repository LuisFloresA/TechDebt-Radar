import { describe, expect, it } from 'vitest'
import {
  ALL_BRANCHES,
  branchOptions,
  defaultBranch,
  parseGithubUrl,
} from './urls'

describe('parseGithubUrl', () => {
  it('extrae owner/repo de una URL válida', () => {
    expect(parseGithubUrl('https://github.com/octocat/Hello-World')).toEqual({
      owner: 'octocat',
      repo: 'Hello-World',
    })
  })

  it('soporta .git y www', () => {
    expect(parseGithubUrl('https://www.github.com/a/b.git')).toEqual({
      owner: 'a',
      repo: 'b',
    })
  })

  it('rechaza hosts o protocolos inválidos', () => {
    expect(parseGithubUrl('http://github.com/a/b')).toBeNull()
    expect(parseGithubUrl('https://gitlab.com/a/b')).toBeNull()
    expect(parseGithubUrl('no es url')).toBeNull()
    expect(parseGithubUrl('https://github.com/solo')).toBeNull()
  })
})

describe('branchOptions', () => {
  it('ordena all, main y luego el resto alfabético', () => {
    const opts = branchOptions(['zeta', 'main', 'alpha', 'docs'])
    expect(opts.map((o) => o.value)).toEqual([ALL_BRANCHES, 'main', 'alpha', 'docs', 'zeta'])
  })

  it('sin main no lo incluye', () => {
    const opts = branchOptions(['dev', 'prod'])
    expect(opts.map((o) => o.value)).toEqual([ALL_BRANCHES, 'dev', 'prod'])
  })
})

describe('defaultBranch', () => {
  it('elige main si existe, si no all', () => {
    expect(defaultBranch(['dev', 'main'])).toBe('main')
    expect(defaultBranch(['dev'])).toBe(ALL_BRANCHES)
  })
})
