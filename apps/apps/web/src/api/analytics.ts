import { apiClient } from '../lib/auth'

export interface ProjectAnalytics {
  total_tasks: number
  completed_tasks: number
  open_tasks: number
  overdue_tasks: number
  velocity: Array<{ sprint_name: string; completed_points: number; planned_points: number }>
  status_distribution: Array<{ status: string; count: number }>
  team_utilization: Array<{ user_id: string; full_name: string; open_tasks: number; hours_logged: number }>
}

export const analyticsApi = {
  projectStats: (projectId: string, orgId: string) =>
    apiClient.get<{ data: ProjectAnalytics }>(`/analytics/projects/${projectId}?org_id=${orgId}`).then(r => r.data.data),
}
