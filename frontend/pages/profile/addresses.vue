<script setup lang="ts">
import { ref } from 'vue'
import { useAddresses } from '~/composables/useAddresses'
import type { DeliveryAddress, CreateAddressRequest } from '~/composables/useAddresses'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

const { getAddresses, createAddress, updateAddress, deleteAddress, setDefaultAddress } = useAddresses()
const toast = useToast()
const { confirm } = useConfirm()

const { data, pending, refresh } = await getAddresses()
const addresses = computed(() => data.value?.items || [])

const showForm = ref(false)
const editingAddress = ref<DeliveryAddress | undefined>()
const formPending = ref(false)

const openAddForm = () => {
  editingAddress.value = undefined
  showForm.value = true
}

const openEditForm = (address: DeliveryAddress) => {
  editingAddress.value = address
  showForm.value = true
}

const handleSubmit = async (formData: CreateAddressRequest) => {
  formPending.value = true
  try {
    if (editingAddress.value) {
      await updateAddress(editingAddress.value.id, formData)
      toast.success('Адрес обновлён')
    } else {
      await createAddress(formData)
      toast.success('Адрес добавлен')
    }
    showForm.value = false
    await refresh()
  } catch {
    toast.error('Ошибка', 'Не удалось сохранить адрес')
  } finally {
    formPending.value = false
  }
}

const handleDelete = async (address: DeliveryAddress) => {
  if (!await confirm({ title: `Удалить адрес «${address.name}»?`, message: 'Это действие нельзя отменить.', confirmLabel: 'Удалить', variant: 'danger' })) return
  try {
    await deleteAddress(address.id)
    toast.success('Адрес удалён')
    await refresh()
  } catch {
    toast.error('Ошибка', 'Не удалось удалить адрес')
  }
}

const handleSetDefault = async (address: DeliveryAddress) => {
  try {
    await setDefaultAddress(address.id)
    toast.success('Адрес установлен по умолчанию')
    await refresh()
  } catch {
    toast.error('Ошибка')
  }
}

useSeoMeta({
  title: 'Мои адреса | WifiOBD',
  description: 'Управление адресами доставки'
})
</script>

<template>
  <div class="addresses-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">Мои адреса</h1>
        <button class="btn btn--primary" data-testid="add-address-btn" @click="openAddForm">
          <Icon name="ph:plus-bold" size="16" />
          Добавить адрес
        </button>
      </div>

      <div v-if="pending" class="loading-state">
        <Icon name="ph:spinner-gap-bold" size="32" class="spin" />
        <p>Загрузка...</p>
      </div>

      <div v-else-if="addresses.length === 0" class="empty-state">
        <Icon name="ph:map-pin-slash-bold" size="48" />
        <p>У вас пока нет сохранённых адресов</p>
        <button class="btn btn--primary" @click="openAddForm">Добавить первый адрес</button>
      </div>

      <div v-else class="addresses-grid" data-testid="addresses-list">
        <AddressCard
          v-for="addr in addresses"
          :key="addr.id"
          :address="addr"
          @edit="openEditForm(addr)"
          @delete="handleDelete(addr)"
          @set-default="handleSetDefault(addr)"
        />
      </div>

      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal-content" data-testid="address-form-modal">
          <h2 class="modal-title">{{ editingAddress ? 'Редактировать адрес' : 'Новый адрес' }}</h2>
          <AddressForm
            :address="editingAddress"
            :pending="formPending"
            @submit="handleSubmit"
            @cancel="showForm = false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.addresses-page {
  padding: 40px 0 80px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 0;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 20px;
  color: var(--color-muted);
}

.addresses-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 768px) {
  .addresses-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: 20px;
}

.modal-content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 32px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 24px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: var(--text-sm);
  cursor: pointer;
  border: none;
  transition: background var(--transition-fast), transform var(--transition-fast);
  min-height: 44px;
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
