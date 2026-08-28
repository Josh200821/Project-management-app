import { apiClient } from '../lib/auth'

export interface Organization {
  id: string; name: string; slug: string; logo_url: string | null; plan: string; created_at: string
}

export const organizationsApi = {
  list: () => apiClient.get<{ data: Organization[] }>('/organizations').then(r => r.data.data),
  create: (data: { name: string; slug?: string }) =>
    apiClient.post<{ data: Organization }>('/organizations', data).then(r => r.data.data),
  inviteMember: (orgId: string, email: string, role = 'member') =>
    apiClient.post(`/organizations/${orgId}/members/invite`, { email, role }),
}
