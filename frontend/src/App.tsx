import { useState } from 'react'

import { useTeams } from '@/api/queries'
import type { Horizon } from '@/api/types'
import { Controls } from '@/components/Controls'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'

export default function App() {
  const [teamId, setTeamId] = useState<string | null>(null)
  const [horizon, setHorizon] = useState<Horizon>(14)
  const teams = useTeams()

  const selectedTeam = teams.data?.find((team) => team.id === teamId)

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 p-6">
      <header>
        <h1 className="text-3xl font-bold">Favorite Upcoming Clashes</h1>
        <p className="text-muted-foreground">Upcoming Liiga games of your favourite team.</p>
      </header>

      {teams.error && (
        <Alert variant="destructive">
          <AlertTitle>Could not load teams</AlertTitle>
          <AlertDescription>{teams.error.message}</AlertDescription>
        </Alert>
      )}

      {teams.isPending ? (
        <Skeleton className="h-16 w-96" />
      ) : (
        teams.data && (
          <Controls
            teams={teams.data}
            teamId={teamId}
            horizon={horizon}
            onTeamChange={setTeamId}
            onHorizonChange={setHorizon}
          />
        )
      )}

      <p className="text-muted-foreground">
        {selectedTeam
          ? `Selected: ${selectedTeam.name}, next ${horizon} days`
          : 'Choose your favourite team to see its upcoming games.'}
      </p>
    </main>
  )
}
