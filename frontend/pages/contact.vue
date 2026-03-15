<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useContact } from '~/composables/useContact'
import { useToast } from '~/composables/useToast'

useSeoMeta({
  title: 'Обратная связь — WifiOBD',
  description: 'Свяжитесь с нами. Форма обратной связи WifiOBD — задайте вопрос, оставьте заявку или сообщите об ошибке.',
})

const config = useRuntimeConfig()
const { submitContactForm, getContactSettings } = useContact()
const toast = useToast()

// ── Settings (greeting text) ────────────────────────────────
const settings = ref({ contact_page_text: null as string | null })

onMounted(async () => {
  settings.value = await getContactSettings()

  // Load SmartCaptcha widget after mount (client-only)
  if (config.public.smartCaptchaSiteKey) {
    initSmartCaptcha()
  }
})

// ── Form state ───────────────────────────────────────────────
const form = reactive({
  name: '',
  email: '',
  phone: '',
  subject: '',
  message: '',
})

const captchaToken = ref('')
const pending = ref(false)

// ── Errors ───────────────────────────────────────────────────
const errors = reactive({
  name: '',
  email: '',
  subject: '',
  message: '',
})

// ── Computed ─────────────────────────────────────────────────
const canSubmit = computed(() => {
  const hasToken = config.public.smartCaptchaSiteKey
    ? !!captchaToken.value
    : true
  return hasToken && !pending.value
})

// ── Validation ───────────────────────────────────────────────
function validateForm(): boolean {
  let valid = true

  errors.name = ''
  errors.email = ''
  errors.subject = ''
  errors.message = ''

  if (!form.name.trim() || form.name.trim().length < 2) {
    errors.name = 'Введите имя (минимум 2 символа)'
    valid = false
  }

  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email.trim() || !emailRe.test(form.email.trim())) {
    errors.email = 'Введите корректный email'
    valid = false
  }

  if (!form.subject.trim() || form.subject.trim().length < 2) {
    errors.subject = 'Укажите тему сообщения (минимум 2 символа)'
    valid = false
  }

  if (!form.message.trim() || form.message.trim().length < 10) {
    errors.message = 'Напишите сообщение (минимум 10 символов)'
    valid = false
  }

  return valid
}

// ── SmartCaptcha ─────────────────────────────────────────────
let smartCaptchaWidgetId: number | undefined

type SmartCaptchaInstance = {
  render: (el: HTMLElement, opts: object) => number
  reset: (id: number) => void
}

function getSmartCaptcha(): SmartCaptchaInstance | undefined {
  return (window as Record<string, unknown>).smartCaptcha as SmartCaptchaInstance | undefined
}

function initSmartCaptcha() {
  const el = document.getElementById('smartcaptcha-widget')
  if (!el) return

  const sc = getSmartCaptcha()
  if (!sc) {
    // Script may still be loading — retry after 100ms
    setTimeout(initSmartCaptcha, 100)
    return
  }

  smartCaptchaWidgetId = sc.render(el, {
    sitekey: config.public.smartCaptchaSiteKey,
    callback: (token: string) => {
      captchaToken.value = token
    },
    'expired-callback': () => {
      captchaToken.value = ''
    },
    'error-callback': () => {
      captchaToken.value = ''
    },
  })
}

function resetSmartCaptcha() {
  const sc = getSmartCaptcha()
  if (sc && smartCaptchaWidgetId !== undefined) {
    sc.reset(smartCaptchaWidgetId)
  }
  captchaToken.value = ''
}

