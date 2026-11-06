import type { Horizon, Team } from '@/api/types'
import { HORIZONS } from '@/api/types'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

interface ControlsProps {
  teams: Team[]
  teamId: string | null
  horizon: Horizon
  onTeamChange: (teamId: string) => void
  onHorizonChange: (horizon: Horizon) => void
}

// Controlled component: shows the current choice and reports changes; the state lives in the parent.
export function Controls({ teams, teamId, horizon, onTeamChange, onHorizonChange }: ControlsProps) {
  return (
    <div className="flex flex-wrap items-end gap-6">
      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium">Favourite team</span>
        <Select
          items={teams.map((team) => ({ value: team.id, label: team.name }))}
          value={teamId}
          onValueChange={(value) => value && onTeamChange(value)}
        >
          <SelectTrigger className="w-56" aria-label="Favourite team">
            <SelectValue placeholder="Choose a team" />
          </SelectTrigger>
          <SelectContent>
            {teams.map((team) => (
              <SelectItem key={team.id} value={team.id}>
                {team.logoUrl && <img src={team.logoUrl} alt="" className="size-5 object-contain" />}
                {team.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
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
