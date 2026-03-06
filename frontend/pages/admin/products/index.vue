<script setup lang="ts">
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'
import { useProducts } from '~/composables/useProducts'
import { useToast } from '~/composables/useToast'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const { adminGetProducts, deleteProduct } = useProducts()
const { data: products, pending, refresh } = await adminGetProducts()

const toast = useToast()

const searchQuery = ref('')
const filteredProducts = computed(() => {
  if (!products.value?.items) return []
  if (!searchQuery.value.trim()) return products.value.items
  const q = searchQuery.value.toLowerCase()
  return products.value.items.filter((p: any) =>
    p.name?.toLowerCase().includes(q) || p.sku?.toLowerCase().includes(q)
  )
})

const handleDelete = async (id: string, name: string) => {
  if (!confirm(`Удалить товар «${name}»? Это действие нельзя отменить.`)) return
  try {
    await deleteProduct(id)
    toast.success('Удалено', `Товар «${name}» удалён`)
    await refresh()
  } catch (err: any) {
    toast.error('Ошибка', err?.data?.detail || 'Не удалось удалить товар')
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Товары</template>
    <template #header-actions>
      <UButton 
        to="/admin/products/create" 
        icon="ph:plus-bold" 
        size="sm"
        data-testid="admin-save-btn"
      >
        <span class="hidden sm:inline">Добавить</span>
        <span class="sm:hidden">Создать</span>
      </UButton>
    </template>

    <div class="products-index-page">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Поиск по названию или SKU..."
          class="search-input"
          data-testid="search-input"
        />
      </div>
      <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table" data-testid="product-list">
          <thead>
            <tr>
              <th>Товар</th>
              <th class="hidden md:table-cell">Категория</th>
              <th class="hidden sm:table-cell">Цена</th>
              <th class="hidden sm:table-cell">Склад</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in filteredProducts" :key="product.id" data-testid="product-card">
              <td>
                <div class="product-cell">
                  <img v-if="product.main_image_url" :src="product.main_image_url" :alt="product.name" width="40" height="40" loading="lazy" />
                  <div v-else class="image-placeholder">
                    <Icon name="ph:package-bold" size="20" />
                  </div>
                  <div class="product-info">
                    <span class="product-name" data-testid="product-title">{{ product.name }}</span>
                    <div class="sm:hidden product-meta">
                      <span>{{ product.price_display }} {{ product.currency }}</span>
                      <span class="dot">·</span>
                      <span :class="product.stock > 0 ? 'text-success' : 'text-error'">
                        {{ product.stock > 0 ? `В наличии: ${product.stock}` : 'Нет на складе' }}
                      </span>
                    </div>
                  </div>
                </div>
              </td>
              <td class="hidden md:table-cell">{{ product.category?.name || '—' }}</td>
              <td class="hidden sm:table-cell" data-testid="product-price">{{ product.price_display }} {{ product.currency }}</td>
              <td class="hidden sm:table-cell" data-testid="product-stock">
                <UBadge :variant="product.stock > 0 ? 'success' : 'danger'">
                  {{ product.stock }}
                </UBadge>
              </td>
              <td>
                <div class="actions">
                  <UButton variant="ghost" size="sm" :to="`/admin/products/${product.id}`" aria-label="Редактировать">
                    <Icon name="ph:pencil-simple-bold" size="18" />
                  </UButton>
                  <UButton variant="ghost" size="sm" color="danger" aria-label="Удалить" data-testid="admin-delete-btn" @click="handleDelete(product.id, product.name)">
                    <Icon name="ph:trash-bold" size="18" />
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>
  </div>
  </NuxtLayout>
</template>

<style scoped>
.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--text-sm);
  outline: none;
  transition: border-color var(--transition-fast);
}

.search-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 20%, transparent);
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 140px;
}

.product-cell img, .image-placeholder {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  flex-shrink: 0;
}

.image-placeholder {
  background: var(--color-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
}

.product-info {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: 500;
  color: var(--color-text);
  font-size: var(--text-sm);
}

.product-meta {
  font-size: var(--text-xs);
  color: var(--color-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-success { color: var(--color-success); }
.text-error { color: var(--color-error); }
.dot { opacity: 0.5; }

.actions {
  display: flex;
  gap: 4px;
}

.hidden { display: none; }
@media (min-width: 640px) {
  .sm\:inline { display: inline; }
  .sm\:hidden { display: none; }
  .sm\:table-cell { display: table-cell; }
  .product-name { font-size: var(--text-base); }
}
@media (min-width: 768px) {
  .md\:table-cell { display: table-cell; }
}

.space-y-4 > * + * { margin-top: 16px; }
</style>
