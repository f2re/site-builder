<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProducts, type ProductCreate } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'
import UButton from '~/components/U/UButton.vue'
import UInput from '~/components/U/UInput.vue'
import UCard from '~/components/U/UCard.vue'
import USelect from '~/components/U/USelect.vue'
import UTextarea from '~/components/U/UTextarea.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import TipTapEditor from '~/components/blog/TipTapEditor.vue'
import ProductMediaManager from '~/components/Admin/ProductMediaManager.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { adminGetCategories, adminGetProductById, updateProduct, deleteProduct } = useProducts()

const productId = route.params.id as string

const { data: categoriesData } = await adminGetCategories()
const categoryOptions = computed(() => {
  const base = (categoriesData.value || []).map(c => ({ id: c.id, name: c.name }))
  return [{ id: null, name: 'Без категории' }, ...base]
})

const { data: product, pending, error } = await adminGetProductById(productId)

const form = ref<Partial<ProductCreate>>({})

// Initialize form when product data is loaded
watch(product, (newVal) => {
  if (newVal) {
    form.value = {
      name: newVal.name,
      slug: newVal.slug,
      category_id: newVal.category_id || null,
      description: newVal.description,
      content_json: newVal.content_json,
      is_active: newVal.is_active,
      is_featured: newVal.is_featured,
      meta_title: newVal.meta_title,
      meta_description: newVal.meta_description,
      images: newVal.images.map(img => ({
        url: img.url,
        alt: img.alt,
        is_cover: img.is_cover,
        sort_order: img.sort_order
      })),
      variants: newVal.variants.map(v => ({
        name: v.name,
        sku: v.sku,
        price: v.price,
        stock_quantity: v.stock_quantity,
        attributes: v.attributes
      }))
    }
  }
}, { immediate: true })

const isPending = ref(false)

const handleUpdate = async () => {
  isPending.value = true
  try {
    const payload = { ...form.value }
    if (payload.category_id === '') payload.category_id = null
    
    await updateProduct(productId, payload)
    toast.success('Успех', 'Товар успешно обновлен')
  } catch (err: any) {
    console.error('Error updating product:', err)
    toast.error('Ошибка', err.data?.message || 'Не удалось обновить товар')
  } finally {
    isPending.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Вы уверены, что хотите удалить этот товар?')) return

  try {
    await deleteProduct(productId)
    toast.success('Успех', 'Товар удален')
    router.push('/admin/products')
  } catch (err: any) {
    toast.error('Ошибка', err.data?.message || 'Не удалось удалить товар')
  }
}
</script>

<template>
  <div class="product-edit-page">
    <div v-if="pending" class="space-y-6">
      <USkeleton height="40px" width="300px" />
      <div class="grid gap-6 lg:grid-cols-3">
        <div class="lg:col-span-2 space-y-6">
          <USkeleton height="400px" />
          <USkeleton height="200px" />
        </div>
        <USkeleton height="300px" />
      </div>
    </div>

    <div v-else-if="error" class="error-state">
      <Icon name="ph:warning-bold" size="48" />
      <p>Ошибка при загрузке товара</p>
      <UButton to="/admin/products" variant="ghost">Вернуться к списку</UButton>
    </div>

    <template v-else>
      <div class="mb-6 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <UButton variant="ghost" to="/admin/products" icon="ph:arrow-left-bold" />
          <h1 class="text-2xl font-bold">Редактирование: {{ product?.name }}</h1>
        </div>
        <div class="flex gap-3">
          <UButton 
            variant="ghost" 
            color="danger"
            icon="ph:trash-bold"
            @click="handleDelete"
          >
            Удалить
          </UButton>
          <UButton 
            variant="primary" 
            :loading="isPending"
            icon="ph:floppy-disk-bold"
            @click="handleUpdate"
          >
            Сохранить
          </UButton>
        </div>
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
                label="Краткое описание" 
                placeholder="Краткое описание товара (для карточки)"
                rows="2"
              />
            </div>
          </UCard>

          <UCard title="Изображения">
            <ProductMediaManager v-model="form.images" />
          </UCard>

          <UCard title="Полное описание (Rich Text)">
            <TipTapEditor v-model="form.content_json" placeholder="Расскажите о товаре подробно..." />
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
          
          <UCard title="Инфо">
            <div class="space-y-2 text-xs text-muted">
              <div class="flex justify-between">
                <span>ID:</span>
                <span class="font-mono">{{ product?.id }}</span>
              </div>
              <div class="flex justify-between">
                <span>Создан:</span>
                <span>{{ product?.created_at ? new Date(product.created_at).toLocaleString('ru-RU') : '—' }}</span>
              </div>
              <div class="flex justify-between">
                <span>Обновлен:</span>
                <span>{{ product?.updated_at ? new Date(product.updated_at).toLocaleString('ru-RU') : '—' }}</span>
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </template>
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

.space-y-2 > * + * { margin-top: 0.5rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }
.grid { display: grid; }
.gap-3 { gap: 0.75rem; }
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
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.font-medium { font-weight: 500; }
.font-mono { font-family: var(--font-mono); }
.text-muted { color: var(--color-muted); }

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
  gap: 16px;
  color: var(--color-text-2);
}
</style>
