<script setup lang="ts">
import { ref } from 'vue'
import { useUser, type UserAddress } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import USkeleton from '~/components/U/USkeleton.vue'

const props = defineProps<{
  userId: string
}>()

const toast = useToast()
const { confirm } = useConfirm()
const { adminGetUserAddresses, adminDeleteUserAddress } = useUser()

const { data: addresses, pending, refresh } = adminGetUserAddresses(props.userId)

const deletingId = ref<string | null>(null)

const handleDeleteAddress = async (addr: UserAddress) => {
  const label = addr.full_address || [addr.city, addr.street, addr.house].filter(Boolean).join(', ') || `Адрес #${addr.id}`
  const confirmed = await confirm({
    title: 'Удалить адрес?',
    message: label,
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена',
    variant: 'danger',
  })
  if (!confirmed) return

  deletingId.value = addr.id
  try {
    await adminDeleteUserAddress(props.userId, addr.id)
    toast.success('Адрес удалён')
    await refresh()
  } catch (err: unknown) {
    const apiErr = err as { data?: { message?: string; detail?: string } }
    toast.error(apiErr.data?.message || apiErr.data?.detail || 'Не удалось удалить адрес')
  } finally {
    deletingId.value = null
  }
}

const formatAddress = (addr: UserAddress): string => {
  if (addr.full_address) return addr.full_address
  return [addr.postal_code, addr.city, addr.street, addr.house, addr.apartment]
    .filter(Boolean)
    .join(', ')
}
</script>

<template>
  <div class="addresses-list" data-testid="user-addresses-section">
    <div v-if="pending" class="addresses-loading">
      <USkeleton v-for="i in 2" :key="i" height="52px" class="addr-skeleton" />
    </div>

    <div v-else-if="!addresses || addresses.length === 0" class="addresses-empty">
      Адресов нет
    </div>

    <ul v-else class="addresses-ul">
      <li
        v-for="addr in addresses"
        :key="addr.id"
        class="address-item"
        data-testid="address-item"
      >
        <div class="address-info">
          <Icon name="ph:map-pin-bold" size="16" class="address-icon" />
          <span class="address-text">{{ formatAddress(addr) }}</span>
          <span v-if="addr.is_default" class="address-default-badge">По умолчанию</span>
        </div>
        <UButton
          variant="ghost"
          size="sm"
          :loading="deletingId === addr.id"
          :aria-label="`Удалить адрес ${formatAddress(addr)}`"
          class="delete-addr-btn"
          data-testid="delete-address-btn"
          @click="handleDeleteAddress(addr)"
        >
          <template #icon>
            <Icon name="ph:trash-bold" size="16" />
          </template>
        </UButton>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.addresses-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.addresses-loading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.addr-skeleton {
  margin-bottom: 0;
}

.addresses-empty {
  color: var(--color-muted);
  font-size: var(--text-sm);
  text-align: center;
  padding: 12px 0;
}

.addresses-ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.address-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.address-item:hover {
  border-color: var(--color-accent);
}

.address-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.address-icon {
  color: var(--color-muted);
  flex-shrink: 0;
}

.address-text {
  font-size: var(--text-sm);
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.address-default-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 6px;
  background: var(--color-accent-glow);
  color: var(--color-accent);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.delete-addr-btn {
  flex-shrink: 0;
}
</style>
