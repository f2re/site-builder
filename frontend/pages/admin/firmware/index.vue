<script setup lang="ts">
import type { Complectation } from '~/stores/firmwareStore'

definePageMeta({
  middleware: 'auth',
  layout: 'admin'
})

const { 
  fetchGlobalDevices, 
  fetchAllComplectations, 
  importExcel, 
  mergeUsers,
  createComplectation,
  updateComplectation,
  deleteComplectation
} = useFirmware()

const { globalDevices, allComplectations } = storeToRefs(useFirmwareStore())
const toast = useToast()

const isLoading = ref(true)
const isImporting = ref(false)
const isMerging = ref(false)
const isSavingComplectation = ref(false)

// Merge users form
const mergeSource = ref('')
const mergeTarget = ref('')

// Complectation modal
const showComplectationModal = ref(false)
const editingComplectation = ref<Partial<Complectation> | null>(null)

const onImportExcel = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files?.length) return
  
  isImporting.value = true
  try {
    await importExcel(target.files[0])
    toast.success({ title: 'Импорт завершен', message: 'Данные из Excel успешно загружены' })
    await fetchGlobalDevices()
  } catch (err) {
    toast.error({ title: 'Ошибка импорта', message: 'Не удалось загрузить Excel файл' })
  } finally {
    isImporting.value = false
    target.value = ''
  }
}

const onMergeUsers = async () => {
  if (!mergeSource.value || !mergeTarget.value) return
  
  isMerging.value = true
  try {
    await mergeUsers(mergeSource.value, mergeTarget.value)
    toast.success({ title: 'Пользователи объединены', message: 'Все устройства перенесены на целевой аккаунт' })
    mergeSource.value = ''
    mergeTarget.value = ''
  } catch (err) {
    toast.error({ title: 'Ошибка объединения', message: 'Не удалось объединить пользователей' })
  } finally {
    isMerging.value = false
  }
}

const openComplectationModal = (comp: Complectation | null = null) => {
  editingComplectation.value = comp ? { ...comp } : {
    caption: '',
    label: '',
    code: 0,
    simple: true
  }
  showComplectationModal.value = true
}

const onSaveComplectation = async () => {
  if (!editingComplectation.value?.caption || !editingComplectation.value?.label) return
  
  isSavingComplectation.value = true
  try {
    if (editingComplectation.value.id) {
      await updateComplectation(editingComplectation.value.id, editingComplectation.value)
      toast.success({ title: 'Обновлено', message: 'Комплектация успешно обновлена' })
    } else {
      await createComplectation(editingComplectation.value as Omit<Complectation, 'id'>)
      toast.success({ title: 'Создано', message: 'Новая комплектация успешно добавлена' })
    }
    await fetchAllComplectations()
    showComplectationModal.value = false
  } catch (err) {
    toast.error({ title: 'Ошибка сохранения', message: 'Не удалось сохранить комплектацию' })
  } finally {
    isSavingComplectation.value = false
  }
}

const onDeleteComplectation = async (id: string) => {
  if (!confirm('Вы уверены, что хотите удалить эту комплектацию?')) return
  
  try {
    await deleteComplectation(id)
    toast.success({ title: 'Удалено', message: 'Комплектация успешно удалена' })
    await fetchAllComplectations()
  } catch (err) {
    toast.error({ title: 'Ошибка удаления', message: 'Не удалось удалить комплектацию' })
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      fetchGlobalDevices(),
      fetchAllComplectations()
    ])
  } finally {
    isLoading.value = false
  }
})

useSeo({ title: 'Управление прошивками (Admin)' })
</script>

