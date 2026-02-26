<script setup lang="ts">
useSeoMeta({
  title: 'WifiOBD Shop — OBD2 диагностика и IoT мониторинг авто',
  description: 'Магазин профессиональных OBD2 сканеров, WiFi адаптеров и IoT систем мониторинга для вашего автомобиля.',
})

const features = [
  {
    icon: '⚡',
    title: 'Быстрая диагностика',
    text: 'Подключение за 30 секунд. Считывайте коды ошибок и параметры двигателя в реальном времени.',
  },
  {
    icon: '📡',
    title: 'WiFi & Bluetooth',
    text: 'Работает с iPhone и Android через популярные приложения: Torque, OBD Fusion, Car Scanner.',
  },
  {
    icon: '🛡️',
    title: 'Гарантия 12 месяцев',
    text: 'Официальная гарантия на все устройства. Возврат в течение 14 дней без вопросов.',
  },
]

const stats = [
  { value: '500+', label: 'Товаров в каталоге' },
  { value: '24/7', label: 'Поддержка клиентов' },
  { value: '15 000', label: 'Довольных клиентов' },
]
</script>

<template>
  <div class="home-page">
    <!-- Hero -->
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-content">
        <p class="hero-eyebrow">OBD2 · WiFi · IoT Мониторинг</p>
        <h1 id="hero-title" class="hero-title">
          Магазин <span class="text-accent">WifiOBD</span> решений
        </h1>
        <p class="hero-subtitle">
          Всё для диагностики вашего авто в одном месте.
          От OBD2 сканеров до продвинутых IoT систем мониторинга.
        </p>
        <div class="hero-actions">
          <NuxtLink to="/products" class="btn btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
              aria-hidden="true">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <path d="M16 10a4 4 0 0 1-8 0"/>
            </svg>
            Перейти в каталог
          </NuxtLink>
          <NuxtLink to="/blog" class="btn btn-secondary">Читать блог</NuxtLink>
        </div>
      </div>
      <!-- Hero visual -->
      <div class="hero-visual" aria-hidden="true">
        <div class="device-mockup">
          <div class="device-screen">
            <div class="screen-header">
              <span class="screen-dot" />
              <span class="screen-title">OBD2 Live Data</span>
            </div>
            <div class="screen-metrics">
              <div class="metric">
                <span class="metric-label">RPM</span>
                <span class="metric-value">2 450</span>
              </div>
              <div class="metric">
                <span class="metric-label">Скорость</span>
                <span class="metric-value text-accent">87 км/ч</span>
              </div>
              <div class="metric">
                <span class="metric-label">T° двигателя</span>
                <span class="metric-value">92°C</span>
              </div>
              <div class="metric">
                <span class="metric-label">Ошибки</span>
                <span class="metric-value" style="color: var(--color-success)">0</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <div class="stats-grid" role="list">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="stat-card"
        role="listitem"
      >
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Features -->
    <section class="features" aria-label="Преимущества">
      <h2 class="section-title">Почему WifiOBD?</h2>
      <div class="features-grid">
        <div
          v-for="f in features"
          :key="f.title"
          class="feature-card"
        >
          <div class="feature-icon" aria-hidden="true">{{ f.icon }}</div>
          <h3 class="feature-title">{{ f.title }}</h3>
          <p class="feature-text">{{ f.text }}</p>
        </div>
      </div>
    </section>

    <!-- CTA Banner -->
    <section class="cta-banner" aria-label="Призыв к действию">
      <h2 class="cta-title">Готовы начать диагностику?</h2>
      <p class="cta-sub">Выберите устройство и получите бесплатную доставку при заказе от 2 000 ₽</p>
      <NuxtLink to="/products" class="btn btn-primary">Смотреть каталог</NuxtLink>
    </section>
  </div>
</template>

<style scoped>
/* Hero */
.hero {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 48px;
  align-items: center;
  padding: 72px 0 60px;
}

.hero-eyebrow {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-accent);
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.hero-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 20px;
  letter-spacing: -1px;
}

.hero-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-2);
  line-height: 1.6;
  margin-bottom: 36px;
  max-width: 480px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Device mockup */
.hero-visual {
  display: flex;
  justify-content: center;
}

.device-mockup {
  background: var(--color-surface-2);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-xl);
  padding: 20px;
  width: 100%;
  max-width: 340px;
  box-shadow: var(--shadow-card), var(--shadow-glow-accent);
}

.device-screen {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.screen-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.screen-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50%       { opacity: .3; }
}

.screen-title {
  font-size: var(--text-xs);
  color: var(--color-muted);
  font-family: var(--font-mono);
}

.screen-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--color-border);
}

.metric {
  background: var(--color-bg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: var(--text-xs);
  color: var(--color-muted);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: .05em;
}

.metric-value {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  font-family: var(--font-mono);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin: 64px 0;
}

.stat-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 32px 24px;
  border-radius: var(--radius-lg);
  text-align: center;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-card);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-accent);
  margin-bottom: 6px;
  font-family: var(--font-mono);
}

.stat-label {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 500;
}

/* Features */
.features {
  margin: 0 0 64px;
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 36px;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  transition: border-color var(--transition-fast), transform var(--transition-fast);
}

.feature-card:hover {
  border-color: var(--color-border-strong);
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.feature-title {
  font-size: var(--text-base);
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--color-text);
}

.feature-text {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  line-height: 1.6;
}

/* CTA Banner */
.cta-banner {
  background: linear-gradient(135deg, var(--color-surface-2) 0%, var(--color-surface-3) 100%);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-xl);
  padding: 52px 48px;
  text-align: center;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
}

.cta-banner::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.cta-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 12px;
}

.cta-sub {
  color: var(--color-text-2);
  font-size: var(--text-base);
  margin-bottom: 28px;
}

/* Responsive */
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 48px 0 40px;
  }

  .hero-subtitle { max-width: 100%; }
  .hero-actions  { justify-content: center; }
  .hero-visual   { display: none; }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .cta-banner {
    padding: 36px 24px;
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
