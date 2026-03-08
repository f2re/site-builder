/**
 * useConfirm — Promise-based composable для диалогов подтверждения.
 *
 * Singleton: один глобальный диалог на всё приложение.
 * Компонент UConfirmDialog должен быть размещён в app.vue один раз.
 *
 * @example
 * const { confirm } = useConfirm()
 * if (!await confirm({ title: 'Удалить?', variant: 'danger' })) return
 */

import { ref } from 'vue'

export type ConfirmVariant = 'danger' | 'warning' | 'default'

export interface ConfirmOptions {
  /** Заголовок диалога */
  title: string
  /** Дополнительное описание */
  message?: string
  /** Текст кнопки подтверждения (по умолчанию: 'Подтвердить') */
  confirmLabel?: string
  /** Текст кнопки отмены (по умолчанию: 'Отмена') */
  cancelLabel?: string
  /** Визуальный стиль кнопки подтверждения */
  variant?: ConfirmVariant
}

interface ConfirmState {
  open: boolean
  title: string
  message: string
  confirmLabel: string
  cancelLabel: string
  variant: ConfirmVariant
  resolve: ((value: boolean) => void) | null
}

const state = ref<ConfirmState>({
  open: false,
  title: '',
  message: '',
  confirmLabel: 'Подтвердить',
  cancelLabel: 'Отмена',
  variant: 'default',
  resolve: null,
})

/**
 * Глобальный composable для отображения диалога подтверждения.
 * Требует наличия компонента <UConfirmDialog /> в app.vue.
 */
export const useConfirm = () => {
  /**
   * Открывает диалог подтверждения и возвращает Promise<boolean>.
   * true — пользователь нажал «Подтвердить», false — «Отмена» или закрыл.
   */
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      state.value = {
        open: true,
        title: options.title,
        message: options.message ?? '',
        confirmLabel: options.confirmLabel ?? 'Подтвердить',
        cancelLabel: options.cancelLabel ?? 'Отмена',
        variant: options.variant ?? 'default',
        resolve,
      }
    })
  }

  /** Вызывается компонентом UConfirmDialog при нажатии «Подтвердить» */
  const _resolve = (value: boolean) => {
    if (state.value.resolve) {
      state.value.resolve(value)
    }
    state.value.open = false
    state.value.resolve = null
  }

  return {
    /** Реактивное состояние диалога (используется в UConfirmDialog) */
    state,
    confirm,
    _resolve,
  }
}
