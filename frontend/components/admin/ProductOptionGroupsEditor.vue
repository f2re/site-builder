<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useProductOptionsStore } from '~/stores/productOptions'
import type { ProductOptionGroup, ProductOptionValue } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'

const props = defineProps<{
  productId: string
  initialGroups?: ProductOptionGroup[]
}>()

const emit = defineEmits<{
  change: [groups: ProductOptionGroup[]]
}>()

const store = useProductOptionsStore()
const toast = useToast()
const { confirm } = useConfirm()

// Initialize store from prop
watch(
  () => props.initialGroups,
  (val) => {
    if (val) {
      store.setGroups(props.productId, val)
    }
  },
  { immediate: true }
)

const groups = computed(() => store.getGroups(props.productId))
const isBusy = computed(() => store.isLoading(props.productId))

// ─── Group forms ──────────────────────────────────────────────────
const isAddingGroup = ref(false)
const editingGroupId = ref<string | null>(null)

const newGroupForm = ref({ name: '', is_required: false, sort_order: 0 })
const editGroupForm = ref<{ name: string; is_required: boolean; sort_order: number }>({
  name: '',
  is_required: false,
  sort_order: 0,
})

const resetNewGroup = () => {
  newGroupForm.value = { name: '', is_required: false, sort_order: groups.value.length }
}

const startAddGroup = () => {
  resetNewGroup()
  isAddingGroup.value = true
}

const cancelAddGroup = () => {
  isAddingGroup.value = false
  resetNewGroup()
}

const handleCreateGroup = async () => {
  if (!newGroupForm.value.name.trim()) {
    toast.warning('Ошибка', 'Введите название группы')
    return
  }
  try {
    await store.createGroup(props.productId, {
      name: newGroupForm.value.name.trim(),
      is_required: newGroupForm.value.is_required,
      sort_order: newGroupForm.value.sort_order,
    })
    toast.success('Готово', 'Группа опций создана')
    isAddingGroup.value = false
    resetNewGroup()
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось создать группу')
  }
}

const startEditGroup = (group: ProductOptionGroup) => {
  editingGroupId.value = group.id
  editGroupForm.value = {
    name: group.name,
    is_required: group.is_required,
    sort_order: group.sort_order,
  }
}

const cancelEditGroup = () => {
  editingGroupId.value = null
}

const handleUpdateGroup = async (groupId: string) => {
  if (!editGroupForm.value.name.trim()) {
    toast.warning('Ошибка', 'Введите название группы')
    return
  }
  try {
    await store.updateGroup(props.productId, groupId, {
      name: editGroupForm.value.name.trim(),
      is_required: editGroupForm.value.is_required,
      sort_order: editGroupForm.value.sort_order,
    })
    toast.success('Готово', 'Группа обновлена')
    editingGroupId.value = null
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось обновить группу')
  }
}

const handleDeleteGroup = async (group: ProductOptionGroup) => {
  const ok = await confirm({
    title: 'Удалить группу?',
    message: `Группа "${group.name}" и все её значения будут удалены безвозвратно.`,
    confirmLabel: 'Удалить',
    variant: 'danger',
  })
  if (!ok) return
  try {
    await store.deleteGroup(props.productId, group.id)
    toast.success('Удалено', 'Группа опций удалена')
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось удалить группу')
  }
}

// ─── Value forms ──────────────────────────────────────────────────
const addingValueToGroup = ref<string | null>(null)
const editingValueId = ref<string | null>(null)

const newValueForm = ref({
  name: '',
  price_modifier: 0,
  is_default: false,
  sort_order: 0,
  sku_suffix: '',
})

const editValueForm = ref({
  name: '',
  price_modifier: 0,
  is_default: false,
  sort_order: 0,
  sku_suffix: '',
})

const resetNewValue = () => {
  newValueForm.value = { name: '', price_modifier: 0, is_default: false, sort_order: 0, sku_suffix: '' }
}

const startAddValue = (groupId: string) => {
  resetNewValue()
  addingValueToGroup.value = groupId
  editingValueId.value = null
}

