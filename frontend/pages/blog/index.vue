<script setup lang="ts">
useSeoMeta({
  title: 'Блог — WifiOBD Shop',
  description: 'Статьи и инструкции по диагностике автомобилей, обзоры OBD2 устройств и советы по эксплуатации.',
})
</script>

<template>
  <div class="blog-page">
    <div class="page-header">
      <h1 class="page-title">Блог</h1>
      <p class="page-subtitle">Инструкции, обзоры и советы по OBD2 диагностике</p>
    </div>

    <!-- Placeholder posts -->
    <div class="posts-grid">
      <article
        v-for="i in 3"
        :key="i"
        class="post-card"
        aria-hidden="true"
      >
        <div class="skeleton post-img-skeleton" />
        <div class="post-body">
          <div class="skeleton skeleton-line" style="width: 30%; height: 12px; margin-bottom: 12px" />
          <div class="skeleton skeleton-line" style="width: 85%; height: 20px; margin-bottom: 8px" />
          <div class="skeleton skeleton-line" style="width: 60%; height: 14px" />
        </div>
      </article>
    </div>

    <p class="coming-soon">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        aria-hidden="true">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
      Статьи скоро появятся. Следите за обновлениями.
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

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 28px;
  margin-bottom: 40px;
}

.post-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.post-img-skeleton {
  width: 100%;
  height: 200px;
}

.post-body {
  padding: 20px;
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
