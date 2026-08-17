import { apiClient } from '../lib/auth'
import type { Project } from '../stores/projectStore'

export const projectsApi = {
  list: (orgId: string) =>
    apiClient.get<{ data: Project[] }>(`/organizations/${orgId}/projects`).then(r => r.data.data),
  get: (orgId: string, projectId: string) =>
    apiClient.get<{ data: Project }>(`/organizations/${orgId}/projects/${projectId}`).then(r => r.data.data),
  create: (orgId: string, data: { name: string; description?: string }) =>
    apiClient.post<{ data: Project }>(`/organizations/${orgId}/projects`, data).then(r => r.data.data),
  update: (orgId: string, projectId: string, data: Partial<Project>) =>
    apiClient.patch<{ data: Project }>(`/organizations/${orgId}/projects/${projectId}`, data).then(r => r.data.data),
  delete: (orgId: string, projectId: string) =>
    apiClient.delete(`/organizations/${orgId}/projects/${projectId}`),
}
