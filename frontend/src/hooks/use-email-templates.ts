import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type { EmailTemplate, PaginatedResponse } from '@/lib/types'

interface EmailTemplatesParams {
  page?: number
  page_size?: number
  is_active?: boolean
}

export function useEmailTemplates(params: EmailTemplatesParams = {}) {
  return useQuery({
    queryKey: ['email-templates', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<EmailTemplate>>('/email-templates', {
        params,
      })
      return response.data
    },
  })
}

export function useEmailTemplate(id: number | null) {
  return useQuery({
    queryKey: ['email-template', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<EmailTemplate>(`/email-templates/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

interface EmailPreviewRequest {
  template_id: number
  contact_id: number
}

interface EmailPreviewResponse {
  subject: string
  body: string
  to_email: string
  to_name: string
}

export function useEmailPreview() {
  return useMutation({
    mutationFn: async (data: EmailPreviewRequest) => {
      const response = await api.post<EmailPreviewResponse>('/email-templates/preview', data)
      return response.data
    },
  })
}

interface EmailSendRequest {
  template_id: number
  contact_id: number
  subject_override?: string
}

export function useSendEmail() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: EmailSendRequest) => {
      const response = await api.post('/email-templates/send', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contact-history'] })
    },
  })
}
