<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'
import { useProducts } from '~/composables/useProducts'
import ProductCard from '~/components/catalog/ProductCard.vue'
import BlogCard from '~/components/blog/BlogCard.vue'
import USkeleton from '~/components/U/USkeleton.vue'

useSeoMeta({
  title: 'WifiOBD Shop — OBD2 диагностика и IoT мониторинг авто',
  description: 'Магазин профессиональных OBD2 сканеров, WiFi адаптеров и IoT систем мониторинга для вашего автомобиля.',
})

const { getPosts } = useBlog()
const { getProducts } = useProducts()

// Fetch featured products (first 4)
const { data: productsData, pending: productsPending } = getProducts({ per_page: 4 })

// Fetch latest blog posts (first 3)
const { data: blogData, pending: blogPending } = getPosts({ per_page: 3 })

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
            <Icon name="ph:shopping-bag-bold" size="20" />
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

    <!-- Featured Products -->
    <section class="featured-products section">
      <div class="section-header">
        <h2 class="section-title">Популярные товары</h2>
        <NuxtLink to="/products" class="view-all">
          Все товары <Icon name="ph:arrow-right-bold" />
        </NuxtLink>
      </div>

      <div v-if="productsPending" class="products-grid">
        <USkeleton v-for="i in 4" :key="i" height="400px" />
      </div>
      <div v-else-if="productsData?.items?.length" class="products-grid">
        <ProductCard
          v-for="product in productsData.items"
          :key="product.id"
          :product="product"
        />
      </div>
    </section>

    <!-- Features -->
    <section class="features section" aria-label="Преимущества">
      <h2 class="section-title text-center">Почему WifiOBD?</h2>
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

    <!-- Latest News -->
    <section class="latest-news section">
      <div class="section-header">
        <h2 class="section-title">Последнее в блоге</h2>
        <NuxtLink to="/blog" class="view-all">
          Все статьи <Icon name="ph:arrow-right-bold" />
        </NuxtLink>
      </div>

      <div v-if="blogPending" class="blog-grid">
        <USkeleton v-for="i in 3" :key="i" height="350px" />
      </div>
      <div v-else-if="blogData?.items?.length" class="blog-grid">
        <BlogCard
          v-for="post in blogData.items"
          :key="post.id"
          :post="post"
        />
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
.section {
  padding: 64px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.section-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
}

.text-center { text-align: center; }

.view-all {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 700;
  font-size: var(--text-sm);
  transition: transform var(--transition-fast);
}

.view-all:hover {
  transform: translateX(4px);
}

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
  margin: 32px 0 64px;
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

/* Grids */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.blog-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* Features */
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
  margin: 64px 0 16px;
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
@media (max-width: 1024px) {
  .products-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 48px 0 40px;
  }

  .hero-subtitle { max-width: 100%; }
  .hero-actions  { justify-content: center; }
  .hero-visual   { display: none; }

  .products-grid { grid-template-columns: repeat(2, 1fr); }
  .blog-grid { grid-template-columns: repeat(2, 1fr); }
  .features-grid { grid-template-columns: 1fr; }

  .cta-banner {
    padding: 36px 24px;
  }
}

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: 1fr; }
  .products-grid { grid-template-columns: 1fr; }
  .blog-grid { grid-template-columns: 1fr; }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
