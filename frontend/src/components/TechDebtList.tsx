import type { StaticEntry } from '../types'

function shortPath(path: string): string {
  const parts = path.split('/')
  return parts.length > 2 ? parts.slice(-2).join('/') : path
}

export function TechDebtList({ files }: { files: StaticEntry[] }) {
  return (
    <table className="debt-table">
      <thead>
        <tr>
          <th>Archivo</th>
          <th>Líneas</th>
          <th>Complejidad</th>
          <th>TODO</th>
          <th>FIXME</th>
        </tr>
      </thead>
      <tbody>
        {files.map((f) => (
          <tr key={f.path}>
            <td title={f.path}>{shortPath(f.path)}</td>
            <td>{f.lines}</td>
            <td>{f.complexity}</td>
            <td>{f.todos > 0 ? f.todos : '—'}</td>
            <td>{f.fixmes > 0 ? f.fixmes : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
