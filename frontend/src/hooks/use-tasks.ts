import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import type {
  Task,
  TaskListItem,
  TaskCreate,
  TaskStatus,
  PaginatedResponse,
} from '@/lib/types'

interface TasksParams {
  page?: number
  page_size?: number
  status?: TaskStatus
  assigned_to?: string
  contact_id?: number
  is_overdue?: boolean
}

export function useTasks(params: TasksParams = {}) {
  return useQuery({
    queryKey: ['tasks', params],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<TaskListItem>>('/tasks', {
        params,
      })
      return response.data
    },
  })
}

export function useMyTasks(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['tasks', 'my', page, pageSize],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<TaskListItem>>('/tasks/my', {
        params: { page, page_size: pageSize },
      })
      return response.data
    },
  })
}

export function useTask(id: number | null) {
  return useQuery({
    queryKey: ['task', id],
    queryFn: async () => {
      if (!id) return null
      const response = await api.get<Task>(`/tasks/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: TaskCreate) => {
      const response = await api.post<Task>('/tasks', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<TaskCreate> }) => {
      const response = await api.put<Task>(`/tasks/${id}`, data)
      return response.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['task', variables.id] })
    },
  })
}

interface CompleteTaskData {
  notes?: string
  create_follow_up?: boolean
  follow_up_title?: string
  follow_up_due_date?: string
  follow_up_priority?: 'low' | 'medium' | 'high' | 'urgent'
}

export function useCompleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: CompleteTaskData }) => {
      const response = await api.post<{ task: Task; follow_up_task: Task | null }>(
        `/tasks/${id}/complete`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/tasks/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
