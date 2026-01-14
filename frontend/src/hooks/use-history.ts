import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ContactHistoryItem, PaginatedResponse } from '@/lib/types'

export function useContactHistory(contactId: number | null) {
  return useQuery({
    queryKey: ['contactHistory', contactId],
    queryFn: async () => {
      if (!contactId) return null
      const response = await api.get<PaginatedResponse<ContactHistoryItem>>(
        `/contacts/${contactId}/history`
      )
      return response.data
    },
    enabled: !!contactId,
  })
}

export function useAddNote() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ contactId, content }: { contactId: number; content: string }) => {
      const response = await api.post<ContactHistoryItem>(
        `/contacts/${contactId}/notes`,
        { content }
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contactHistory', variables.contactId] })
    },
  })
}

export function useAddCall() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      contactId,
      content,
      duration_minutes,
      outcome,
    }: {
      contactId: number
      content: string
      duration_minutes?: number
      outcome?: string
    }) => {
      const response = await api.post<ContactHistoryItem>(
        `/contacts/${contactId}/calls`,
        { content, duration_minutes, outcome }
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contactHistory', variables.contactId] })
    },
  })
}
