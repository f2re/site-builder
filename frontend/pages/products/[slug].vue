<script setup lang="ts">
import { useProducts } from '~/composables/useProducts'
import { useCartStore } from '~/stores/cartStore'
import { useProductSchema } from '~/composables/useSchemaOrg'
import { useToast } from '~/composables/useToast'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import { ref, computed, watch, watchEffect } from 'vue'

const route = useRoute()
const config = useRuntimeConfig()
const { getProduct } = useProducts()
const cartStore = useCartStore()
const toast = useToast()

const slug = route.params.slug as string
const { data: product, pending, error } = await getProduct(slug)

const activeImage = ref('')

watch(product, (newVal) => {
  if (newVal?.images?.length) {
    activeImage.value = newVal.images[0]
  }
}, { immediate: true })

const addToCart = () => {
  if (product.value) {
    cartStore.addItem({
      id: product.value.id as any,
      name: product.value.name,
      price: product.value.price_display,
      image: product.value.images[0]
    })
    
    toast.success({
      title: 'Добавлено в корзину',
      message: `${product.value.name} успешно добавлен.`
    })
  }
}

// SEO
useSeoMeta({
  title: () => product.value ? `${product.value.name} | WifiOBD` : 'Загрузка...',
  description: () => product.value?.description || 'Подробное описание товара в нашем каталоге.',
  ogTitle: () => product.value ? `${product.value.name} | WifiOBD` : 'Загрузка...',
  ogDescription: () => product.value?.description,
  ogImage: () => product.value?.images?.[0] ? (product.value.images[0].startsWith('http') ? product.value.images[0] : `${config.public.siteUrl}${product.value.images[0]}`) : undefined,
  twitterCard: 'summary_large_image',
})

useHead({
  link: [
    { rel: 'canonical', href: () => `${config.public.siteUrl}/products/${slug}` }
  ]
})

// Schema.org
watchEffect(() => {
  if (product.value) {
    useProductSchema({
      name: product.value.name,
      description: product.value.description,
      images: product.value.images,
      price_rub: product.value.price_rub,
      stock: product.value.stock,
      sku: product.value.slug
    })
  }
})

const breadcrumbItems = computed(() => [
  { name: 'Каталог', path: '/products' },
  { name: product.value?.category?.name || '...', path: `/products?category=${product.value?.category?.slug}` },
  { name: product.value?.name || '...', path: `/products/${slug}` }
])

// Variant mock
const selectedVariant = ref('Standard')
const variants = ['Standard', 'Premium', 'Pro']
</script>

<template>
  <div class="product-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />

      <div v-if="pending" class="product-page__skeleton-wrapper">
        <div class="skeleton-image skeleton"></div>
        <div class="skeleton-content">
          <div class="skeleton-line skeleton w-1/2"></div>
          <div class="skeleton-line skeleton h-12"></div>
          <div class="skeleton-line skeleton w-1/3"></div>
          <div class="skeleton-line skeleton h-24"></div>
        </div>
      </div>

      <div v-else-if="error" class="product-page__error">
        <div class="error-card">
          <Icon name="ph:warning-circle-bold" size="64" color="var(--color-error)" />
          <h2>Ошибка при загрузке товара</h2>
          <p>Товар не найден или произошла ошибка сервера.</p>
          <NuxtLink to="/products" class="btn btn--primary">Вернуться в каталог</NuxtLink>
        </div>
      </div>

      <div v-else-if="product" class="product-page__layout">
        <!-- Gallery -->
        <div class="product-gallery">
          <div class="product-gallery__main">
            <Transition name="fade" mode="out-in">
              <NuxtImg 
                :key="activeImage"
                :src="activeImage" 
                :alt="product.name" 
                class="product-gallery__main-image"
                loading="eager"
                format="webp"
                sizes="sm:480px md:800px lg:1200px"
              />
            </Transition>
          </div>
          <div v-if="product.images.length > 1" class="product-gallery__thumbs">
            <button
              v-for="img in product.images"
              :key="img"
              class="product-gallery__thumb"
              :class="{ 'is-active': activeImage === img }"
              @click="activeImage = img"
            >
              <NuxtImg :src="img" :alt="product.name" width="80" height="80" fit="contain" format="webp" />
            </button>
          </div>
        </div>

        <!-- Info -->
        <div class="product-info">
          <div class="product-info__header">
            <div class="product-info__category">{{ product.category?.name }}</div>
            <h1 class="product-info__title">{{ product.name }}</h1>
          </div>

          <div class="product-info__price-block">
            <div class="product-info__price">
              <span class="product-info__price-value">{{ product.price_display }}</span>
              <span class="product-info__price-currency">{{ product.currency }}</span>
            </div>

            <div
              class="product-info__stock"
              :class="product.stock > 0 ? 'product-info__stock--in' : 'product-info__stock--out'"
            >
              <span class="stock-dot"></span>
              {{ product.stock > 0 ? `В наличии (${product.stock} шт.)` : 'Нет в наличии' }}
            </div>
          </div>

          <!-- Variant Switcher (Mock) -->
          <div class="product-variants">
            <div class="product-variants__label">Версия</div>
            <div class="product-variants__list">
              <button 
                v-for="v in variants" 
                :key="v"
                class="variant-btn"
                :class="{ 'is-active': selectedVariant === v }"
                @click="selectedVariant = v"
              >
                {{ v }}
              </button>
            </div>
          </div>

          <div class="product-info__actions">
            <button
              class="btn btn--primary btn--lg btn-add-cart"
              :disabled="product.stock <= 0"
              @click="addToCart"
            >
              <Icon name="ph:shopping-cart-simple-bold" size="20" />
              <span>Добавить в корзину</span>
            </button>
            <button class="btn btn--ghost btn--lg btn-one-click">
              Купить в 1 клик
            </button>
          </div>

          <div class="product-info__description">
            <h3 class="section-title">Описание</h3>
            <p>{{ product.description }}</p>
          </div>

          <div v-if="product.attributes && Object.keys(product.attributes).length" class="product-info__attributes">
            <h3 class="section-title">Характеристики</h3>
            <div class="attributes-grid">
              <div v-for="(val, key) in product.attributes" :key="key" class="attribute-row">
                <span class="attribute-key">{{ key }}</span>
                <span class="attribute-value">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-page {
  padding: 40px 0;
}

