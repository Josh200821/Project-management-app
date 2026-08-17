import { useState } from 'react'
import { useNotificationStore } from '../../stores/notificationStore'
import { useMarkRead, useMarkAllRead } from '../../hooks/useNotifications'
import { formatRelative } from '../../lib/utils'

export function NotificationCenter() {
  const [open, setOpen] = useState(false)
  const { notifications, unreadCount } = useNotificationStore()
  const markRead = useMarkRead()
  const markAllRead = useMarkAllRead()

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-violet-600 text-[10px] font-bold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-10 z-50 w-80 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
            <h3 className="text-sm font-semibold text-white">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={() => markAllRead.mutate()}
                className="text-xs text-violet-400 hover:text-violet-300"
              >
                Mark all read
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-center text-sm text-slate-500 py-8">No notifications</p>
            ) : (
              notifications.slice(0, 20).map((n) => (
                <div
                  key={n.id}
                  onClick={() => { if (!n.read_at) markRead.mutate(n.id) }}
                  className={`px-4 py-3 border-b border-slate-800 cursor-pointer hover:bg-slate-800 transition-colors ${!n.read_at ? 'bg-slate-800/50' : ''}`}
                >
                  <div className="flex items-start gap-3">
                    {!n.read_at && <div className="mt-1.5 h-2 w-2 rounded-full bg-violet-500 shrink-0" />}
                    <div className={!n.read_at ? '' : 'ml-5'}>
                      <p className="text-sm text-slate-200">{n.title}</p>
                      {n.body && <p className="text-xs text-slate-400 mt-0.5">{n.body}</p>}
                      <p className="text-xs text-slate-500 mt-1">{formatRelative(n.created_at)}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
