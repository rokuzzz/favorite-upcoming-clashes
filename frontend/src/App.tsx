import { useState } from 'react'

import { useMatches } from '@/features/matches/queries'
import { usePreferences, useSavePreferences } from '@/features/preferences/queries'
import { useTeams } from '@/features/teams/queries'
import type { Horizon } from '@/api/types'
import { Controls, ControlsSkeleton } from '@/features/matches/Controls'
import { MatchCard, MatchCardSkeleton } from '@/features/matches/MatchCard'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

export default function App() {
  const [chosenTeamId, setChosenTeamId] = useState<string | null>(null)
  const [horizon, setHorizon] = useState<Horizon>(14)
  const teams = useTeams()
  const preferences = usePreferences()
  const savePreferences = useSavePreferences()

  const favouriteTeamId = preferences.data?.favouriteTeamId ?? null
  // Until the user picks a team, show the saved favourite.
  const teamId = chosenTeamId ?? favouriteTeamId
  const matches = useMatches(teamId, horizon)

  const toggleFavourite = () => savePreferences.mutate({ favouriteTeamId: teamId === favouriteTeamId ? null : teamId })

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

      {savePreferences.error && (
        <Alert variant="destructive">
          <AlertTitle>Could not save the favourite team</AlertTitle>
          <AlertDescription>{savePreferences.error.message}</AlertDescription>
        </Alert>
      )}

      {teams.isPending || preferences.isPending ? (
        <ControlsSkeleton />
      ) : (
        teams.data && (
          <Controls
            teams={teams.data}
            teamId={teamId}
            favouriteTeamId={favouriteTeamId}
            horizon={horizon}
            onTeamChange={setChosenTeamId}
            onFavouriteToggle={toggleFavourite}
            onHorizonChange={setHorizon}
          />
        )
      )}

      {/* Wait for the saved favourite before asking the user to choose. */}
      {!preferences.isPending && teamId === null && (
        <p className="text-muted-foreground">Choose a team to see its upcoming games.</p>
      )}

      {matches.error && (
        <Alert variant="destructive">
          <AlertTitle>Could not load matches</AlertTitle>
          <AlertDescription>{matches.error.message}</AlertDescription>
        </Alert>
      )}

      {teamId !== null && matches.isPending && (
        <section className="flex flex-col gap-4" aria-busy>
          <Skeleton className="h-7 w-80" />
          <div className="grid gap-4 md:grid-cols-2">
            {[0, 1, 2, 3].map((i) => (
              <MatchCardSkeleton key={i} />
            ))}
          </div>
        </section>
      )}

      {matches.data && (
        // While another team or horizon loads, the previous list stays visible but dimmed.
        <section className={cn('flex flex-col gap-4 transition-opacity', matches.isPlaceholderData && 'opacity-50')}>
          <h2 className="text-xl font-semibold">
            {matches.data.team.name}: {matches.data.matches.length} game
            {matches.data.matches.length === 1 ? '' : 's'} in the next {matches.data.horizonDays} days
          </h2>
          {matches.data.matches.length === 0 ? (
            <p className="text-muted-foreground">No games in this period. Try a longer time horizon.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {matches.data.matches.map((match) => (
                <MatchCard key={match.id} match={match} />
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  )
}
