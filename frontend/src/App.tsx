import { useEffect, useState } from 'react'

import { Badge } from '@/components/ui/badge'

export default function App() {
  const [status, setStatus] = useState('checking…')

  useEffect(() => {
    fetch('/api/health')
      .then((response) => response.json())
      .then((data: { status: string }) => setStatus(data.status))
      .catch(() => setStatus('backend not reachable'))
  }, [])

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-2 p-6">
      <h1 className="text-3xl font-bold">Favorite Upcoming Clashes</h1>
      <p className="flex items-center gap-2 text-muted-foreground">
        Backend status:
        <Badge variant={status === 'ok' ? 'default' : 'destructive'}>{status}</Badge>
      </p>
    </main>
  )
}
