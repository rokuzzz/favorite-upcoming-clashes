// React hooks for server data. TanStack Query handles caching, loading/error state and out-of-order responses.
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from './client'
import type { Horizon, Preferences } from './types'

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

export function usePreferences() {
  return useQuery({ queryKey: ['preferences'], queryFn: api.getPreferences, staleTime: Infinity })
}

export function useSavePreferences() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: api.savePreferences,
    // Show the change immediately; the server answer replaces it, and a failure restores the old value.
    onMutate: async (preferences: Preferences) => {
      await queryClient.cancelQueries({ queryKey: ['preferences'] })
      const previous = queryClient.getQueryData<Preferences>(['preferences'])
      queryClient.setQueryData(['preferences'], preferences)
      return { previous }
    },
    onError: (_error, _preferences, context) => queryClient.setQueryData(['preferences'], context?.previous),
    onSuccess: (saved) => queryClient.setQueryData(['preferences'], saved),
  })
}