const cancelAddValue = () => {
  addingValueToGroup.value = null
  resetNewValue()
}

const handleCreateValue = async (groupId: string) => {
  if (!newValueForm.value.name.trim()) {
    toast.warning('Ошибка', 'Введите название значения')
    return
  }
  const group = groups.value.find((g) => g.id === groupId)
  try {
    await store.createValue(props.productId, groupId, {
      name: newValueForm.value.name.trim(),
      price_modifier: Number(newValueForm.value.price_modifier),
      is_default: newValueForm.value.is_default,
      sort_order: group?.values.length ?? 0,
      sku_suffix: newValueForm.value.sku_suffix || null,
    })
    toast.success('Готово', 'Значение добавлено')
    addingValueToGroup.value = null
    resetNewValue()
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось добавить значение')
  }
}

const startEditValue = (val: ProductOptionValue) => {
  editingValueId.value = val.id
  addingValueToGroup.value = null
  editValueForm.value = {
    name: val.name,
    price_modifier: val.price_modifier,
    is_default: val.is_default,
    sort_order: val.sort_order,
    sku_suffix: val.sku_suffix || '',
  }
}

const cancelEditValue = () => {
  editingValueId.value = null
}

const handleUpdateValue = async (groupId: string, valueId: string) => {
  if (!editValueForm.value.name.trim()) {
    toast.warning('Ошибка', 'Введите название значения')
    return
  }
  try {
    await store.updateValue(props.productId, groupId, valueId, {
      name: editValueForm.value.name.trim(),
      price_modifier: Number(editValueForm.value.price_modifier),
      is_default: editValueForm.value.is_default,
      sort_order: editValueForm.value.sort_order,
      sku_suffix: editValueForm.value.sku_suffix || null,
    })
    toast.success('Готово', 'Значение обновлено')
    editingValueId.value = null
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось обновить значение')
  }
}

const handleDeleteValue = async (groupId: string, val: ProductOptionValue) => {
  const ok = await confirm({
    title: 'Удалить значение?',
    message: `Значение "${val.name}" будет удалено.`,
    confirmLabel: 'Удалить',
    variant: 'danger',
  })
  if (!ok) return
  try {
    await store.deleteValue(props.productId, groupId, val.id)
    toast.success('Удалено', 'Значение удалено')
    emit('change', groups.value)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    toast.error('Ошибка', e?.data?.message || 'Не удалось удалить значение')
  }
}

const formatModifier = (mod: number): string => {
  if (mod === 0) return 'Без доплаты'
  return `${mod > 0 ? '+' : ''}${mod.toLocaleString('ru-RU')} ₽`
}
</script>

