import { apiClient } from '../lib/auth'
import type { Notification } from '../stores/notificationStore'

export const notificationsApi = {
  list: () => apiClient.get<{ data: Notification[] }>('/notifications').then(r => r.data.data),
  markRead: (id: string) => apiClient.post(`/notifications/${id}/read`),
  markAllRead: () => apiClient.post('/notifications/read-all'),
}
