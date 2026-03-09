<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUser, type UserAdminUpdate, type UserAddress, type UserAddressCreate } from '~/composables/useUser'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UInput from '~/components/U/UInput.vue'
import USelect from '~/components/U/USelect.vue'
import UModal from '~/components/U/UModal.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import UBadge from '~/components/U/UBadge.vue'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { confirm } = useConfirm()
const userId = route.params.id as string
const { 
  adminGetUserFull, 
  adminUpdateUser, 
  adminCreateUserAddress, 
  adminUpdateUserAddress, 
  adminDeleteUserAddress 
} = useUser()

const { data: user, pending, error, refresh } = await adminGetUserFull(userId)

// General Info Form
const generalForm = ref<UserAdminUpdate>({
  full_name: '',
  email: '',
  phone: '',
  role: 'customer',
  is_active: true,
})

// Initialize form when data is loaded
if (user.value) {
  generalForm.value = {
    full_name: user.value.full_name || '',
    email: user.value.email || '',
    phone: user.value.phone || '',
    role: user.value.role,
    is_active: user.value.is_active,
  }
}

const isSavingGeneral = ref(false)
const handleSaveGeneral = async () => {
  isSavingGeneral.value = true
  try {
    await adminUpdateUser(userId, generalForm.value)
    toast.success('Данные пользователя обновлены')
    router.push(`/admin/users/${userId}`)
  } catch (err: any) {
    toast.error(err.data?.message || 'Не удалось обновить данные')
  } finally {
    isSavingGeneral.value = false
  }
}

// Address Management
const isAddressModalOpen = ref(false)
const isSavingAddress = ref(false)
const editingAddressId = ref<string | null>(null)

const addressForm = ref<UserAddressCreate>({
  name: '',
  recipient_name: '',
  recipient_phone: '',
  full_address: '',
  address_type: 'home',
  city: '',
  postal_code: '',
  provider: 'cdek',
  pickup_point_code: '',
  is_default: false,
})

const openAddAddress = () => {
  editingAddressId.value = null
  addressForm.value = {
    name: 'Основной',
    recipient_name: user.value?.full_name || '',
    recipient_phone: user.value?.phone || '',
    full_address: '',
    address_type: 'home',
    city: '',
    postal_code: '',
    provider: 'cdek',
    pickup_point_code: '',
    is_default: user.value?.addresses.length === 0,
  }
  isAddressModalOpen.value = true
}

const openEditAddress = (addr: UserAddress) => {
  editingAddressId.value = addr.id
  addressForm.value = {
    name: addr.name,
    recipient_name: addr.recipient_name,
    recipient_phone: addr.recipient_phone,
    full_address: addr.full_address,
    address_type: addr.address_type,
    city: addr.city,
    postal_code: addr.postal_code || '',
    provider: addr.provider,
    pickup_point_code: addr.pickup_point_code || '',
    is_default: addr.is_default,
  }
  isAddressModalOpen.value = true
}

const handleSaveAddress = async () => {
  isSavingAddress.value = true
  try {
    if (editingAddressId.value) {
      await adminUpdateUserAddress(userId, editingAddressId.value, addressForm.value)
      toast.success('Адрес обновлен')
    } else {
      await adminCreateUserAddress(userId, addressForm.value)
      toast.success('Адрес добавлен')
    }
    isAddressModalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.error(err.data?.message || 'Не удалось сохранить адрес')
  } finally {
    isSavingAddress.value = false
  }
}

const handleDeleteAddress = async (addrId: string) => {
  const confirmed = await confirm({
    title: 'Удалить адрес?',
    message: 'Вы уверены, что хотите удалить этот адрес?',
    variant: 'danger',
    confirmLabel: 'Удалить',
    cancelLabel: 'Отмена'
  })
  
  if (confirmed) {
    try {
      await adminDeleteUserAddress(userId, addrId)
      toast.success('Адрес удален')
      refresh()
    } catch (err: any) {
      toast.error(err.data?.message || 'Не удалось удалить адрес')
    }
  }
}

const roleOptions = [
  { label: 'Покупатель', value: 'customer' },
  { label: 'Менеджер', value: 'manager' },
  { label: 'Админ', value: 'admin' }
]

const addressTypeOptions = [
  { label: 'Дом', value: 'home' },
  { label: 'Работа', value: 'work' },
  { label: 'Пункт выдачи', value: 'pickup' },
  { label: 'Другое', value: 'other' }
]

const providerOptions = [
  { label: 'CDEK', value: 'cdek' },
  { label: 'Почта России', value: 'russian_post' },
  { label: 'Курьер', value: 'courier' }
]

