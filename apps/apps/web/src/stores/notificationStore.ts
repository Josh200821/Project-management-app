import { create } from 'zustand'

export interface Notification {
  id: string
  type: string
  title: string
  body: string
  entity_type: string | null
  entity_id: string | null
  read_at: string | null
  created_at: string
}

interface NotificationState {
  notifications: Notification[]
  unreadCount: number
  setNotifications: (n: Notification[]) => void
  addNotification: (n: Notification) => void
  markRead: (id: string) => void
  markAllRead: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  unreadCount: 0,
  setNotifications: (notifications) =>
    set({ notifications, unreadCount: notifications.filter((n) => !n.read_at).length }),
  addNotification: (n) =>
    set((s) => ({
      notifications: [n, ...s.notifications],
      unreadCount: s.unreadCount + 1,
    })),
  markRead: (id) =>
    set((s) => ({
      notifications: s.notifications.map((n) =>
        n.id === id ? { ...n, read_at: new Date().toISOString() } : n
      ),
      unreadCount: Math.max(0, s.unreadCount - 1),
    })),
  markAllRead: () =>
    set((s) => ({
      notifications: s.notifications.map((n) => ({
        ...n,
        read_at: n.read_at ?? new Date().toISOString(),
      })),
      unreadCount: 0,
    })),
}))
