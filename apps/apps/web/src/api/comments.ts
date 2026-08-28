import { apiClient } from '../lib/auth'

export interface Comment {
  id: string; task_id: string; author_id: string; body: string
  edited_at: string | null; created_at: string
}

export const commentsApi = {
  list: (taskId: string) =>
    apiClient.get<{ data: Comment[] }>(`/tasks/${taskId}/comments`).then(r => r.data.data),
  create: (taskId: string, body: string) =>
    apiClient.post<{ data: Comment }>(`/tasks/${taskId}/comments`, { body }).then(r => r.data.data),
  update: (taskId: string, commentId: string, body: string) =>
    apiClient.patch<{ data: Comment }>(`/tasks/${taskId}/comments/${commentId}`, { body }).then(r => r.data.data),
  delete: (taskId: string, commentId: string) =>
    apiClient.delete(`/tasks/${taskId}/comments/${commentId}`),
}
