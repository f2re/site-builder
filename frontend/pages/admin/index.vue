<script setup lang="ts">
import AdminAttentionStats from '~/components/Admin/AdminAttentionStats.vue'
import AdminSalesChart from '~/components/Admin/AdminSalesChart.vue'
import AdminRecentOrders from '~/components/Admin/AdminRecentOrders.vue'
import UCard from '~/components/U/UCard.vue'
import USkeleton from '~/components/U/USkeleton.vue'

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
    color: 'var(--color-success)',
    dataTestId: 'stat-revenue'
  },
  { 
    label: 'Заказы', 
    value: stats.value?.orders_count || 0,
    icon: 'ph:shopping-cart-bold',
    color: 'var(--color-info)',
    dataTestId: 'stat-orders'
  },
  { 
    label: 'Пользователи', 
    value: stats.value?.users_count || 0,
    icon: 'ph:users-bold',
    color: 'var(--color-accent)',
    dataTestId: 'stat-users'
  },
])
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>
      Панель управления
    </template>

    <div class="admin-dashboard">
      <!-- Requires Attention Section -->
      <div class="dashboard-section">
        <h2 class="section-title">Требуют внимания</h2>
        <AdminAttentionStats :stats="stats?.attention_stats" :pending="pending" />
      </div>

      <!-- Main Metrics -->
      <div class="dashboard-section">
        <div v-if="pending" class="stats-grid">
          <USkeleton v-for="i in 3" :key="i" height="110px" />
        </div>
        
        <div v-else class="stats-grid">
          <UCard v-for="stat in statCards" :key="stat.label" class="stat-card" :data-testid="stat.dataTestId">
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
        <!-- Chart Widget -->
        <div class="dashboard-section">
          <h2 class="section-title">Аналитика продаж</h2>
          <UCard class="chart-card">
            <AdminSalesChart :stats="stats?.daily_stats || []" :pending="pending" />
          </UCard>
        </div>

        <!-- Recent Orders Widget -->
        <div class="dashboard-section">
          <AdminRecentOrders />
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
  flex-direction: column;
  justify-content: center;
}
</style>
