import { apiClient } from '../lib/auth'

export const analyticsApi = {
  projectStats: (projectId: string, orgId: string) =>
    apiClient.get<{ data: any }>(`/analytics/projects/${projectId}?org_id=${orgId}`).then(r => r.data.data),
}
