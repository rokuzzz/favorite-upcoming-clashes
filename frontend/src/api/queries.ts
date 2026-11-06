// React hooks for server data. TanStack Query handles caching, loading/error state and out-of-order responses.
import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { api } from './client'
import type { Horizon } from './types'

export function useTeams() {
  return useQuery({
    queryKey: ['teams'],
    queryFn: api.getTeams,
    staleTime: 60 * 60 * 1000, // the team list practically never changes during a session
  })
}

export function useMatches(teamId: string | null, days: Horizon) {
  return useQuery({
    queryKey: ['matches', teamId, days],
    queryFn: () => api.getMatches(teamId!, days),
    enabled: teamId !== null, // nothing to load until a team is chosen
    placeholderData: keepPreviousData, // keep showing the old list while the new one loads
  })
}
