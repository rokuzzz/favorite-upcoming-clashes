import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { api } from '@/api/client'
import type { Horizon } from '@/api/types'

/** `include` lists the optional data sources to load with each match, e.g. ['weather']. */
export function useMatches(teamId: string | null, days: Horizon, include: string[] = []) {
  return useQuery({
    queryKey: ['matches', teamId, days, include],
    queryFn: () => api.getMatches(teamId!, days, include),
    enabled: teamId !== null, // nothing to load until a team is chosen
    placeholderData: keepPreviousData, // keep showing the old list while the new one loads
  })
}
