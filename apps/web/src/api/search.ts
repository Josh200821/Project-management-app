import { apiClient } from '../lib/auth'

export const searchApi = {
  search: (q: string, orgId: string) =>
    apiClient.get<{ data: any[] }>(`/search?q=${encodeURIComponent(q)}&org_id=${orgId}`).then(r => r.data.data),
}
