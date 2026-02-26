<template>
  <div class="home-page">
    <section class="hero">
      <h1 class="hero-title">Магазин <span class="text-accent">WifiOBD</span> решений</h1>
      <p class="hero-subtitle">Всё для диагностики вашего авто в одном месте. От OBD2 сканеров до продвинутых IoT систем мониторинга.</p>
      <div class="hero-actions">
        <NuxtLink to="/products" class="btn btn-primary">Перейти в каталог</NuxtLink>
        <NuxtLink to="/blog" class="btn btn-secondary">Читать блог</NuxtLink>
      </div>
    </section>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">500+</div>
        <div class="stat-label">Товаров</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">24/7</div>
        <div class="stat-label">Поддержка</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">15к</div>
        <div class="stat-label">Клиентов</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 60px 0;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
}

.text-accent {
  color: var(--color-accent);
}

.hero-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  margin-bottom: 40px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn {
  padding: 12px 32px;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all var(--transition-normal);
  cursor: pointer;
}

.btn-primary {
  background-color: var(--color-accent);
  color: white;
  box-shadow: var(--shadow-glow-accent);
}

.btn-primary:hover {
  background-color: var(--color-accent-hover);
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: var(--color-surface-2);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-surface-3);
  border-color: var(--color-border-strong);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 80px;
}

.stat-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 32px;
  border-radius: var(--radius-lg);
  text-align: center;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-accent);
  margin-bottom: 8px;
}

.stat-label {
  color: var(--color-text-2);
  font-weight: 500;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
