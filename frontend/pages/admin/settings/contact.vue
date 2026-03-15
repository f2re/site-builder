<script setup lang="ts">
definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const toast = useToast()
const { getSettings, updateSettings } = useAdminContact()

const { data: settings, pending, refresh } = await getSettings()

const contactEmail = ref<string>(settings.value?.contact_email ?? '')
const contactPageText = ref<string>(settings.value?.contact_page_text ?? '')

watch(settings, (val) => {
  if (val) {
    contactEmail.value = val.contact_email ?? ''
    contactPageText.value = val.contact_page_text ?? ''
  }
})

const saving = ref(false)

async function handleSave() {
  saving.value = true
  try {
    await updateSettings({
      contact_email: contactEmail.value || null,
      contact_page_text: contactPageText.value || null,
    })
    toast.success('Настройки сохранены', undefined)
    await refresh()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error('Ошибка сохранения', err.data?.detail || 'Не удалось сохранить настройки')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="header-title">
        <Icon name="ph:gear-bold" size="20" />
        <span>Настройки страницы обратной связи</span>
      </div>
    </template>

    <div class="settings-page">
      <div v-if="pending" class="skeleton-layout">
        <USkeleton height="80px" />
        <USkeleton height="300px" />
        <USkeleton height="50px" />
      </div>

      <form
        v-else
        class="settings-form"
        data-testid="settings-contact-form"
        @submit.prevent="handleSave"
      >
        <!-- Email field -->
        <div class="form-section">
          <div class="section-label">
            <Icon name="ph:envelope-bold" size="16" />
            <span>Уведомления</span>
          </div>
          <div class="form-field">
            <UInput
              v-model="contactEmail"
              type="email"
              label="Email для уведомлений о новых заявках"
              placeholder="admin@example.com"
              name="contact_email"
              data-testid="admin-settings-contact-email"
            />
            <p class="field-hint">
              На этот адрес будут приходить уведомления о новых заявках
            </p>
          </div>
        </div>

        <!-- Rich editor -->
        <div class="form-section">
          <div class="section-label">
            <Icon name="ph:text-align-left-bold" size="16" />
            <span>Текст на странице обратной связи</span>
          </div>
          <div class="form-field">
            <div class="editor-label">Текст приветствия над формой</div>
            <div
              data-testid="settings-contact-page-text-editor"
              class="editor-wrapper"
            >
              <URichEditor
                v-model="contactPageText"
                placeholder="Введите текст, который будет отображаться над формой обратной связи..."
              />
            </div>
            <p class="field-hint">
              Этот текст отображается над формой обратной связи на сайте
            </p>
          </div>
        </div>

        <!-- Save button -->
        <div class="form-actions">
          <UButton
            type="submit"
            variant="primary"
            :loading="saving"
            data-testid="admin-settings-contact-save-btn"
          >
            <template #icon>
              <Icon name="ph:floppy-disk-bold" size="16" />
            </template>
            Сохранить настройки
          </UButton>
        </div>
      </form>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text);
}

.settings-page {
  max-width: 860px;
}

.skeleton-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 860px;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.form-section:focus-within {
  border-color: var(--color-accent);
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-2);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-field {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  margin-bottom: 4px;
}

.editor-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.field-hint {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin: 0;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}
</style>