.product-page__layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
}

@media (min-width: 1024px) {
  .product-page__layout {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}

/* Gallery */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 100px;
}

.product-gallery__main {
  aspect-ratio: 1 / 1;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-gallery__main-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 24px;
}

.product-gallery__thumbs {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px;
}

.product-gallery__thumb {
  width: 80px;
  height: 80px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
  padding: 8px;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.product-gallery__thumb:hover {
  border-color: var(--color-accent);
}

.product-gallery__thumb.is-active {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* Info */
.product-info__header {
  margin-bottom: 24px;
}

.product-info__category {
  font-size: var(--text-sm);
  color: var(--color-accent);
  font-weight: 700;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.product-info__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-text);
  line-height: 1.1;
}

.product-info__price-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface-2);
  padding: 24px;
  border-radius: var(--radius-lg);
  margin-bottom: 32px;
  border: 1px solid var(--color-border);
}

.product-info__price {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.product-info__price-value {
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--color-text);
}

.product-info__price-currency {
  font-size: var(--text-base);
  color: var(--color-text-2);
}

.product-info__stock {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
  font-weight: 600;
}

.stock-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.product-info__stock--in {
  color: var(--color-success);
}
.product-info__stock--in .stock-dot {
  background: var(--color-success);
  box-shadow: 0 0 10px var(--color-success);
}

.product-info__stock--out {
  color: var(--color-muted);
}
.product-info__stock--out .stock-dot {
  background: var(--color-muted);
}

/* Variants */
.product-variants {
  margin-bottom: 32px;
}

.product-variants__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  color: var(--color-muted);
  font-weight: 700;
  margin-bottom: 12px;
}

.product-variants__list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.variant-btn {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.variant-btn:hover {
  border-color: var(--color-accent);
}

.variant-btn.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.product-info__actions {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.btn-add-cart {
  flex: 2;
  gap: 12px;
}

.btn-one-click {
  flex: 1;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-text);
  border-left: 4px solid var(--color-accent);
  padding-left: 12px;
}

.product-info__description {
  margin-bottom: 40px;
}

.product-info__description p {
  color: var(--color-text-2);
  line-height: 1.6;
  white-space: pre-line;
}

.attributes-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attribute-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
}

.attribute-key {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.attribute-value {
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
}

/* Skeletons */
.product-page__skeleton-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}

.skeleton-image { aspect-ratio: 1/1; border-radius: var(--radius-xl); }
.skeleton-content { display: flex; flex-direction: column; gap: 16px; }
.skeleton-line { border-radius: 4px; }
.w-1\/2 { width: 50%; }
.w-1\/3 { width: 33%; }
.h-12 { height: 48px; }
.h-24 { height: 96px; }

/* Error State */
.product-page__error {
  padding: 80px 0;
  display: flex;
  justify-content: center;
}

.error-card {
  text-align: center;
  max-width: 400px;
  background: var(--color-surface);
  padding: 40px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
}

.error-card h2 { margin: 24px 0 12px; }
.error-card p { color: var(--color-text-2); margin-bottom: 32px; }

/* Animations */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
