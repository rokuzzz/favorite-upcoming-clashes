import { useEffect, useState } from 'react'

export default function App() {
  const [status, setStatus] = useState('checking…')

  useEffect(() => {
    fetch('/api/health')
      .then((response) => response.json())
      .then((data: { status: string }) => setStatus(data.status))
      .catch(() => setStatus('backend not reachable'))
  }, [])

  return (
    <main>
      <h1>Favorite Upcoming Clashes</h1>
      <p>Backend status: {status}</p>
    </main>
  )
}
