import { apiClient } from '../lib/auth'

export interface SearchResult {
  id: string
  project_id: string
  task_number: number
  title: string
  status: string
  priority: string
  assignee_id: string | null
}

export const searchApi = {
  search: (q: string, orgId: string) =>
    apiClient.get<{ data: SearchResult[] }>(`/search?q=${encodeURIComponent(q)}&org_id=${orgId}`).then(r => r.data.data),
}
