import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { api } from '@/api/client'
import type { Horizon } from '@/api/types'

export function useMatches(teamId: string | null, days: Horizon) {
  return useQuery({
    queryKey: ['matches', teamId, days],
    queryFn: () => api.getMatches(teamId!, days),
    enabled: teamId !== null, // nothing to load until a team is chosen
    placeholderData: keepPreviousData, // keep showing the old list while the new one loads
  })
}
