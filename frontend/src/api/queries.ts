// React hooks for server data. TanStack Query handles caching, loading/error state and out-of-order responses.
import { useQuery } from '@tanstack/react-query'

import { api } from './client'

export function useTeams() {
  return useQuery({
    queryKey: ['teams'],
    queryFn: api.getTeams,
    staleTime: 60 * 60 * 1000, // the team list practically never changes during a session
  })
}
