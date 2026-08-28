import { useNotifications, useMarkRead, useMarkAllRead } from "../../hooks/useNotifications"
import { useNotificationStore } from "../../stores/notificationStore"
import { formatRelative } from "../../lib/utils"

export default function NotificationsPage() {
  const { isLoading } = useNotifications()
  const { notifications, unreadCount } = useNotificationStore()
  const markAllRead = useMarkAllRead()
  const markRead = useMarkRead()

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-white">Notifications {unreadCount > 0 && <span className="text-sm text-slate-400">({unreadCount} unread)</span>}</h1>
        {unreadCount > 0 && <button onClick={() => markAllRead.mutate()} className="text-sm text-violet-400 hover:text-violet-300">Mark all read</button>}
      </div>
      <div className="space-y-2">
        {isLoading ? (
          <p className="text-center py-16 text-slate-500">Loading notifications…</p>
        ) : notifications.length === 0 ? (
          <p className="text-center py-16 text-slate-500">You are all caught up!</p>
        ) : notifications.map((n) => (
          <div key={n.id} onClick={() => { if (!n.read_at) markRead.mutate(n.id) }}
            className={"flex gap-4 p-4 rounded-xl border cursor-pointer transition-colors " + (!n.read_at ? "bg-slate-800/60 border-slate-700" : "bg-slate-900/40 border-slate-800")}>
            {!n.read_at && <div className="mt-2 h-2 w-2 rounded-full bg-violet-500 shrink-0" />}
            <div className={!n.read_at ? "" : "ml-5"}>
              <p className="text-sm font-medium text-slate-100">{n.title}</p>
              {n.body && <p className="text-sm text-slate-400 mt-0.5">{n.body}</p>}
              <p className="text-xs text-slate-500 mt-1">{formatRelative(n.created_at)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}