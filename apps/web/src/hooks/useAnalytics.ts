import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '../api/analytics'

export function useProjectAnalytics(projectId: string, orgId: string) {
  return useQuery({
    queryKey: ['analytics', projectId],
    queryFn: () => analyticsApi.projectStats(projectId, orgId),
    enabled: !!projectId && !!orgId,
  })
}