// ── Submit ────────────────────────────────────────────────────
async function handleSubmit() {
  if (!validateForm()) return
  if (pending.value) return

  pending.value = true

  const payload = {
    name: form.name.trim(),
    email: form.email.trim(),
    subject: form.subject.trim(),
    message: form.message.trim(),
    captcha_token: config.public.smartCaptchaSiteKey
      ? captchaToken.value
      : 'dev-bypass',
    ...(form.phone.trim() ? { phone: form.phone.trim() } : {}),
  }

  try {
    await submitContactForm(payload)

    toast.success('Заявка отправлена!', 'Мы свяжемся с вами в ближайшее время.')

    // Reset form
    form.name = ''
    form.email = ''
    form.phone = ''
    form.subject = ''
    form.message = ''
    resetSmartCaptcha()
  } catch (err: unknown) {
    const fetchErr = err as { status?: number }
    if (fetchErr?.status === 422) {
      toast.error('Ошибка проверки антибот', 'Пожалуйста, пройдите проверку SmartCaptcha снова.', {
        label: 'Обновить',
        handler: resetSmartCaptcha,
      })
      resetSmartCaptcha()
    } else if (fetchErr?.status === 429) {
      toast.add({
        type: 'warning',
        title: 'Слишком много запросов',
        message: 'Пожалуйста, подождите немного и попробуйте снова.',
        duration: 6000,
      })
    } else {
      toast.error('Ошибка сервера', 'Не удалось отправить заявку. Попробуйте позже.')
    }
  } finally {
    pending.value = false
  }
}

// Load SmartCaptcha script in head (client-side only, when sitekey configured)
if (config.public.smartCaptchaSiteKey) {
  useHead({
    script: [
      {
        src: 'https://smartcaptcha.yandexcloud.net/captcha.js',
        defer: true,
        async: true,
      },
    ],
  })
}
</script>

<template>
  <div class="contact-page">
    <!-- Hero -->
    <section class="contact-hero" aria-labelledby="contact-title">
      <div class="contact-hero__inner">
        <p class="contact-hero__eyebrow">Поддержка · Вопросы · Сотрудничество</p>
        <h1 id="contact-title" class="contact-hero__title">
          Свяжитесь <span class="text-accent">с нами</span>
        </h1>
        <p class="contact-hero__subtitle">
          Заполните форму — мы ответим в течение рабочего дня.
        </p>
      </div>
    </section>

    <!-- Main content -->
    <div class="contact-layout">
      <!-- Greeting text from settings -->
      <div
        v-if="settings.contact_page_text"
        class="contact-greeting"
        v-html="settings.contact_page_text"
      />

      <!-- Form card -->
      <div class="contact-card" data-testid="contact-form">
        <div class="contact-card__header">
          <Icon name="ph:envelope-simple-bold" class="contact-card__icon" aria-hidden="true" />
          <h2 class="contact-card__title">Форма обратной связи</h2>
        </div>

        <form class="contact-form" novalidate @submit.prevent="handleSubmit">
          <!-- Name + Email row -->
          <div class="form-row">
            <UInput
              v-model="form.name"
              label="Ваше имя *"
              name="name"
              type="text"
              placeholder="Иван Петров"
              :error="errors.name"
              autocomplete="name"
              data-testid="contact-name-input"
            />
            <UInput
              v-model="form.email"
              label="Email *"
              name="email"
              type="email"
              placeholder="ivan@example.com"
              :error="errors.email"
              autocomplete="email"
              data-testid="contact-email-input"
            />
          </div>

          <!-- Phone + Subject row -->
          <div class="form-row">
            <UInput
              v-model="form.phone"
              label="Телефон"
              name="phone"
              type="tel"
              placeholder="+7 (999) 000-00-00"
              autocomplete="tel"
              data-testid="contact-phone-input"
            />
            <UInput
              v-model="form.subject"
              label="Тема *"
              name="subject"
              type="text"
              placeholder="Вопрос по заказу"
              :error="errors.subject"
              data-testid="contact-subject-input"
            />
          </div>

          <!-- Message -->
          <UTextarea
            v-model="form.message"
            label="Сообщение *"
            name="message"
            placeholder="Опишите ваш вопрос или пожелание..."
            :rows="6"
            :error="errors.message"
            data-testid="contact-message-input"
          />

          <!-- SmartCaptcha widget -->
          <div class="captcha-wrapper" data-testid="contact-captcha">
            <div
              v-if="config.public.smartCaptchaSiteKey"
              id="smartcaptcha-widget"
            />
            <p v-else class="captcha-dev-note">
              <Icon name="ph:shield-check-bold" size="16" aria-hidden="true" />
              Режим разработки — SmartCaptcha отключена
            </p>
          </div>

          <!-- Submit button -->
          <UButton
            type="submit"
            variant="primary"
            size="lg"
            :loading="pending"
            :disabled="!canSubmit"
            block
            data-testid="contact-submit-btn"
          >
            <template #icon>
              <Icon name="ph:paper-plane-right-bold" size="20" aria-hidden="true" />
            </template>
            Отправить заявку
          </UButton>
        </form>
      </div>

      <!-- Info sidebar -->
      <aside class="contact-info" aria-label="Контактная информация">
        <div class="info-card">
          <div class="info-card__icon-wrap" aria-hidden="true">
            <Icon name="ph:clock-countdown-bold" size="28" />
          </div>
          <h3 class="info-card__title">Время ответа</h3>
          <p class="info-card__text">Отвечаем в течение одного рабочего дня</p>
        </div>

        <div class="info-card">
          <div class="info-card__icon-wrap" aria-hidden="true">
            <Icon name="ph:shield-check-bold" size="28" />
          </div>
          <h3 class="info-card__title">Защита данных</h3>
          <p class="info-card__text">Ваши данные в безопасности — мы не передаём их третьим лицам</p>
        </div>

        <div class="info-card">
          <div class="info-card__icon-wrap" aria-hidden="true">
            <Icon name="ph:headset-bold" size="28" />
          </div>
          <h3 class="info-card__title">Поддержка</h3>
          <p class="info-card__text">Техническая помощь по OBD2 устройствам и настройке</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.contact-page {
  min-height: 100vh;
  background-color: var(--color-bg);
  color: var(--color-text);
}

