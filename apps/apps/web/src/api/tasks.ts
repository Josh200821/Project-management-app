import { apiClient } from './client'

export interface Task {
  id: string
  projectId: string
  taskNumber: number
  title: string
  description: string | null
  status: 'todo' | 'in_progress' | 'in_review' | 'done'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  storyPoints: number | null
  dueDate: string | null
  assigneeId: string | null
  boardOrder: number
  createdAt: string
}

export interface CreateTaskPayload {
  project_id: string
  title: string
  description?: string
  status?: string
  priority?: string
  assignee_id?: string
  due_date?: string
  sprint_id?: string
}

export const tasksApi = {
  list: (projectId: string, params?: Record<string, string>) =>
    apiClient.get<Task[]>('/tasks', { params: { project_id: projectId, ...params } }),

  get: (taskId: string) =>
    apiClient.get<Task>(`/tasks/${taskId}`),

  create: (payload: CreateTaskPayload) =>
    apiClient.post<Task>('/tasks', payload),

  update: (taskId: string, payload: Partial<CreateTaskPayload>) =>
    apiClient.patch<Task>(`/tasks/${taskId}`, payload),

  delete: (taskId: string) =>
    apiClient.delete(`/tasks/${taskId}`),

  move: (taskId: string, status: string, boardOrder: number) =>
    apiClient.post(`/tasks/${taskId}/move`, { status, board_order: boardOrder }),

  search: (query: string) =>
    apiClient.get<Task[]>('/search', { params: { q: query } }),
}
