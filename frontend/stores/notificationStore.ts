import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './authStore'
import { useToast } from '~/composables/useToast'

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  read: boolean
  created_at: string
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const ws = ref<WebSocket | null>(null)
  const authStore = useAuthStore()
  const config = useRuntimeConfig()
  const toast = useToast()

  const wsUrl = (config.public.wsUrl as string) || 'ws://localhost:8000/api/v1/ws/notifications'

  function connect() {
    if (import.meta.server) return
    if (!authStore.accessToken || ws.value) return

    try {
      ws.value = new WebSocket(`${wsUrl}?token=${authStore.accessToken}`)

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'notification') {
            const payload = data.payload as Notification
            notifications.value.unshift({ ...payload, read: false })
            
            toast.add({
              title: payload.title,
              message: payload.message,
              type: payload.type || 'info'
            })
          }
        } catch (e) {
          console.error('Failed to parse WS message', e)
        }
      }

      ws.value.onclose = () => {
        ws.value = null
        if (authStore.isAuthenticated) {
          setTimeout(connect, 5000)
        }
      }

      ws.value.onerror = (err) => {
        console.error('WebSocket error:', err)
        ws.value?.close()
      }
    } catch (e) {
      console.error('Failed to connect to WS', e)
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  function markAsRead(id: string) {
    const n = notifications.value.find(n => n.id === id)
    if (n) n.read = true
  }

  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

  return {
    notifications,
    unreadCount,
    connect,
    disconnect,
    markAsRead
  }
})
