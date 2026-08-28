import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { sprintsApi, Sprint } from '../api/sprints'

export function useSprints(projectId: string) {
  return useQuery({
    queryKey: ['sprints', projectId],
    queryFn: () => sprintsApi.list(projectId),
    enabled: !!projectId,
  })
}

export function useCreateSprint(projectId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Sprint>) => sprintsApi.create(projectId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sprints', projectId] }),
  })
}

export function useCloseSprint(projectId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (sprintId: string) => sprintsApi.close(projectId, sprintId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sprints', projectId] }),
  })
}

export function useBurndown(projectId: string, sprintId: string) {
  return useQuery({
    queryKey: ['burndown', projectId, sprintId],
    queryFn: () => sprintsApi.burndown(projectId, sprintId),
    enabled: !!projectId && !!sprintId,
  })
}
