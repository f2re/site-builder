<script setup lang="ts">
definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { confirm } = useConfirm()
const { getMessage, replyMessage, deleteMessage } = useAdminContact()

const id = route.params.id as string

const { data: message, pending, error, refresh } = await getMessage(id)

const replying = ref(false)
const deleting = ref(false)

async function handleReply() {
  if (!message.value || message.value.status === 'REPLIED') return
  replying.value = true
  try {
    await replyMessage(id)
    toast.success('Статус обновлён', 'Заявка отмечена как отвеченная')
    await refresh()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error('Ошибка', err.data?.detail || 'Не удалось обновить статус')
  } finally {
    replying.value = false
  }
}

async function handleDelete() {
  const confirmed = await confirm({
    title: 'Удалить заявку?',
    message: 'Это действие нельзя отменить. Заявка будет удалена навсегда.',
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена',
    variant: 'danger',
  })
  if (!confirmed) return

  deleting.value = true
  try {
    await deleteMessage(id)
    toast.success('Заявка удалена')
    router.push('/admin/contact')
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.error('Ошибка удаления', err.data?.detail || 'Не удалось удалить заявку')
  } finally {
    deleting.value = false
  }
}

function getStatusVariant(status: string): 'accent' | 'info' | 'success' {
  if (status === 'NEW') return 'accent'
  if (status === 'REPLIED') return 'success'
  return 'info'
}

function getStatusLabel(status: string): string {
  if (status === 'NEW') return 'Новая'
  if (status === 'READ') return 'Прочитана'
  if (status === 'REPLIED') return 'Отвечено'
  return status
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="header-row">
        <NuxtLink
          to="/admin/contact"
          class="back-link"
          data-testid="contact-back-btn"
          aria-label="Назад к списку заявок"
        >
          <Icon name="ph:arrow-left-bold" size="20" />
        </NuxtLink>
        <span>Заявка</span>
      </div>
    </template>

    <div class="contact-detail-page">
      <!-- Skeleton -->
      <div v-if="pending" class="skeleton-layout">
        <USkeleton height="120px" />
        <USkeleton height="200px" />
        <USkeleton height="80px" />
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="error-state">
        <Icon name="ph:warning-circle-bold" size="48" />
        <p>Ошибка загрузки заявки</p>
        <UButton variant="secondary" @click="refresh">Повторить</UButton>
      </div>

      <!-- Content -->
      <div v-else-if="message" class="detail-layout" data-testid="admin-contact-detail">
        <!-- Sender info card -->
        <div class="detail-card" data-testid="contact-sender-info">
          <div class="card-header">
            <Icon name="ph:user-bold" size="18" />
            <h2 class="card-title">Отправитель</h2>
            <div class="status-area" data-testid="contact-status-badge">
              <UBadge :variant="getStatusVariant(message.status)" size="md">
                {{ getStatusLabel(message.status) }}
              </UBadge>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Имя</span>
              <span class="info-value">{{ message.name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Email</span>
              <a :href="`mailto:${message.email}`" class="info-value info-link">
                {{ message.email }}
              </a>
            </div>
            <div v-if="message.phone" class="info-row">
              <span class="info-label">Телефон</span>
              <a :href="`tel:${message.phone}`" class="info-value info-link">
                {{ message.phone }}
              </a>
            </div>
            <div class="info-row">
              <span class="info-label">Тема</span>
              <span class="info-value info-subject">{{ message.subject }}</span>
            </div>
          </div>
        </div>

        <!-- Message body -->
        <div class="detail-card" data-testid="contact-message-body">
          <div class="card-header">
            <Icon name="ph:chat-circle-text-bold" size="18" />
            <h2 class="card-title">Сообщение</h2>
          </div>
          <div class="message-text">
            {{ message.message }}
          </div>
        </div>

        <!-- Metadata -->
        <div class="detail-card metadata-card">
          <div class="card-header">
            <Icon name="ph:info-bold" size="18" />
            <h2 class="card-title">Метаданные</h2>
          </div>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">IP-адрес</span>
              <span class="info-value font-mono">{{ message.ip_address || '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Получена</span>
              <span class="info-value">{{ formatDate(message.created_at) }}</span>
            </div>
            <div v-if="message.read_at" class="info-row">
              <span class="info-label">Прочитана</span>
              <span class="info-value">{{ formatDate(message.read_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions-row">
          <UButton
            v-if="message.status !== 'REPLIED'"
            variant="primary"
            :loading="replying"
            data-testid="admin-contact-reply-btn"
            @click="handleReply"
          >
            <template #icon>
              <Icon name="ph:check-circle-bold" size="16" />
            </template>
            Отметить как отвеченное
          </UButton>

          <UButton
            variant="danger"
            :loading="deleting"
            data-testid="admin-contact-delete-btn"
            @click="handleDelete"
          >
            <template #icon>
              <Icon name="ph:trash-bold" size="16" />
            </template>
            Удалить
          </UButton>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  color: var(--color-text-2);
  text-decoration: none;
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent);
  background: var(--color-surface-2);
}

.contact-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
}

.skeleton-layout {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 64px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-2);
  text-align: center;
}

.detail-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color var(--transition-fast);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-2);
}

.card-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  flex: 1;
}

.status-area {
  margin-left: auto;
}

.info-grid {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  gap: 16px;
}

.info-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  min-width: 100px;
  flex-shrink: 0;
  padding-top: 2px;
}

.info-value {
  font-size: var(--text-sm);
  color: var(--color-text);
}

.info-link {
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.info-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.info-subject {
  font-weight: 600;
  font-size: var(--text-base);
}

.font-mono {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.message-text {
  padding: 20px;
  font-size: var(--text-base);
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
  word-break: break-word;
}

.metadata-card {
  font-size: var(--text-sm);
}

.actions-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 8px;
}

@media (max-width: 480px) {
  .info-row {
    flex-direction: column;
    gap: 4px;
  }

  .info-label {
    min-width: unset;
  }

  .actions-row {
    flex-direction: column;
  }
}
</style>
