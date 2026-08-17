import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsApi } from '../api/notifications'
import { useNotificationStore } from '../stores/notificationStore'
import { useEffect } from 'react'

export function useNotifications() {
  const setNotifications = useNotificationStore((s) => s.setNotifications)
  const query = useQuery({ queryKey: ['notifications'], queryFn: notificationsApi.list })
  useEffect(() => {
    if (query.data) setNotifications(query.data)
  }, [query.data, setNotifications])
  return query
}

export function useMarkRead() {
  const qc = useQueryClient()
  const markRead = useNotificationStore((s) => s.markRead)
  return useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: (_, id) => {
      markRead(id)
      qc.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useMarkAllRead() {
  const qc = useQueryClient()
  const markAllRead = useNotificationStore((s) => s.markAllRead)
  return useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      markAllRead()
      qc.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}
