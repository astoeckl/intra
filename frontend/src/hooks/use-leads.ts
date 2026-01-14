import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Lead,
  LeadListItem,
  LeadCreate,
  LeadStatus,
  LeadImportResult,
} from '@/lib/types'

interface PaginatedLeadResponse {
  items: LeadListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface LeadsParams {
  page?: number
  page_size?: number
  status?: LeadStatus
  campaign_id?: number
}

export function useLeads(params: LeadsParams = {}) {
  return useQuery({
    queryKey: ['leads', params],
    queryFn: async () => {
      const response = await api.get<PaginatedLeadResponse>('/leads', {
        params,
      })
      return response.data
    },
  })
}

export function useLead(id: number | null) {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Lead>(`/leads/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateLead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: LeadCreate) => {
      const response = await api.post<Lead>('/leads', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
    },
  })
}

export function useUpdateLead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<LeadCreate> }) => {
      const response = await api.put<Lead>(`/leads/${id}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
      queryClient.invalidateQueries({ queryKey: ['lead', variables.id] })
    },
  })
}

export function useImportLeads() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ file, campaign_id }: { file: File; campaign_id?: number }) => {
      const formData = new FormData()
      formData.append('file', file)
      
      const params = campaign_id ? `?campaign_id=${campaign_id}` : ''
      const response = await api.post<LeadImportResult>(`/leads/import${params}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
    },
  })
}
