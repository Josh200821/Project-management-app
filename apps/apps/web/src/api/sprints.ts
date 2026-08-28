import { apiClient } from '../lib/auth'

export interface Sprint {
  id: string; project_id: string; name: string; goal: string | null
  start_date: string | null; end_date: string | null
  status: string; capacity_points: number | null; velocity_points: number | null; created_at: string
}

export const sprintsApi = {
  list: (projectId: string) =>
    apiClient.get<{ data: Sprint[] }>(`/projects/${projectId}/sprints`).then(r => r.data.data),
  create: (projectId: string, data: Partial<Sprint>) =>
    apiClient.post<{ data: Sprint }>(`/projects/${projectId}/sprints`, data).then(r => r.data.data),
  update: (projectId: string, sprintId: string, data: Partial<Sprint>) =>
    apiClient.patch<{ data: Sprint }>(`/projects/${projectId}/sprints/${sprintId}`, data).then(r => r.data.data),
  close: (projectId: string, sprintId: string) =>
    apiClient.post(`/projects/${projectId}/sprints/${sprintId}/close`),
  burndown: (projectId: string, sprintId: string) =>
    apiClient.get<{ data: Array<{ day: string; remaining: number; ideal: number }> }>(
      `/projects/${projectId}/sprints/${sprintId}/burndown`
    ).then(r => r.data.data),
}
