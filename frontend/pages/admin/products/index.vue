<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const config = useRuntimeConfig()
const { data: products, pending, refresh } = await useFetch('/api/v1/products', {
  baseURL: config.public.apiBase,
})
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-xl font-bold">Товары</h1>
      <UButton to="/admin/products/create" icon="ph:plus-bold">Добавить товар</UButton>
    </div>

    <UCard class="overflow-hidden">
      <div v-if="pending" class="p-4 space-y-4">
        <USkeleton v-for="i in 5" :key="i" height="40px" />
      </div>
      <table v-else class="admin-table">
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
                <img :src="product.images[0]" :alt="product.name" width="40" height="40" />
                <span>{{ product.name }}</span>
              </div>
            </td>
            <td>{{ product.category.name }}</td>
            <td>{{ product.price_display }} {{ product.currency }}</td>
            <td>
              <UBadge :variant="product.stock > 0 ? 'success' : 'danger'">
                {{ product.stock }}
              </UBadge>
            </td>
            <td>
              <div class="actions">
                <UButton variant="ghost" size="sm" :to="`/admin/products/${product.slug}`">
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
    </UCard>
  </div>
</template>

<style scoped>
.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  padding: 12px 16px;
  background: var(--color-surface-2);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-2);
  border-bottom: 1px solid var(--color-border);
}

.admin-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-cell img {
  border-radius: var(--radius-sm);
  object-fit: cover;
}

.actions {
  display: flex;
  gap: 4px;
}

.overflow-hidden { overflow: hidden; }
.space-y-4 > * + * { margin-top: 16px; }
.p-4 { padding: 16px; }
</style>
