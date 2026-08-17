import { useEffect } from 'react'
import { connectWebSocket, disconnectWebSocket } from '../lib/websocket'
import { getAccessToken } from '../lib/auth'

export function useWebSocket() {
  useEffect(() => {
    const token = getAccessToken()
    if (token) {
      connectWebSocket(token)
    }
    return () => disconnectWebSocket()
  }, [])
}
