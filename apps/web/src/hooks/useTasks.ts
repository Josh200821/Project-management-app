import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { tasksApi, CreateTaskPayload } from '../api/tasks'

export function useTasks(projectId: string, filters?: Record<string, string>) {
  return useQuery({
    queryKey: ['tasks', projectId, filters],
    queryFn: () => tasksApi.list(projectId, filters).then((r) => r.data),
    enabled: !!projectId,
  })
}

export function useCreateTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CreateTaskPayload) => tasksApi.create(payload).then((r) => r.data),
    onSuccess: (task) => {
      qc.invalidateQueries({ queryKey: ['tasks', task.projectId] })
    },
  })
}

export function useMoveTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ taskId, status, boardOrder }: { taskId: string; status: string; boardOrder: number }) =>
      tasksApi.move(taskId, status, boardOrder),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
