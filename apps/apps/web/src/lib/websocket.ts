import { useNotificationStore } from '../stores/notificationStore'

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

export function connectWebSocket(token: string) {
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
  ws = new WebSocket(`${WS_URL}/ws/notifications?token=${token}`)

  ws.onopen = () => {
    console.log('[WS] Connected')
    if (reconnectTimer) clearTimeout(reconnectTimer)
  }

  ws.onmessage = (event) => {
    try {
      const notification = JSON.parse(event.data)
      useNotificationStore.getState().addNotification(notification)
    } catch {
      console.warn('[WS] Could not parse message', event.data)
    }
  }

  ws.onclose = () => {
    console.log('[WS] Disconnected — reconnecting in 3s')
    reconnectTimer = setTimeout(() => connectWebSocket(token), 3000)
  }

  ws.onerror = (err) => {
    console.error('[WS] Error', err)
    ws?.close()
  }
}

export function disconnectWebSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer)
  ws?.close()
  ws = null
}