<template>
  <div class="option-groups-editor" data-testid="option-groups-editor">
    <!-- Loading overlay -->
    <div v-if="isBusy" class="option-groups-editor__loading" aria-live="polite" aria-label="Загрузка">
      <div class="spinner" aria-hidden="true"></div>
      <span>Обновление...</span>
    </div>

    <!-- Groups list -->
    <div class="option-groups-editor__list">
      <div
        v-for="group in groups"
        :key="group.id"
        class="group-card"
        :data-testid="`option-group-card-${group.id}`"
      >
        <!-- Group header -->
        <div class="group-card__header">
          <template v-if="editingGroupId === group.id">
            <!-- Edit group form (inline) -->
            <div class="group-edit-form">
              <input
                v-model="editGroupForm.name"
                class="form-input"
                placeholder="Название группы"
                :data-testid="`group-name-input-${group.id}`"
              />
              <div class="group-edit-form__row">
                <label class="toggle-label">
                  <input
                    v-model="editGroupForm.is_required"
                    type="checkbox"
                    class="toggle-cb"
                    :data-testid="`group-required-toggle-${group.id}`"
                  />
                  <span>Обязательная</span>
                </label>
                <input
                  v-model.number="editGroupForm.sort_order"
                  type="number"
                  class="form-input form-input--narrow"
                  placeholder="Порядок"
                  aria-label="Порядок сортировки"
                  :data-testid="`group-sort-input-${group.id}`"
                />
              </div>
              <div class="group-edit-form__actions">
                <button
                  type="button"
                  class="btn btn--primary btn--sm"
                  :disabled="isBusy"
                  :data-testid="`group-save-btn-${group.id}`"
                  @click="handleUpdateGroup(group.id)"
                >
                  Сохранить
                </button>
                <button
                  type="button"
                  class="btn btn--ghost btn--sm"
                  @click="cancelEditGroup"
                >
                  Отмена
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="group-card__meta">
              <span class="group-card__name">{{ group.name }}</span>
              <span v-if="group.is_required" class="group-card__badge group-card__badge--required">
                Обязательная
              </span>
              <span class="group-card__badge group-card__badge--count">
                {{ group.values.length }} зн.
              </span>
            </div>
            <div class="group-card__actions">
              <button
                type="button"
                class="icon-btn"
                title="Редактировать группу"
                aria-label="Редактировать группу"
                :data-testid="`group-edit-btn-${group.id}`"
                @click="startEditGroup(group)"
              >
                <Icon name="ph:pencil-simple-bold" size="16" aria-hidden="true" />
              </button>
              <button
                type="button"
                class="icon-btn icon-btn--danger"
                title="Удалить группу"
                aria-label="Удалить группу"
                :disabled="isBusy"
                :data-testid="`group-delete-btn-${group.id}`"
                @click="handleDeleteGroup(group)"
              >
                <Icon name="ph:trash-bold" size="16" aria-hidden="true" />
              </button>
            </div>
          </template>
        </div>

        <!-- Values list -->
        <div class="group-card__values">
          <div
            v-for="val in group.values"
            :key="val.id"
            class="value-row"
            :data-testid="`option-value-row-${val.id}`"
          >
            <template v-if="editingValueId === val.id">
              <!-- Edit value form -->
              <div class="value-edit-form">
                <div class="value-edit-form__row">
                  <input
                    v-model="editValueForm.name"
                    class="form-input"
                    placeholder="Название значения"
                    :data-testid="`value-name-input-${val.id}`"
                  />
                  <input
                    v-model.number="editValueForm.price_modifier"
                    type="number"
                    class="form-input form-input--narrow"
                    placeholder="Наценка ₽"
                    aria-label="Наценка"
                    :data-testid="`value-modifier-input-${val.id}`"
                  />
                </div>
                <div class="value-edit-form__row">
                  <input
                    v-model="editValueForm.sku_suffix"
                    class="form-input"
                    placeholder="Суффикс SKU (опционально)"
                    aria-label="Суффикс SKU"
                    :data-testid="`value-sku-input-${val.id}`"
                  />
                  <label class="toggle-label">
                    <input
                      v-model="editValueForm.is_default"
                      type="checkbox"
                      class="toggle-cb"
                      :data-testid="`value-default-toggle-${val.id}`"
                    />
                    <span>По умолчанию</span>
                  </label>
                </div>
                <div class="value-edit-form__actions">
                  <button
                    type="button"
                    class="btn btn--primary btn--sm"
                    :disabled="isBusy"
                    :data-testid="`value-save-btn-${val.id}`"
                    @click="handleUpdateValue(group.id, val.id)"
                  >
                    Сохранить
                  </button>
                  <button
                    type="button"
                    class="btn btn--ghost btn--sm"
                    @click="cancelEditValue"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="value-row__info">
                <span class="value-row__name">{{ val.name }}</span>
                <span
                  class="value-row__modifier"
                  :class="{
                    'is-positive': val.price_modifier > 0,
                    'is-negative': val.price_modifier < 0,
                  }"
                >
                  {{ formatModifier(val.price_modifier) }}
                </span>
                <span v-if="val.is_default" class="value-row__badge value-row__badge--default">
                  Дефолт
                </span>
                <span v-if="val.sku_suffix" class="value-row__badge">
                  SKU: {{ val.sku_suffix }}
                </span>
              </div>
              <div class="value-row__actions">
                <button
                  type="button"
                  class="icon-btn"
                  title="Редактировать"
                  aria-label="Редактировать значение"
                  :data-testid="`value-edit-btn-${val.id}`"
                  @click="startEditValue(val)"
                >
                  <Icon name="ph:pencil-simple-bold" size="14" aria-hidden="true" />
                </button>
                <button
                  type="button"
                  class="icon-btn icon-btn--danger"
                  title="Удалить"
                  aria-label="Удалить значение"
                  :disabled="isBusy"
                  :data-testid="`value-delete-btn-${val.id}`"
                  @click="handleDeleteValue(group.id, val)"
                >
                  <Icon name="ph:x-bold" size="14" aria-hidden="true" />
                </button>
              </div>
            </template>
          </div>

          <!-- Add value form -->
          <div v-if="addingValueToGroup === group.id" class="add-value-form">
            <div class="add-value-form__row">
              <input
                v-model="newValueForm.name"
                class="form-input"
                placeholder="Название значения"
                data-testid="new-value-name-input"
              />
              <input
                v-model.number="newValueForm.price_modifier"
                type="number"
                class="form-input form-input--narrow"
                placeholder="Наценка ₽"
                aria-label="Наценка"
                data-testid="new-value-modifier-input"
              />
            </div>
            <div class="add-value-form__row">
              <input
                v-model="newValueForm.sku_suffix"
                class="form-input"
                placeholder="Суффикс SKU (опционально)"
                aria-label="Суффикс SKU"
                data-testid="new-value-sku-input"
              />
              <label class="toggle-label">
                <input
                  v-model="newValueForm.is_default"
                  type="checkbox"
                  class="toggle-cb"
                  data-testid="new-value-default-toggle"
                />
                <span>По умолчанию</span>
              </label>
            </div>
            <div class="add-value-form__actions">
              <button
                type="button"
                class="btn btn--primary btn--sm"
                :disabled="isBusy"
                data-testid="new-value-submit-btn"
                @click="handleCreateValue(group.id)"
              >
                Добавить
              </button>
              <button
                type="button"
                class="btn btn--ghost btn--sm"
                @click="cancelAddValue"
              >
                Отмена
              </button>
            </div>
          </div>

          <!-- Add value button -->
          <button
            v-if="addingValueToGroup !== group.id"
            type="button"
            class="add-inline-btn"
            :data-testid="`add-value-btn-${group.id}`"
            @click="startAddValue(group.id)"
          >
            <Icon name="ph:plus-bold" size="14" aria-hidden="true" />
            Добавить значение
          </button>
        </div>
      </div>
    </div>

    <!-- No groups placeholder -->
    <div v-if="groups.length === 0 && !isAddingGroup" class="option-groups-editor__empty">
      <Icon name="ph:sliders-horizontal-bold" size="32" aria-hidden="true" />
      <p>Нет групп опций. Добавьте первую группу.</p>
    </div>

    <!-- Add group form -->
    <div v-if="isAddingGroup" class="add-group-form">
      <h4 class="add-group-form__title">Новая группа опций</h4>
      <input
        v-model="newGroupForm.name"
        class="form-input"
        placeholder="Название группы (напр. «Длина кабеля»)"
        data-testid="new-group-name-input"
      />
      <div class="add-group-form__row">
        <label class="toggle-label">
          <input
            v-model="newGroupForm.is_required"
            type="checkbox"
            class="toggle-cb"
            data-testid="new-group-required-toggle"
          />
          <span>Обязательная для заказа</span>
        </label>
        <input
          v-model.number="newGroupForm.sort_order"
          type="number"
          class="form-input form-input--narrow"
          placeholder="Порядок"
          aria-label="Порядок сортировки"
          data-testid="new-group-sort-input"
        />
      </div>
      <div class="add-group-form__actions">
        <button
          type="button"
          class="btn btn--primary"
          :disabled="isBusy"
          data-testid="new-group-submit-btn"
          @click="handleCreateGroup"
        >
          Создать группу
        </button>
        <button
          type="button"
          class="btn btn--ghost"
          @click="cancelAddGroup"
        >
          Отмена
        </button>
      </div>
    </div>

    <!-- Add group button -->
    <button
      v-if="!isAddingGroup"
      type="button"
      class="add-group-btn"
      data-testid="add-group-btn"
      @click="startAddGroup"
    >
      <Icon name="ph:plus-circle-bold" size="18" aria-hidden="true" />
      Добавить группу опций
    </button>
  </div>
