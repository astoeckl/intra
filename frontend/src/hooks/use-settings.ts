import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Setting,
  SettingCreate,
  SettingUpdate,
  LookupValue,
  LookupValueCreate,
  LookupValueUpdate,
} from '@/lib/types'

// ============ Settings Hooks ============

export function useSettings(category?: string) {
  return useQuery({
    queryKey: ['settings', { category }],
    queryFn: async () => {
      const response = await api.get<Setting[]>('/settings', {
        params: category ? { category } : undefined,
      })
      return response.data
    },
  })
}

export function useSetting(key: string) {
  return useQuery({
    queryKey: ['setting', key],
    queryFn: async () => {
      const response = await api.get<Setting>(`/settings/${key}`)
      return response.data
    },
    enabled: !!key,
  })
}

export function useCreateSetting() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: SettingCreate) => {
      const response = await api.post<Setting>('/settings', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })
}

export function useUpdateSetting() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ key, data }: { key: string; data: SettingUpdate }) => {
      const response = await api.put<Setting>(`/settings/${key}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      queryClient.invalidateQueries({ queryKey: ['setting', variables.key] })
    },
  })
}

export function useDeleteSetting() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (key: string) => {
      await api.delete(`/settings/${key}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })
}

// ============ Lookup Values Hooks ============

export function useLookupCategories() {
  return useQuery({
    queryKey: ['lookup-categories'],
    queryFn: async () => {
      const response = await api.get<string[]>('/settings/lookups/categories')
      return response.data
    },
  })
}

export function useLookupValues(category: string, includeInactive = false) {
  return useQuery({
    queryKey: ['lookup-values', category, { includeInactive }],
    queryFn: async () => {
      const response = await api.get<LookupValue[]>(`/settings/lookups/${category}`, {
        params: { include_inactive: includeInactive },
      })
      return response.data
    },
    enabled: !!category,
  })
}

export function useCreateLookupValue() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: LookupValueCreate) => {
      const response = await api.post<LookupValue>('/settings/lookups', data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lookup-values', data.category] })
      queryClient.invalidateQueries({ queryKey: ['lookup-categories'] })
    },
  })
}

export function useUpdateLookupValue() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (params: { id: number; data: LookupValueUpdate; category: string }) => {
      const response = await api.put<LookupValue>(`/settings/lookups/${params.id}`, params.data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['lookup-values', variables.category] })
    },
  })
}

export function useDeleteLookupValue() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (params: { id: number; category: string; hardDelete?: boolean }) => {
      await api.delete(`/settings/lookups/${params.id}`, {
        params: { hard_delete: params.hardDelete ?? false },
      })
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['lookup-values', variables.category] })
    },
  })
}

export function useReorderLookupValues() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (params: { category: string; orderedIds: number[] }) => {
      await api.post(`/settings/lookups/${params.category}/reorder`, params.orderedIds)
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['lookup-values', variables.category] })
    },
  })
}
