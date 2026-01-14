import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { Company, CompanyCreate, PaginatedResponse } from '@/lib/types'

interface CompaniesParams {
  page?: number
  page_size?: number
  search?: string
}

export function useCompanies(params: CompaniesParams = {}) {
  return useQuery({
    queryKey: ['companies', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Company>>('/companies', {
        params,
      })
      return response.data
    },
  })
}

export function useCompany(id: number | null) {
  return useQuery({
    queryKey: ['company', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Company>(`/companies/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateCompany() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CompanyCreate) => {
      const response = await api.post<Company>('/companies', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
  })
}

export function useUpdateCompany() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<CompanyCreate> }) => {
      const response = await api.put<Company>(`/companies/${id}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      queryClient.invalidateQueries({ queryKey: ['company', variables.id] })
    },
  })
}

export function useDeleteCompany() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/companies/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
  })
}
