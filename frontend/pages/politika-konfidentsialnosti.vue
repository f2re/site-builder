<script setup lang="ts">
useSeoMeta({ title: 'Политика конфиденциальности — WifiOBD' })
</script>

<template>
  <main class="info-page">
    <div class="container">
      <div class="info-page__header">
        <h1 class="info-page__title">Политика конфиденциальности</h1>
        <p class="info-page__subtitle">Последнее обновление: 2026 год</p>
      </div>
      <div class="info-page__content">
        <p>Раздел находится в разработке. Здесь будет размещена актуальная политика конфиденциальности и обработки персональных данных.</p>
      </div>
    </div>
  </main>
</template>

<style scoped>
.info-page {
  padding: 64px 0;
  min-height: 60vh;
}

.info-page__header {
  margin-bottom: 48px;
}

.info-page__title {
  font-size: clamp(1.75rem, 4vw, 3rem);
  font-weight: 900;
  color: var(--color-text);
}

.info-page__subtitle {
  color: var(--color-text-2);
  margin-top: 8px;
}

.info-page__content {
  color: var(--color-text-2);
  line-height: 1.8;
  max-width: 800px;
}
</style>
