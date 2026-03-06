<script setup lang="ts">
import UButton from '~/components/U/UButton.vue'
import UCard from '~/components/U/UCard.vue'
import UBadge from '~/components/U/UBadge.vue'
import USkeleton from '~/components/U/USkeleton.vue'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const config = useRuntimeConfig()
const { data: products, pending, refresh } = await useFetch('/products', {
  baseURL: config.public.apiBase,
})
</script>

<template>
  <div class="products-index-page">
    <div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-xl font-bold">Товары</h1>
      <UButton to="/admin/products/create" icon="ph:plus-bold">Добавить товар</UButton>
    </div>

    <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <div v-else class="admin-table-wrapper">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Товар</th>
              <th>Категория</th>
              <th>Цена</th>
              <th>Склад</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products?.items" :key="product.id">
              <td>
                <div class="product-cell">
                  <img v-if="product.images?.length" :src="product.images[0]" :alt="product.name" width="40" height="40" />
                  <div v-else class="image-placeholder">
                    <Icon name="ph:package-bold" size="20" />
                  </div>
                  <span>{{ product.name }}</span>
                </div>
              </td>
              <td>{{ product.category?.name || '—' }}</td>
              <td>{{ product.price_display }} {{ product.currency }}</td>
              <td>
                <UBadge :variant="product.stock > 0 ? 'success' : 'danger'">
                  {{ product.stock }}
                </UBadge>
              </td>
              <td>
                <div class="actions">
                  <UButton variant="ghost" size="sm" :to="`/admin/products/${product.id}`">
                    <Icon name="ph:pencil-simple-bold" />
                  </UButton>
                  <UButton variant="ghost" size="sm" color="danger">
                    <Icon name="ph:trash-bold" />
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>
  </div>
</template>

<style scoped>
/* Local overrides for specific cells */
.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
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

.actions {
  display: flex;
  gap: 4px;
}

.space-y-4 > * + * { margin-top: 16px; }
</style>