/* ── Hero ── */
.contact-hero {
  padding: clamp(3rem, 8vw, 6rem) clamp(1rem, 5vw, 3rem) clamp(2rem, 5vw, 4rem);
  text-align: center;
  background: linear-gradient(
    180deg,
    var(--color-bg-subtle) 0%,
    var(--color-bg) 100%
  );
  border-bottom: 1px solid var(--color-border);
}

.contact-hero__inner {
  max-width: 640px;
  margin: 0 auto;
}

.contact-hero__eyebrow {
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-accent);
  margin-bottom: 0.75rem;
}

.contact-hero__title {
  font-size: var(--text-3xl);
  font-weight: 800;
  line-height: 1.1;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.text-accent {
  color: var(--color-accent);
}

.contact-hero__subtitle {
  font-size: var(--text-base);
  color: var(--color-text-2);
  line-height: 1.6;
}

/* ── Layout ── */
.contact-layout {
  max-width: 1280px;
  margin: 0 auto;
  padding: clamp(2rem, 5vw, 4rem) clamp(1rem, 5vw, 3rem);
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .contact-layout {
    grid-template-columns: 1fr 320px;
    grid-template-rows: auto 1fr;
    align-items: start;
  }

  .contact-greeting {
    grid-column: 1 / -1;
  }

  .contact-card {
    grid-column: 1;
  }

  .contact-info {
    grid-column: 2;
    grid-row: 2;
  }
}

/* ── Greeting ── */
.contact-greeting {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem 2rem;
  color: var(--color-text-2);
  line-height: 1.7;
  font-size: var(--text-base);
}

/* ── Form card ── */
.contact-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: clamp(1.5rem, 4vw, 2.5rem);
  box-shadow: var(--shadow-card);
  transition:
    border-color var(--transition-normal),
    box-shadow var(--transition-normal);
}

.contact-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.contact-card__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.contact-card__icon {
  font-size: 1.75rem;
  color: var(--color-accent);
  flex-shrink: 0;
}

.contact-card__title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

/* ── Form rows ── */
.contact-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

/* ── SmartCaptcha ── */
.captcha-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 65px;
}

.captcha-dev-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-xs);
  color: var(--color-muted);
  background-color: var(--color-surface-2);
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-md);
  padding: 0.5rem 1rem;
}

/* ── Info sidebar ── */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.info-card:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.info-card__icon-wrap {
  color: var(--color-accent);
  display: flex;
  align-items: center;
}

.info-card__title {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.info-card__text {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  line-height: 1.5;
  margin: 0;
}
</style>
