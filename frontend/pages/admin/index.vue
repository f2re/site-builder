<script setup lang="ts">
definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const { data: stats, pending } = await useApi<any>('/admin/stats')

const statCards = computed(() => [
  { 
    label: 'Выручка', 
    value: stats.value?.revenue_rub ? `${stats.value.revenue_rub.toLocaleString()} ₽` : '0 ₽',
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
  <NuxtLayout name="admin">
    <template #header-title>
      Панель управления
    </template>

    <div class="admin-dashboard">
      <div class="dashboard-section">
        <div v-if="pending" class="stats-grid">
          <USkeleton v-for="i in 3" :key="i" height="110px" />
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
      </div>

      <div class="dashboard-grid">
        <!-- Chart Widget (Placeholder) -->
        <div class="dashboard-section">
          <h2 class="section-title">Аналитика продаж</h2>
          <UCard class="chart-card">
            <div class="chart-placeholder">
              <Icon name="ph:chart-bar-bold" size="48" class="placeholder-icon" />
              <p>График продаж будет доступен после накопления данных</p>
            </div>
          </UCard>
        </div>

        <!-- Recent Orders Widget -->
        <div class="dashboard-section">
          <h2 class="section-title">Последние заказы</h2>
          <UCard>
            <div class="empty-state">
              <Icon name="ph:shopping-bag-open-bold" size="32" />
              <p>Здесь появится список последних заказов</p>
              <UButton to="/admin/orders" variant="ghost" size="sm" class="mt-4">
                Перейти к заказам
              </UButton>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }
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
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-2);
  font-weight: 500;
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  line-height: 1;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

@media (min-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 2fr 1fr;
    gap: 24px;
  }
}

.chart-card {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  color: var(--color-muted);
  gap: 12px;
}

.placeholder-icon {
  opacity: 0.2;
}

.mt-4 {
  margin-top: 16px;
}
</style>
