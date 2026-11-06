import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/api/client'
import type { Preferences } from '@/api/types'

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
