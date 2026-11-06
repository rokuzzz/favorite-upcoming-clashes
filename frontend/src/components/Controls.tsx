import { Star } from 'lucide-react'

import type { Horizon, Team } from '@/api/types'
import { HORIZONS } from '@/api/types'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { cn } from '@/lib/utils'

interface ControlsProps {
  teams: Team[]
  teamId: string | null
  favouriteTeamId: string | null
  horizon: Horizon
  onTeamChange: (teamId: string) => void
  onFavouriteToggle: () => void
  onHorizonChange: (horizon: Horizon) => void
}

// Controlled component: shows the current choice and reports changes; the state lives in the parent.
export function Controls({
  teams,
  teamId,
  favouriteTeamId,
  horizon,
  onTeamChange,
  onFavouriteToggle,
  onHorizonChange,
}: ControlsProps) {
  const isFavourite = teamId !== null && teamId === favouriteTeamId

  return (
    <div className="flex flex-wrap items-end gap-6">
      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium">Team</span>
        <div className="flex items-center gap-2">
          <Select
            items={teams.map((team) => ({ value: team.id, label: team.name }))}
            value={teamId}
            onValueChange={(value) => value && onTeamChange(value)}
          >
            <SelectTrigger className="w-56" aria-label="Team">
              <SelectValue placeholder="Choose a team" />
            </SelectTrigger>
            <SelectContent>
              {teams.map((team) => (
                <SelectItem key={team.id} value={team.id}>
                  {team.logoUrl && <img src={team.logoUrl} alt="" className="size-5 object-contain" />}
                  {team.name}
                  {team.id === favouriteTeamId && <Star className="size-3 fill-current text-primary" />}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="icon"
            disabled={teamId === null}
            aria-pressed={isFavourite}
            aria-label={isFavourite ? 'Remove from favourites' : 'Save as favourite team'}
            title={isFavourite ? 'Remove from favourites' : 'Save as favourite team'}
            onClick={onFavouriteToggle}
          >
            <Star className={cn('size-4', isFavourite && 'fill-current text-primary')} />
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium">Time horizon</span>
        <ToggleGroup
          variant="outline"
          aria-label="Time horizon"
          value={[String(horizon)]}
          onValueChange={(values) => values[0] && onHorizonChange(Number(values[0]) as Horizon)}
        >
          {HORIZONS.map((days) => (
            <ToggleGroupItem key={days} value={String(days)}>
              {days} days
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      </div>
    </div>
  )
}
