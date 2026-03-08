/**
 * usePrompt — Promise-based composable для диалогов ввода текста.
 *
 * Singleton: один глобальный диалог на всё приложение.
 * Компонент UPromptDialog должен быть размещён в app.vue один раз.
 *
 * @example
 * const { prompt } = usePrompt()
 * const url = await prompt({ title: 'Введите URL', placeholder: 'https://...' })
 * if (url === null) return // пользователь отменил
 */

import { ref } from 'vue'

export interface PromptOptions {
  /** Заголовок диалога */
  title: string
  /** Label для поля ввода */
  label?: string
  /** Placeholder поля ввода */
  placeholder?: string
  /** Начальное значение поля ввода */
  defaultValue?: string
  /** Тип поля ввода */
  inputType?: 'text' | 'url' | 'email'
  /** Текст кнопки подтверждения (по умолчанию: 'OK') */
  confirmLabel?: string
  /** Текст кнопки отмены (по умолчанию: 'Отмена') */
  cancelLabel?: string
}

interface PromptState {
  open: boolean
  title: string
  label: string
  placeholder: string
  defaultValue: string
  inputType: 'text' | 'url' | 'email'
  confirmLabel: string
  cancelLabel: string
  resolve: ((value: string | null) => void) | null
}

const state = ref<PromptState>({
  open: false,
  title: '',
  label: '',
  placeholder: '',
  defaultValue: '',
  inputType: 'text',
  confirmLabel: 'OK',
  cancelLabel: 'Отмена',
  resolve: null,
})

/**
 * Глобальный composable для отображения диалога ввода текста.
 * Требует наличия компонента <UPromptDialog /> в app.vue.
 */
export const usePrompt = () => {
  /**
   * Открывает диалог ввода и возвращает Promise<string | null>.
   * null — пользователь нажал «Отмена» или закрыл диалог.
   */
  const prompt = (options: PromptOptions): Promise<string | null> => {
    return new Promise<string | null>((resolve) => {
      state.value = {
        open: true,
        title: options.title,
        label: options.label ?? '',
        placeholder: options.placeholder ?? '',
        defaultValue: options.defaultValue ?? '',
        inputType: options.inputType ?? 'text',
        confirmLabel: options.confirmLabel ?? 'OK',
        cancelLabel: options.cancelLabel ?? 'Отмена',
        resolve,
      }
    })
  }

  /** Вызывается компонентом UPromptDialog при подтверждении или отмене */
  const _resolve = (value: string | null) => {
    if (state.value.resolve) {
      state.value.resolve(value)
    }
    state.value.open = false
    state.value.resolve = null
  }

  return {
    /** Реактивное состояние диалога (используется в UPromptDialog) */
    state,
    prompt,
    _resolve,
  }
}
