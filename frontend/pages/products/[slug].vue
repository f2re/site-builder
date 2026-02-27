<script setup lang="ts">
import { useProducts } from '~/composables/useProducts'
import { useCartStore } from '~/stores/cartStore'
import { useProductSchema } from '~/composables/useSchemaOrg'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'

const route = useRoute()
const config = useRuntimeConfig()
const { getProduct } = useProducts()
const cartStore = useCartStore()

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
    cartStore.addItem(product.value.id, 1)
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
    useProductSchema(product.value)
  }
})

const breadcrumbItems = computed(() => [
  { name: 'Каталог', path: '/products' },
  { name: product.value?.name || '...', path: `/products/${slug}` }
])
</script>

<template>
  <div class="product-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />

      <div v-if="pending" class="product-page__skeleton skeleton"></div>

      <div v-else-if="error" class="product-page__error">
        <h2>Ошибка при загрузке товара</h2>
        <p>Товар не найден или произошла ошибка сервера.</p>
        <NuxtLink to="/products" class="btn btn--primary">Вернуться в каталог</NuxtLink>
      </div>

      <div v-else-if="product" class="product-page__layout">
        <!-- Gallery -->
        <div class="product-gallery">
          <div class="product-gallery__main">
            <NuxtImg 
              :src="activeImage" 
              :alt="product.name" 
              class="product-gallery__main-image"
              loading="lazy"
              format="webp"
            />
          </div>
          <div v-if="product.images.length > 1" class="product-gallery__thumbs">
            <button
              v-for="img in product.images"
              :key="img"
              class="product-gallery__thumb"
              :class="{ 'is-active': activeImage === img }"
              @click="activeImage = img"
            >
              <NuxtImg :src="img" :alt="product.name" width="80" height="80" fit="contain" />
            </button>
          </div>
        </div>

        <!-- Info -->
        <div class="product-info">
          <div class="product-info__category">{{ product.category.name }}</div>
          <h1 class="product-info__title">{{ product.name }}</h1>

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

          <div class="product-info__actions">
            <button
              class="btn btn--primary btn--lg"
              :disabled="product.stock <= 0"
              @click="addToCart"
            >
              Добавить в корзину
            </button>
            <button class="btn btn--secondary btn--lg">Купить в 1 клик</button>
          </div>

          <div class="product-info__description">
            <h3 class="section-title">Описание</h3>
            <p>{{ product.description }}</p>
          </div>

          <div v-if="product.attributes" class="product-info__attributes">
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
    grid-template-columns: 1.2fr 1fr;
  }
}

/* Gallery */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-gallery__thumbs {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
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

.product-gallery__thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* Info */
.product-info__category {
  font-size: var(--text-sm);
  color: var(--color-accent);
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.product-info__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 24px;
  color: var(--color-text);
  line-height: 1.2;
}

.product-info__price-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-bg-subtle);
  padding: 24px;
  border-radius: var(--radius-lg);
  margin-bottom: 32px;
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
  box-shadow: 0 0 8px var(--color-success);
}

.product-info__stock--out {
  color: var(--color-muted);
}
.product-info__stock--out .stock-dot {
  background: var(--color-muted);
}

.product-info__actions {
  display: flex;
  gap: 16px;
  margin-bottom: 40px;
}

.product-info__actions .btn {
  flex: 1;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-accent);
  display: inline-block;
  padding-bottom: 4px;
}

.product-info__description {
  margin-bottom: 40px;
}

.product-info__description p {
  color: var(--color-text-2);
  line-height: 1.6;
}

.attributes-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attribute-row {
  display: flex;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.attribute-key {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.attribute-value {
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 500;
}

.product-page__skeleton {
  height: 600px;
}

/* Base button styles */
.btn--lg {
  padding: 16px 32px;
  font-size: var(--text-base);
}

.btn--secondary {
  background: transparent;
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
}

.btn--secondary:hover {
  background: var(--color-accent-glow);
  transform: translateY(-2px);
}
</style>