<template>
  <div class="admin-firmware">
    <header class="admin-header">
      <h1 class="admin-title">Управление прошивками и устройствами</h1>
    </header>

    <div class="admin-grid">
      <!-- Import & Tools -->
      <section class="admin-section">
        <UCard>
          <template #header><h3 class="section-title">Инструменты</h3></template>
          
          <div class="tool-group">
            <h4 class="tool-title">Импорт из Excel</h4>
            <p class="tool-desc">Загрузите файл с серийными номерами и привязками.</p>
            <div class="file-upload">
              <input 
                type="file" 
                id="excel-import" 
                accept=".xlsx, .xls" 
                class="hidden-input"
                @change="onImportExcel"
              >
              <UButton 
                as="label" 
                for="excel-import" 
                :loading="isImporting"
                variant="secondary"
                block
              >
                <template #icon><Icon name="ph:file-xls-bold" /></template>
                Выбрать файл
              </UButton>
            </div>
          </div>

          <div class="divider"></div>

          <div class="tool-group">
            <h4 class="tool-title">Объединение пользователей</h4>
            <p class="tool-desc">Перенос устройств с одного email на другой.</p>
            <div class="merge-form">
              <UInput v-model="mergeSource" label="Источник (Email)" placeholder="from@example.com" />
              <UInput v-model="mergeTarget" label="Цель (Email)" placeholder="to@example.com" />
              <UButton 
                variant="danger" 
                :loading="isMerging"
                :disabled="!mergeSource || !mergeTarget"
                @click="onMergeUsers"
                block
              >
                Объединить аккаунты
              </UButton>
            </div>
          </div>
        </UCard>
      </section>

      <!-- Complectations -->
      <section class="admin-section">
        <UCard>
          <template #header>
            <div class="header-with-action">
              <h3 class="section-title">Комплектации</h3>
              <UButton size="sm" @click="openComplectationModal()">
                <template #icon><Icon name="ph:plus-bold" /></template>
                Добавить
              </UButton>
            </div>
          </template>

          <div class="complectations-list">
            <div v-for="comp in allComplectations" :key="comp.id" class="comp-item">
              <div class="comp-info">
                <span class="comp-name">{{ comp.caption }}</span>
                <span class="comp-code">Code: {{ comp.code }}</span>
                <UBadge :variant="comp.simple ? 'secondary' : 'primary'" size="sm">
                  {{ comp.simple ? 'Simple' : 'Final' }} ({{ comp.label }})
                </UBadge>
              </div>
              <div class="comp-actions">
                <UButton variant="ghost" size="sm" @click="openComplectationModal(comp)">
                  <Icon name="ph:pencil-simple-bold" />
                </UButton>
                <UButton variant="ghost" size="sm" class="delete-btn" @click="onDeleteComplectation(comp.id)">
                  <Icon name="ph:trash-bold" />
                </UButton>
              </div>
            </div>
            <div v-if="allComplectations.length === 0" class="empty-list">
              Комплектации не созданы
            </div>
          </div>
        </UCard>
      </section>

      <!-- Global Devices Table -->
      <section class="admin-section full-width">
        <UCard>
          <template #header><h3 class="section-title">Все устройства в системе</h3></template>
          
          <div class="table-container">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Серийный номер</th>
                  <th>Тип</th>
                  <th>Владелец (Email)</th>
                  <th>Дата добавления</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in globalDevices" :key="device.id">
                  <td><code>{{ device.serial }}</code></td>
                  <td>
                    <UBadge :variant="device.type === 'OBD' ? 'accent' : 'neon'" size="sm">
                      {{ device.type }}
                    </UBadge>
                  </td>
                  <td>{{ device.owner_email }}</td>
                  <td>{{ new Date(device.created_at).toLocaleDateString() }}</td>
                  </tr>
                <tr v-if="globalDevices.length === 0">
                  <td colspan="4" class="text-center">Устройства не найдены</td>
                </tr>
              </tbody>
            </table>
          </div>
        </UCard>
      </section>
    </div>

    <!-- Edit Complectation Modal -->
    <UModal 
      v-model="showComplectationModal" 
      :title="editingComplectation?.id ? 'Редактировать комплектацию' : 'Новая комплектация'"
    >
      <div v-if="editingComplectation" class="modal-form">
        <UInput v-model="editingComplectation.caption" label="Название (Caption)" placeholder="Base + CAN" />
        <UInput v-model="editingComplectation.label" label="Системная метка (Label)" placeholder="base_can" />
        <UInput v-model="editingComplectation.code" type="number" label="Код (Bitmask)" />
        <div class="checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="editingComplectation.simple">
            Простая опция (Simple)
          </label>
        </div>
      </div>
      <template #footer>
        <UButton variant="ghost" @click="showComplectationModal = false">Отмена</UButton>
        <UButton :loading="isSavingComplectation" @click="onSaveComplectation">Сохранить</UButton>
      </template>
    </UModal>
  </div>
</template>

<style scoped>
.admin-firmware {
  padding: 24px;
}

.admin-header {
  margin-bottom: 32px;
}

.admin-title {
  font-size: var(--text-2xl);
  font-weight: 800;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.full-width {
  grid-column: 1 / -1;
}

.section-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 700;
}

.header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-group {
  margin-bottom: 24px;
}

.tool-group:last-child { margin-bottom: 0; }

.tool-title {
  font-size: var(--text-base);
  margin-bottom: 4px;
}

.tool-desc {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 16px;
}

.merge-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.divider {
  height: 1px;
  background: var(--color-border);
  margin: 24px 0;
}

.hidden-input {
  display: none;
}

.complectations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comp-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.comp-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.comp-name {
  font-weight: 600;
}

.comp-price {
  color: var(--color-accent);
  font-weight: 700;
}

.comp-actions {
  display: flex;
  gap: 4px;
}

.delete-btn:hover {
  color: var(--color-error);
}

.empty-list {
  text-align: center;
  padding: 24px;
  color: var(--color-muted);
}

.table-container {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  padding: 12px;
  border-bottom: 2px solid var(--color-border);
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.admin-table td {
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}

.admin-table code {
  font-family: var(--font-mono);
  background: var(--color-surface-2);
  padding: 2px 6px;
  border-radius: 4px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: var(--text-sm);
}

.textarea-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-textarea {
  width: 100%;
  min-height: 100px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 12px;
  color: var(--color-text);
  font-family: var(--font-sans);
  resize: vertical;
}

.admin-textarea:focus {
  border-color: var(--color-accent);
  outline: none;
}

@media (max-width: 640px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
