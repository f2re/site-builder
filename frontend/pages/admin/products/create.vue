<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProducts, type ProductCreate } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import USelect from '~/components/U/USelect.vue'
import UTextarea from '~/components/U/UTextarea.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const router = useRouter()
const toast = useToast()
const { adminGetCategories, createProduct } = useProducts()

const { data: categoriesData } = await adminGetCategories()
const categoryOptions = computed(() => 
  (categoriesData.value || []).map(c => ({ id: c.id, name: c.name }))
)

const form = ref<ProductCreate>({
  name: '',
  slug: '',
  category_id: null,
  description: '',
  is_active: true,
  is_featured: false,
  variants: [
    { name: 'По умолчанию', sku: '', price: 0, stock_quantity: 0 }
  ]
})

const isPending = ref(false)

// Slug auto-generation
watch(() => form.value.name, (newName) => {
  if (newName && !form.value.slug) {
    form.value.slug = newName
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim()
  }
})

const handleCreate = async () => {
  if (!form.value.name || !form.value.slug) {
    toast.error('Ошибка заполнения', 'Заполните обязательные поля: Название и Slug')
    return
  }

  isPending.value = true
  try {
    const payload = { ...form.value }
    // If it's an empty string from select, make it null
    if (payload.category_id === '') payload.category_id = null
    
    const product = await createProduct(payload)
    toast.success('Успех', 'Товар успешно создан')
    router.push(`/admin/products/${product.id}`)
  } catch (err: any) {
    console.error('Error creating product:', err)
    toast.error('Ошибка', err.data?.message || 'Не удалось создать товар')
  } finally {
    isPending.value = false
  }
}
</script>

<template>
  <div class="product-create-page">
    <div class="mb-6 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <UButton variant="ghost" to="/admin/products" icon="ph:arrow-left-bold" />
        <h1 class="text-2xl font-bold">Новый товар</h1>
      </div>
      <UButton 
        variant="primary" 
        :loading="isPending"
        icon="ph:floppy-disk-bold"
        @click="handleCreate"
      >
        Сохранить
      </UButton>
    </div>

    <div class="grid gap-6 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-6">
        <UCard title="Основная информация">
          <div class="space-y-4">
            <UInput 
              v-model="form.name" 
              label="Название" 
              placeholder="Введите название товара"
              required
            />
            <UInput 
              v-model="form.slug" 
              label="Slug (URL)" 
              placeholder="nazvanie-tovara"
              required
            />
            <USelect 
              v-model="form.category_id" 
              label="Категория" 
              :options="categoryOptions"
              placeholder="Выберите категорию"
            />
            <UTextarea 
              v-model="form.description" 
              label="Описание" 
              placeholder="Краткое описание товара"
              rows="4"
            />
          </div>
        </UCard>

        <UCard title="Цена и склад">
          <div v-for="(variant, index) in form.variants" :key="index" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <UInput 
                v-model.number="variant.price" 
                type="number" 
                label="Цена" 
                placeholder="0.00"
              />
              <UInput 
                v-model.number="variant.stock_quantity" 
                type="number" 
                label="Количество на складе" 
                placeholder="0"
              />
            </div>
            <UInput 
              v-model="variant.sku" 
              label="Артикул (SKU)" 
              placeholder="SKU-123"
            />
          </div>
        </UCard>
      </div>

      <div class="space-y-6">
        <UCard title="Статус">
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium">Активен</span>
              <input type="checkbox" v-model="form.is_active" class="toggle-switch" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium">Рекомендуемый</span>
              <input type="checkbox" v-model="form.is_featured" class="toggle-switch" />
            </div>
          </div>
        </UCard>

        <UCard title="SEO">
          <div class="space-y-4">
            <UInput 
              v-model="form.meta_title" 
              label="Meta Title" 
              placeholder="SEO Заголовок"
            />
            <UTextarea 
              v-model="form.meta_description" 
              label="Meta Description" 
              placeholder="SEO Описание"
              rows="3"
            />
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toggle-switch {
  width: 44px;
  height: 24px;
  appearance: none;
  background-color: var(--color-surface-3);
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.toggle-switch:checked {
  background-color: var(--color-success);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  left: 2px;
  top: 2px;
  width: 20px;
  height: 20px;
  background-color: #fff;
  border-radius: 50%;
  transition: transform var(--transition-fast);
}

.toggle-switch:checked::after {
  transform: translateX(20px);
}

.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }
.grid { display: grid; }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .lg\:col-span-2 { grid-column: span 2 / span 2; }
}
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.mb-6 { margin-bottom: 1.5rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.font-bold { font-weight: 700; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.font-medium { font-weight: 500; }
</style>
