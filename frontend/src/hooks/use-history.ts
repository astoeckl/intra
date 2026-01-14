import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { ContactHistoryItem, ContactHistoryUpdate, PaginatedResponse } from '@/lib/types'

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

export function useUpdateHistoryEntry() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      historyId,
      contactId,
      data,
    }: {
      historyId: number
      contactId: number
      data: ContactHistoryUpdate
    }) => {
      const response = await api.put<ContactHistoryItem>(
        `/contacts/history/${historyId}`,
        data
      )
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contactHistory', variables.contactId] })
    },
  })
}

export function useDeleteHistoryEntry() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      historyId,
      contactId,
    }: {
      historyId: number
      contactId: number
    }) => {
      await api.delete(`/contacts/history/${historyId}`)
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contactHistory', variables.contactId] })
    },
  })
}