</template>

<style scoped>
.option-groups-editor {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Loading overlay */
.option-groups-editor__loading {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  z-index: 10;
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.option-groups-editor__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-groups-editor__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 32px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-muted);
  text-align: center;
  font-size: var(--text-sm);
}

/* Group card */
.group-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface-2);
}

.group-card__header {
  padding: 12px 16px;
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: space-between;
  min-height: 48px;
}

.group-card__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.group-card__name {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
}

.group-card__badge {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--color-surface-3);
  color: var(--color-muted);
}

.group-card__badge--required {
  background: rgba(230, 57, 70, 0.12);
  color: var(--color-error);
}

.group-card__badge--count {
  background: var(--color-surface-3);
  color: var(--color-muted);
}

.group-card__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* Values section */
.group-card__values {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  gap: 8px;
  min-height: 44px;
}

.value-row__info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.value-row__name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text);
}

.value-row__modifier {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--color-muted);
}

.value-row__modifier.is-positive { color: var(--color-success); }
.value-row__modifier.is-negative { color: var(--color-error); }

.value-row__badge {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  background: var(--color-surface-3);
  color: var(--color-muted);
}

.value-row__badge--default {
  background: rgba(0, 245, 212, 0.12);
  color: var(--color-neon);
}

.value-row__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* Icon buttons */
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  border-color: var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}

