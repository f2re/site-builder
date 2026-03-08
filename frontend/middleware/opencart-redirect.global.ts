// Middleware: opencart-redirect.global.ts | Agent: frontend-agent | Task: p15_frontend_opencart_redirect

interface RedirectRecord {
  id: string
  old_path: string
  new_path: string
  redirect_code: number
  is_active: boolean
}

export default defineNuxtRouteMiddleware(async (to) => {
  // Активируем middleware ТОЛЬКО для OpenCart-стиля URL (/index.php)
  if (!to.path.startsWith('/index.php')) {
    return
  }

  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  // Составляем old_path = полный путь с query string
  const queryString = new URLSearchParams(
    to.query as Record<string, string>,
  ).toString()
  const oldPath = queryString ? `${to.path}?${queryString}` : to.path

  try {
    const data = await $fetch<RedirectRecord>(
      `/redirects/lookup?old_path=${encodeURIComponent(oldPath)}`,
      {
        baseURL: apiBase,
        // $fetch выбрасывает исключение при 4xx/5xx — обрабатываем ниже
      },
    )

    if (data && data.new_path && data.is_active) {
      const code = data.redirect_code === 302 ? 302 : 301
      return navigateTo(data.new_path, { redirectCode: code })
    }
  } catch (error: unknown) {
    // 404 — редирект не настроен, пропускаем навигацию
    if (
      error !== null &&
      typeof error === 'object' &&
      'statusCode' in error &&
      (error as { statusCode: number }).statusCode === 404
    ) {
      return
    }

    // Сетевая ошибка или 5xx — логируем и пропускаем, не крашим навигацию
    console.warn('[opencart-redirect] API error for path:', oldPath, error)
  }
})
