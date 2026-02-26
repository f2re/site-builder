<script setup lang="ts">
useSeoMeta({
  title: 'Каталог — WifiOBD Shop',
  description: 'Каталог OBD2 сканеров, WiFi адаптеров и IoT устройств для диагностики автомобилей.',
})
</script>

<template>
  <div class="products-page">
    <div class="page-header">
      <h1 class="page-title">Каталог товаров</h1>
      <p class="page-subtitle">OBD2 сканеры, WiFi адаптеры и IoT решения для вашего автомобиля</p>
    </div>

    <!-- Placeholder grid -->
    <div class="products-grid">
      <div
        v-for="i in 8"
        :key="i"
        class="product-card skeleton-card"
        aria-hidden="true"
      >
        <div class="skeleton product-img-skeleton" />
        <div class="card-body">
          <div class="skeleton skeleton-line" style="width: 70%; height: 16px; margin-bottom: 8px" />
          <div class="skeleton skeleton-line" style="width: 40%; height: 22px" />
        </div>
      </div>
    </div>

    <p class="coming-soon">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        aria-hidden="true">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
      Товары скоро появятся. Подпишитесь на обновления в Telegram.
    </p>
  </div>
</template>

<style scoped>
.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 8px;
}

.page-subtitle {
  color: var(--color-text-2);
  font-size: var(--text-base);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.product-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.product-img-skeleton {
  width: 100%;
  height: 180px;
}

.card-body {
  padding: 16px;
}

.skeleton-line {
  border-radius: var(--radius-sm);
  display: block;
}

.coming-soon {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-muted);
  font-size: var(--text-sm);
  justify-content: center;
  padding: 8px 0 32px;
}
</style>