.icon-btn--danger:hover {
  border-color: var(--color-error);
  background: rgba(230, 57, 70, 0.08);
  color: var(--color-error);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Form inputs */
.form-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  min-height: 44px;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.form-input--narrow {
  width: 100px;
  flex-shrink: 0;
}

/* Toggle label */
.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  color: var(--color-text-2);
  cursor: pointer;
  white-space: nowrap;
  user-select: none;
}

.toggle-cb {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
  cursor: pointer;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
  padding: 10px 18px;
  font-size: var(--text-sm);
  white-space: nowrap;
  min-height: 44px;
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow-accent);
}

.btn--ghost {
  background: transparent;
  border-color: var(--color-border);
  color: var(--color-text-2);
}

.btn--ghost:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn--sm {
  padding: 6px 14px;
  font-size: var(--text-xs);
  min-height: 36px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Group edit form */
.group-edit-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-edit-form__row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.group-edit-form__actions {
  display: flex;
  gap: 8px;
}

/* Value edit form */
.value-edit-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
}

.value-edit-form__row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.value-edit-form__actions {
  display: flex;
  gap: 8px;
}

/* Add value form */
.add-value-form {
  padding: 12px;
  background: var(--color-bg-subtle);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.add-value-form__row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.add-value-form__actions {
  display: flex;
  gap: 8px;
}

/* Add value inline button */
.add-inline-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.add-inline-btn:hover {
  background: var(--color-accent-glow);
}

/* Add group form */
.add-group-form {
  padding: 20px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--color-surface-2);
}

.add-group-form__title {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
}

.add-group-form__row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.add-group-form__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Add group button */
.add-group-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-accent);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  font-family: var(--font-sans);
  transition: all var(--transition-fast);
  width: 100%;
  justify-content: center;
  min-height: 44px;
}

.add-group-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
}

/* Responsive */
@media (max-width: 480px) {
  .group-edit-form__row,
  .add-value-form__row,
  .value-edit-form__row {
    flex-direction: column;
    align-items: stretch;
  }

  .form-input--narrow {
    width: 100%;
  }
}
</style>
