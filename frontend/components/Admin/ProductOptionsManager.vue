<script setup lang="ts">
import { ref } from 'vue'
import { useProducts, type ProductOptionGroup, type ProductOptionValue } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import { useConfirm } from '~/composables/useConfirm'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'

const props = defineProps<{
  productId: string
  modelValue: ProductOptionGroup[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: ProductOptionGroup[]]
  'refresh': []
}>()

const { 
  adminCreateOptionGroup, 
  adminUpdateOptionGroup, 
  adminDeleteOptionGroup,
  adminCreateOptionValue,
  adminUpdateOptionValue,
  adminDeleteOptionValue
} = useProducts()

const toast = useToast()
const { confirm } = useConfirm()

const isAddingGroup = ref(false)
const newGroupName = ref('')

const handleAddGroup = async () => {
  if (!newGroupName.value.trim()) return
  
  try {
    await adminCreateOptionGroup(props.productId, {
      name: newGroupName.value.trim(),
      is_required: false,
      sort_order: props.modelValue.length
    })
    newGroupName.value = ''
    isAddingGroup.value = false
    emit('refresh')
    toast.success('Успех', 'Группа опций добавлена')
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось добавить группу')
  }
}

const handleDeleteGroup = async (group: ProductOptionGroup) => {
  if (!await confirm({ 
    title: 'Удалить группу?', 
    message: `Вы уверены, что хотите удалить группу "${group.name}" и все её значения?`,
    confirmLabel: 'Удалить',
    variant: 'danger'
  })) return

  try {
    await adminDeleteOptionGroup(group.id)
    emit('refresh')
    toast.success('Удалено', 'Группа опций удалена')
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось удалить группу')
  }
}

// Option Values management
const addingValueToGroupId = ref<string | null>(null)
const newValueName = ref('')
const newValueModifier = ref(0)

const handleAddValue = async (groupId: string) => {
  if (!newValueName.value.trim()) return
  
  try {
    await adminCreateOptionValue(groupId, {
      name: newValueName.value.trim(),
      price_modifier: newValueModifier.value,
      is_default: false,
      sort_order: 0
    })
    newValueName.value = ''
    newValueModifier.value = 0
    addingValueToGroupId.value = null
    emit('refresh')
    toast.success('Успех', 'Значение добавлено')
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось добавить значение')
  }
}

const handleDeleteValue = async (value: ProductOptionValue) => {
  try {
    await adminDeleteOptionValue(value.id)
    emit('refresh')
    toast.success('Удалено', 'Значение удалено')
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось удалить значение')
  }
}

const toggleRequired = async (group: ProductOptionGroup) => {
  try {
    await adminUpdateOptionGroup(group.id, { is_required: !group.is_required })
    emit('refresh')
  } catch (err: any) {
    toast.error('Ошибка', 'Не удалось обновить статус')
  }
}
</script>

<template>
  <div class="options-manager">
    <div v-for="group in modelValue" :key="group.id" class="group-item">
      <div class="group-header">
        <div class="group-info">
          <h4 class="group-name">{{ group.name }}</h4>
          <label class="required-toggle">
            <input type="checkbox" :checked="group.is_required" @change="toggleRequired(group)" />
            <span>Обязательная</span>
          </label>
        </div>
        <UButton 
          variant="ghost" 
          color="danger" 
          icon="ph:trash-bold" 
          size="xs" 
          @click="handleDeleteGroup(group)"
        />
      </div>

      <div class="values-list">
        <div v-for="val in group.values" :key="val.id" class="value-item">
          <div class="value-main">
            <span class="value-name">{{ val.name }}</span>
            <span class="value-price" :class="{ 'is-positive': val.price_modifier > 0, 'is-negative': val.price_modifier < 0 }">
              {{ val.price_modifier > 0 ? '+' : '' }}{{ val.price_modifier }} ₽
            </span>
          </div>
          <UButton 
            variant="ghost" 
            color="danger" 
            icon="ph:x-bold" 
            size="xs" 
            @click="handleDeleteValue(val)"
          />
        </div>

        <!-- Add Value Form -->
        <div v-if="addingValueToGroupId === group.id" class="add-value-form">
          <UInput v-model="newValueName" placeholder="Название (напр. '2 метра')" size="sm" />
          <UInput v-model.number="newValueModifier" type="number" placeholder="Наценка" size="sm" />
          <div class="flex gap-2">
            <UButton variant="primary" size="sm" @click="handleAddValue(group.id)">ОК</UButton>
            <UButton variant="ghost" size="sm" @click="addingValueToGroupId = null">Отмена</UButton>
          </div>
        </div>
        <UButton 
          v-else 
          variant="ghost" 
          icon="ph:plus-bold" 
          size="sm" 
          class="add-value-btn"
          @click="addingValueToGroupId = group.id"
        >
          Добавить значение
        </UButton>
      </div>
    </div>

    <!-- Add Group -->
    <div v-if="isAddingGroup" class="add-group-form">
      <UInput v-model="newGroupName" placeholder="Название группы (напр. 'Длина кабеля')" />
      <div class="flex gap-2 mt-2">
        <UButton variant="primary" @click="handleAddGroup">Создать группу</UButton>
        <UButton variant="ghost" @click="isAddingGroup = false">Отмена</UButton>
      </div>
    </div>
    <UButton v-else variant="ghost" icon="ph:plus-circle-bold" @click="isAddingGroup = true">
      Добавить группу опций
    </UButton>
  </div>
</template>

<style scoped>
.options-manager {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.group-item {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface-2);
}

.group-header {
  padding: 12px 16px;
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.group-name {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
}

.required-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-muted);
  cursor: pointer;
}

.values-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.value-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.value-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.value-name {
  font-size: var(--text-sm);
  font-weight: 500;
}

.value-price {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--color-muted);
}

.value-price.is-positive { color: var(--color-success); }
.value-price.is-negative { color: var(--color-error); }

.add-value-form {
  padding: 12px;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.add-value-btn {
  justify-content: flex-start;
  color: var(--color-accent);
}

.add-group-form {
  padding: 16px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
}

.flex { display: flex; }
.gap-2 { gap: 0.5rem; }
.mt-2 { margin-top: 0.5rem; }
</style>
