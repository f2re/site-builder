<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { data: stats, pending } = await useApi<any>('/admin/stats')

const statCards = computed(() => [
  { 
    label: 'Выручка', 
    value: stats.value?.revenue_rub ? `${stats.value.revenue_rub} ₽` : '0 ₽',
    icon: 'ph:currency-rub-bold',
    color: 'var(--color-success)'
  },
  { 
    label: 'Заказы', 
    value: stats.value?.orders_count || 0,
    icon: 'ph:shopping-cart-bold',
    color: 'var(--color-info)'
  },
  { 
    label: 'Пользователи', 
    value: stats.value?.users_count || 0,
    icon: 'ph:users-bold',
    color: 'var(--color-accent)'
  },
])
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-xl font-bold">Панель управления</h1>
    </div>

    <div v-if="pending" class="stats-grid">
      <USkeleton v-for="i in 3" :key="i" height="120px" />
    </div>
    
    <div v-else class="stats-grid">
      <UCard v-for="stat in statCards" :key="stat.label" class="stat-card">
        <div class="stat-icon" :style="{ color: stat.color, background: `${stat.color}15` }">
          <Icon :name="stat.icon" size="24" />
        </div>
        <div class="stat-info">
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-value">{{ stat.value }}</span>
        </div>
      </UCard>
    </div>

    <div class="mt-8">
      <h2 class="text-lg font-bold mb-4">Последние заказы</h2>
      <UCard>
        <!-- Table placeholder -->
        <div class="p-8 text-center text-muted">
          Здесь будет список последних заказов
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
}

.mt-8 { margin-top: 32px; }
.mb-4 { margin-bottom: 16px; }
.text-xl { font-size: var(--text-xl); }
.text-lg { font-size: var(--text-lg); }
.font-bold { font-weight: 700; }
.text-muted { color: var(--color-muted); }
.text-center { text-align: center; }
.p-8 { padding: 32px; }
</style>
