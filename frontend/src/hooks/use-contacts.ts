import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Contact,
  ContactListItem,
  ContactCreate,
  ContactSearchResult,
  PaginatedResponse,
} from '@/lib/types'

interface ContactsParams {
  page?: number
  page_size?: number
  search?: string
  company_id?: number
  is_active?: boolean
}

export function useContacts(params: ContactsParams = {}) {
  return useQuery({
    queryKey: ['contacts', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<ContactListItem>>('/contacts', {
        params,
      })
      return response.data
    },
  })
}

interface InfiniteContactsParams {
  search?: string
  company_id?: number
  is_active?: boolean
  page_size?: number
}

export function useInfiniteContacts(params: InfiniteContactsParams = {}) {
  const { page_size = 20, ...filterParams } = params
  
  return useInfiniteQuery({
    queryKey: ['contacts', 'infinite', filterParams],
    queryFn: async ({ pageParam = 1 }) => {
      const response = await api.get<PaginatedResponse<ContactListItem>>('/contacts', {
        params: {
          page: pageParam,
          page_size,
          ...filterParams,
        },
      })
      return response.data
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1
      }
      return undefined
    },
  })
}

export function useContact(id: number | null) {
  return useQuery({
    queryKey: ['contact', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Contact>(`/contacts/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useContactSearch(query: string) {
  return useQuery({
    queryKey: ['contacts', 'search', query],
    queryFn: async () => {
      if (!query || query.length < 2) return []
      const response = await api.get<ContactSearchResult[]>('/contacts/search', {
        params: { q: query, limit: 10 },
      })
      return response.data
    },
    enabled: query.length >= 2,
    staleTime: 30000, // 30 seconds
  })
}

export function useCreateContact() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ContactCreate) => {
      const response = await api.post<Contact>('/contacts', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
    },
  })
}

export function useUpdateContact() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ContactCreate> }) => {
      const response = await api.put<Contact>(`/contacts/${id}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
      queryClient.invalidateQueries({ queryKey: ['contact', variables.id] })
    },
  })
}

export function useDeleteContact() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/contacts/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] })
    },
  })
}