const userInitials = computed(() => {
  if (!user.value?.full_name) return user.value?.email?.charAt(0).toUpperCase() || '?'
  return user.value.full_name
    .split(' ')
    .filter(Boolean)
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const formatDate = (dateString?: string | null) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('ru-RU')
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      <div class="flex items-center gap-2">
        <UButton 
          variant="ghost" 
          :to="`/admin/users/${userId}`" 
          size="sm" 
          aria-label="Назад" 
          data-testid="back-to-view-btn" 
          class="p-1 -ml-2"
        >
          <template #icon><Icon name="ph:caret-left-bold" size="20" /></template>
        </UButton>
        <span class="text-muted mr-1 hidden sm:inline">Редактирование:</span>
        <h1 class="font-bold text-lg truncate max-w-[200px] sm:max-w-none">
          {{ user?.full_name || user?.email || 'Загрузка...' }}
        </h1>
      </div>
    </template>

    <div v-if="pending" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-4"><USkeleton height="320px" /></div>
        <div class="lg:col-span-8"><USkeleton height="600px" /></div>
      </div>
    </div>

    <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
      <UCard class="max-w-md w-full text-center p-8">
        <Icon name="ph:warning-duotone" size="64" class="text-error mb-4 mx-auto" />
        <h2 class="text-xl font-bold mb-2">Ошибка загрузки</h2>
        <p class="text-muted mb-6">Не удалось получить данные пользователя для редактирования.</p>
        <UButton variant="primary" @click="refresh">Повторить попытку</UButton>
      </UCard>
    </div>

    <div v-else-if="user" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Sidebar Panel -->
        <aside class="lg:col-span-4 space-y-6">
          <UCard>
            <div class="flex flex-col items-center text-center py-6">
              <div class="profile-avatar mb-4">
                <span v-if="userInitials">{{ userInitials }}</span>
                <Icon v-else name="ph:user-circle-fill" size="96" />
              </div>
              <h2 class="text-xl font-bold truncate w-full px-2 text-text mb-1">
                {{ user.full_name || 'Без имени' }}
              </h2>
              <p class="text-muted text-sm truncate w-full px-2 mb-4">{{ user.email }}</p>
              
              <div class="flex flex-wrap justify-center gap-2">
                <UBadge variant="accent" size="sm" class="uppercase font-bold tracking-wider">
                  {{ user.role }}
                </UBadge>
                <UBadge :variant="user.is_active ? 'success' : 'error'" size="sm">
                  {{ user.is_active ? 'Активен' : 'Блокирован' }}
                </UBadge>
              </div>
            </div>
            
            <div class="profile-stats border-t border-border pt-6 mt-2 space-y-3">
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">ID:</span>
                <span class="font-mono text-xs text-text">{{ user.id }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-muted">Регистрация:</span>
                <span class="text-text">{{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </UCard>

          <UCard>
            <template #header>
              <div class="flex items-center gap-2">
                <Icon name="ph:info-bold" class="text-warning" />
                <span class="font-bold text-xs uppercase tracking-widest">Подсказка</span>
              </div>
            </template>
            <p class="text-sm text-muted">
              Изменения в основной информации применяются ко всему аккаунту. 
              Для управления адресами используйте кнопки в соответствующем разделе.
            </p>
          </UCard>
        </aside>

        <!-- Main Content Area -->
        <main class="lg:col-span-8 space-y-6">
          <!-- General Information Form -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2">
                <Icon name="ph:user-gear-bold" class="text-accent" size="20" />
                <h2 class="font-bold uppercase tracking-wider text-sm">Основная информация</h2>
              </div>
            </template>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <UInput 
                v-model="generalForm.full_name" 
                label="Полное имя" 
                placeholder="Иван Иванов" 
                data-testid="edit-name-input" 
              />
              <UInput 
                v-model="generalForm.email" 
                label="Email (Логин)" 
                type="email"
                placeholder="user@example.com" 
                required 
                data-testid="edit-email-input" 
              />
              <UInput 
                v-model="generalForm.phone" 
                label="Телефон" 
                placeholder="+7 999 000 00 00" 
                data-testid="edit-phone-input" 
              />
              <USelect 
                v-model="generalForm.role" 
                label="Роль пользователя" 
                :options="roleOptions" 
                data-testid="edit-role-select" 
              />
              
              <div class="md:col-span-2 flex items-center justify-between p-4 bg-surface-2 rounded-xl border border-border mt-2">
                <div class="flex flex-col">
                  <span class="font-bold text-sm">Активный аккаунт</span>
                  <span class="text-xs text-muted">Позволяет пользователю входить в систему</span>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input 
                    v-model="generalForm.is_active" 
                    type="checkbox" 
                    class="sr-only peer" 
                    data-testid="edit-active-toggle"
                  >
                  <div class="w-11 h-6 bg-surface-3 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                </label>
              </div>
            </div>

            <template #footer>
              <div class="flex justify-end gap-3">
                <UButton variant="ghost" :to="`/admin/users/${userId}`">Отмена</UButton>
                <UButton 
                  variant="primary" 
                  :loading="isSavingGeneral" 
                  @click="handleSaveGeneral"
                  data-testid="save-general-btn"
                >
                  Сохранить изменения
                </UButton>
              </div>
            </template>
          </UCard>

          <!-- Addresses Management -->
          <UCard>
            <template #header>
              <div class="flex items-center justify-between w-full">
                <div class="flex items-center gap-2">
                  <Icon name="ph:map-pin-line-bold" class="text-info" size="20" />
                  <h2 class="font-bold uppercase tracking-wider text-sm">Адреса доставки</h2>
                </div>
                <UButton variant="outline" size="sm" @click="openAddAddress" data-testid="add-address-btn">
                  <template #icon><Icon name="ph:plus-bold" /></template>
                  Добавить
                </UButton>
              </div>
            </template>

            <div v-if="user.addresses.length === 0" class="empty-state">
              <Icon name="ph:map-trifold-light" size="48" class="text-muted mb-2" />
              <p class="text-muted text-sm">У пользователя нет сохраненных адресов</p>
            </div>

            <div v-else class="space-y-3 pt-2">
              <div v-for="addr in user.addresses" :key="addr.id" class="address-item-row p-4 rounded-lg bg-surface-2 border border-border">
                <div class="flex flex-col sm:flex-row justify-between gap-4">
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="font-bold text-text">{{ addr.name }}</span>
                      <UBadge v-if="addr.is_default" variant="success" size="sm">Основной</UBadge>
                    </div>
                    <p class="text-sm text-text-2">{{ addr.full_address }}, {{ addr.city }}</p>
                    <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted pt-1">
                      <span><span class="opacity-50">Получатель:</span> {{ addr.recipient_name }}</span>
                      <span><span class="opacity-50">Тел:</span> {{ addr.recipient_phone }}</span>
                      <span><span class="opacity-50">Тип:</span> {{ addr.address_type }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 self-end sm:self-center">
                    <UButton variant="ghost" size="sm" @click="openEditAddress(addr)" :data-testid="`edit-address-${addr.id}`">
                      <template #icon><Icon name="ph:pencil-simple" size="18" /></template>
                    </UButton>
                    <UButton variant="ghost" size="sm" class="text-error" @click="handleDeleteAddress(addr.id)" :data-testid="`delete-address-${addr.id}`">
                      <template #icon><Icon name="ph:trash" size="18" /></template>
                    </UButton>
                  </div>
                </div>
              </div>
            </div>
          </UCard>
        </main>
      </div>
    </div>

    <!-- Address Modal -->
    <UModal 
      v-model="isAddressModalOpen" 
      :title="editingAddressId ? 'Редактировать адрес' : 'Добавить новый адрес'"
      data-testid="address-modal"
    >
      <div class="space-y-4 pt-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UInput v-model="addressForm.name" label="Название адреса" placeholder="Дом, Офис и т.д." required data-testid="addr-name" />
          <USelect v-model="addressForm.address_type" label="Тип адреса" :options="addressTypeOptions" data-testid="addr-type" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UInput v-model="addressForm.recipient_name" label="Имя получателя" placeholder="Имя Фамилия" required data-testid="addr-recipient" />
          <UInput v-model="addressForm.recipient_phone" label="Телефон получателя" placeholder="+7..." required data-testid="addr-phone" />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="sm:col-span-2">
            <UInput v-model="addressForm.city" label="Город" placeholder="Москва" required data-testid="addr-city" />
          </div>
          <UInput v-model="addressForm.postal_code" label="Почтовый индекс" placeholder="123456" data-testid="addr-zip" />
        </div>

        <UInput v-model="addressForm.full_address" label="Полный адрес" placeholder="ул. Ленина, д. 1, кв. 1" required data-testid="addr-full" />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <USelect v-model="addressForm.provider" label="Служба доставки" :options="providerOptions" data-testid="addr-provider" />
          <UInput v-model="addressForm.pickup_point_code" label="Код пункта выдачи (если есть)" placeholder="MSK1" data-testid="addr-pickup-code" />
        </div>

        <div class="flex items-center gap-3 p-3 bg-surface-2 rounded-lg border border-border mt-2">
          <input
            id="addr-default"
            v-model="addressForm.is_default"
            type="checkbox"
            class="w-5 h-5 accent-accent cursor-pointer"
            data-testid="addr-default-toggle"
          />
          <label class="text-sm font-semibold text-text cursor-pointer" for="addr-default">Использовать как адрес по умолчанию</label>
        </div>

        <div class="flex flex-col gap-3 mt-8 sm:flex-row sm:justify-end">
          <UButton variant="ghost" @click="isAddressModalOpen = false">Отмена</UButton>
          <UButton 
            variant="primary" 
            :loading="isSavingAddress" 
            @click="handleSaveAddress"
            data-testid="confirm-save-address"
          >
            {{ editingAddressId ? 'Обновить адрес' : 'Добавить адрес' }}
          </UButton>
        </div>
      </div>
    </UModal>
  </NuxtLayout>
</template>

<style scoped>
.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: var(--radius-full);
  background: var(--color-surface-2);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 800;
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.empty-state {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  text-align: center;
}

.address-item-row {
  transition: all var(--transition-fast);
}

.address-item-row:hover {
  border-color: var(--color-accent-glow);
  background: var(--color-surface-3);
}

/* Custom Toggle Switch for General Info */
.peer-checked\:bg-accent:checked ~ div {
  background-color: var(--color-accent);
}
</style>
