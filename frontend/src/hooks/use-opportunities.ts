import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Opportunity,
  OpportunityListItem,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunityCreateFromLead,
  OpportunityClose,
  OpportunityStage,
  PipelineStats,
  PaginatedResponse,
} from '@/lib/types'

interface OpportunitiesParams {
  page?: number
  page_size?: number
  stage?: OpportunityStage
  company_id?: number
  contact_id?: number
}

export function useOpportunities(params: OpportunitiesParams = {}) {
  return useQuery({
    queryKey: ['opportunities', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<OpportunityListItem>>('/opportunities', {
        params,
      })
      return response.data
    },
  })
}

export function useOpportunity(id: number | null) {
  return useQuery({
    queryKey: ['opportunity', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Opportunity>('/opportunities/' + id)
      return response.data
    },
    enabled: !!id,
  })
}

export function usePipelineStats() {
  return useQuery({
    queryKey: ['pipeline-stats'],
    queryFn: async () => {
      const response = await api.get<PipelineStats>('/opportunities/stats')
      return response.data
    },
  })
}

export function useCreateOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: OpportunityCreate) => {
      const response = await api.post<Opportunity>('/opportunities', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['pipeline-stats'] })
    },
  })
}

export function useUpdateOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: OpportunityUpdate }) => {
      const response = await api.put<Opportunity>('/opportunities/' + id, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['opportunity', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['pipeline-stats'] })
    },
  })
}

export function useDeleteOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete('/opportunities/' + id)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['pipeline-stats'] })
    },
  })
}

export function useConvertLeadToOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ leadId, data }: { leadId: number; data: OpportunityCreateFromLead }) => {
      const response = await api.post<Opportunity>('/opportunities/convert/' + leadId, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['leads'] })
      queryClient.invalidateQueries({ queryKey: ['pipeline-stats'] })
    },
  })
}

export function useCloseOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: OpportunityClose }) => {
      const response = await api.post<Opportunity>('/opportunities/' + id + '/close', data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['opportunity', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['pipeline-stats'] })
    },
  })
}