import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'

export function useProjects(orgId: string) {
  return useQuery({
    queryKey: ['projects', orgId],
    queryFn: () => projectsApi.list(orgId),
    enabled: !!orgId,
  })
}

export function useProject(orgId: string, projectId: string) {
  return useQuery({
    queryKey: ['projects', orgId, projectId],
    queryFn: () => projectsApi.get(orgId, projectId),
    enabled: !!orgId && !!projectId,
  })
}

export function useCreateProject(orgId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) => projectsApi.create(orgId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects', orgId] }),
  })
}
