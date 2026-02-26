import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  action?: { label: string; handler: () => void }
}

const toasts = ref<Toast[]>([])

export const useToast = () => {
  const add = (toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    const duration = toast.duration ?? (toast.type === 'error' ? 6000 : 4000)
    
    const newToast = { ...toast, id, duration }
    toasts.value.push(newToast)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  const remove = (id: string) => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  const success = (title: string, message?: string) => add({ type: 'success', title, message })
  const error = (title: string, message?: string, action?: { label: string; handler: () => void }) => 
    add({ type: 'error', title, message, action })
  const warning = (title: string, message?: string) => add({ type: 'warning', title, message })
  const info = (title: string, message?: string) => add({ type: 'info', title, message })

  return {
    toasts,
    add,
    remove,
    success,
    error,
    warning,
    info
  }
}
