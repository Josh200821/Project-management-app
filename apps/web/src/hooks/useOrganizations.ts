import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { organizationsApi } from '../api/organizations'

export function useOrganizations() {
  return useQuery({ queryKey: ['organizations'], queryFn: organizationsApi.list })
}

export function useCreateOrganization() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: organizationsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['organizations'] }),
  })
}
