<script setup lang="ts">
import { useProducts } from '~/composables/useProducts'
import type { ProductVariant } from '~/composables/useProducts'
import { useProductOptions } from '~/composables/useProductOptions'
import { useCartStore } from '~/stores/cartStore'
import { useProductSchema } from '~/composables/useSchemaOrg'
import { useToast } from '~/composables/useToast'
import { formatPrice } from '~/composables/useFormatters'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import TipTapViewer from '~/components/blog/TipTapViewer.vue'
import QuickBuyModal from '~/components/shop/QuickBuyModal.vue'
import ProductDocIframe from '~/components/shop/ProductDocIframe.vue'
import ProductOptionSelector from '~/components/product/ProductOptionSelector.vue'
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const route = useRoute()
const { getProductBySlug } = useProducts()
const cartStore = useCartStore()
const toast = useToast()

const slug = route.params.slug as string
const { data: product, pending, error } = await getProductBySlug(slug)

const activeImage = ref('')

watch(product, (newVal) => {
  if (newVal?.images?.length) {
    const cover = newVal.images.find(img => img.is_cover) || newVal.images[0]
    activeImage.value = cover.url
  }
}, { immediate: true })

// Variant selection
const selectedVariant = ref<ProductVariant | null>(null)

watch(product, (newVal) => {
  if (newVal?.variants?.length) {
    selectedVariant.value = newVal.variants[0]
  }
}, { immediate: true })

// Product options composable (handles defaults, debounced price calculation)
const {
  selectedOptions,
  allRequiredSelected,
  calculatedPrice,
  isCalculating,
  selectedValueIds,
} = useProductOptions(product)

// Validation state for add-to-cart
const showValidation = ref(false)

const hasMultipleVariants = computed(() => (product.value?.variants?.length ?? 0) > 1)
const hasOptions = computed(() => (product.value?.option_groups?.length ?? 0) > 0)

const currentStock = computed(() => selectedVariant.value?.stock_quantity ?? product.value?.stock ?? 0)

const currentPriceRaw = computed(() => {
  // Use API-calculated price if available, fall back to local calculation
  if (calculatedPrice.value) {
    return calculatedPrice.value.final_price
  }
  const base = selectedVariant.value ? Number(selectedVariant.value.price) : Number(product.value?.price_display ?? 0)
  return base
})
const currentPrice = computed(() => formatPrice(currentPriceRaw.value))

const isCartDisabled = computed(() => {
  if (currentStock.value <= 0) return true
  if (hasOptions.value && !allRequiredSelected.value) return true
  return false
})

const priceBreakdown = computed(() => {
  if (!calculatedPrice.value?.breakdown?.length) return []
  return calculatedPrice.value.breakdown
})

const stockStatus = computed(() => {
  const qty = currentStock.value
  if (qty <= 0) return 'out'
  if (qty <= 5) return 'low'
  return 'in'
})

const stockLabel = computed(() => {
  const qty = currentStock.value
  if (qty <= 0) return 'Нет в наличии'
  if (qty <= 5) return `Осталось мало: ${qty} шт.`
  return `В наличии: ${qty} шт.`
})

const hasDescription = computed(() => {
  return !!(product.value?.description_html || product.value?.content_json || product.value?.description)
})

const hasAttributes = computed(() => {
  return !!(product.value?.attributes && Object.keys(product.value.attributes).length > 0)
})

const hasImages = computed(() => (product.value?.images?.length ?? 0) > 0)

// Loading state for add to cart
const isAddingToCart = ref(false)

const addToCart = async () => {
  if (!product.value) return
  if (currentStock.value <= 0) return

  // Validate required options
  if (hasOptions.value && !allRequiredSelected.value) {
    showValidation.value = true
    toast.warning('Выберите опции', 'Пожалуйста, выберите все обязательные параметры товара.')
    return
  }

  isAddingToCart.value = true

  // Resolve selected options for snapshot
  const optionSnapshots: Array<{
    group_id: string
    group_name: string
    value_id: string
    value_name: string
    price_modifier: number
  }> = []

  if (product.value.option_groups) {
    product.value.option_groups.forEach(group => {
      const selected = selectedOptions.value[group.id]
      if (!selected) return
      const selectedIds = Array.isArray(selected) ? selected : [selected]
      selectedIds.forEach(selId => {
        const val = group.values.find(v => v.id === selId)
        if (val) {
          optionSnapshots.push({
            group_id: group.id,
            group_name: group.name,
            value_id: val.id,
            value_name: val.name,
            price_modifier: Number(val.price_modifier)
          })
        }
      })
    })
  }

  const optionValueIds = selectedValueIds.value

  const variantId = selectedVariant.value?.id || product.value.variants[0]?.id
  const sortedIds = [...optionValueIds].sort()
  const compositeId = `${variantId}:${sortedIds.join(':')}`

  const added = cartStore.addItem({
    id: compositeId,
    variantId: variantId,
    name: product.value.name,
    price: currentPriceRaw.value,
    image: product.value.images[0]?.url || '/placeholder-product.png',
    maxStock: currentStock.value,
    selectedOptions: optionSnapshots,
    selectedOptionValueIds: optionValueIds
  })

  isAddingToCart.value = false

  if (added === false) {
    toast.warning('Недостаточно товара', `В наличии только ${currentStock.value} шт.`)
  } else {
    toast.success('Добавлено в корзину', `${product.value.name} успешно добавлен.`)
  }
}

// SEO & Schema.org
useHead(() => {
  if (!product.value) return {}

  const title = product.value.meta_title || `${product.value.name} — Купить в магазине WifiOBD`
  const description = product.value.meta_description || product.value.description
  const image = product.value.og_image_url || product.value.images[0]?.url

  return {
    title,
    meta: [
      { name: 'description', content: description },
      { property: 'og:title', content: title },
      { property: 'og:description', content: description },
      { property: 'og:image', content: image },
      { property: 'og:type', content: 'product' },
      { name: 'twitter:card', content: 'summary_large_image' },
    ]
  }
})

watch(product, (val) => {
  if (val) {
    useProductSchema({
      name: val.name,
      description: val.description,
      images: val.images.map(img => img.url),
      price_rub: val.price_rub || (val.variants[0]?.price || 0),
      stock: val.stock,
      sku: val.variants[0]?.sku
    })
  }
}, { immediate: true })

const breadcrumbCrumbs = computed(() => {
  const crumbs = [
    { label: 'Главная', to: '/', icon: 'ph:house-bold' },
    { label: 'Каталог', to: '/products' },
  ]
  if (product.value?.category?.name) {
    crumbs.push({
      label: product.value.category.name,
      to: `/products?category=${product.value.category.slug}`
    })
  }
  crumbs.push({ label: product.value?.name || '', to: `/products/${slug}` })
  return crumbs
})

// Sticky Buy Bar logic
const buyPanelRef = ref<HTMLElement | null>(null)
const showStickyBar = ref(false)

const handleScroll = () => {
  if (!buyPanelRef.value) return
  const rect = buyPanelRef.value.getBoundingClientRect()
  showStickyBar.value = rect.bottom < 0
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

// Quick Buy Modal
const isQuickBuyOpen = ref(false)

const openQuickBuy = () => {
  isQuickBuyOpen.value = true
}

const handleQuickBuySubmitted = () => {
  toast.success('Заявка принята!', 'Мы перезвоним вам в течение 30 минут.')
}
</script>

<template>
  <div class="product-page">
    <div class="container">
      <AppBreadcrumbs :crumbs="breadcrumbCrumbs" />

      <!-- Skeleton loader -->
      <div v-if="pending" class="product-skeleton">
        <div class="product-skeleton__gallery skeleton"></div>
        <div class="product-skeleton__info">
          <div class="product-skeleton__badge skeleton"></div>
          <div class="product-skeleton__title skeleton"></div>
          <div class="product-skeleton__price skeleton"></div>
          <div class="product-skeleton__btn skeleton"></div>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="product-error">
        <div class="product-error__card">
          <Icon name="ph:warning-circle-bold" size="64" color="var(--color-error)" />
          <h2 class="product-error__title">Товар не найден</h2>
          <p class="product-error__text">Возможно, товар был удалён или ссылка устарела.</p>
          <NuxtLink to="/products" class="product-btn product-btn--primary">
            <Icon name="ph:arrow-left-bold" size="16" />
            Вернуться в каталог
          </NuxtLink>
        </div>
      </div>

      <!-- Product content -->
      <div v-else-if="product" class="product-layout">

        <!-- HERO: Gallery + Buy Panel -->
        <section class="product-hero" aria-label="Товар">
          <!-- Gallery (60%) -->
          <div
            class="product-gallery"
            data-testid="product-gallery"
          >
            <div
              class="product-gallery__main"
              data-testid="product-gallery-main"
            >
              <Transition name="img-fade" mode="out-in">
                <NuxtImg
                  v-if="hasImages && activeImage"
                  :key="activeImage"
                  :src="activeImage"
                  :alt="product.name"
                  class="product-gallery__main-image"
                  loading="eager"
                  format="webp"
                  sizes="sm:480px md:640px lg:800px"
                />
                <div v-else class="product-gallery__placeholder">
                  <Icon name="ph:image-square-bold" size="80" color="var(--color-muted)" />
                  <span class="product-gallery__placeholder-text">Нет изображения</span>
                </div>
              </Transition>
            </div>

            <div
              v-if="product.images.length > 1"
              class="product-gallery__thumbs"
            >
              <button
                v-for="img in product.images"
                :key="img.url"
                class="product-gallery__thumb"
                :class="{ 'is-active': activeImage === img.url }"
                :aria-label="`Изображение ${img.alt || product.name}`"
                :aria-pressed="activeImage === img.url"
                data-testid="product-gallery-thumb"
                @click="activeImage = img.url"
              >
                <NuxtImg
                  :src="img.url"
                  :alt="img.alt || product.name"
                  width="80"
                  height="80"
                  fit="contain"
                  format="webp"
                />
              </button>
            </div>
          </div>

          <!-- Buy Panel (40%) -->
          <div class="product-buy-panel" ref="buyPanelRef">
            <!-- Category badge -->
            <NuxtLink
              v-if="product.category"
              :to="`/products?category=${product.category.slug}`"
              class="product-buy-panel__category"
              :aria-label="`Категория: ${product.category.name}`"
            >
              {{ product.category.name }}
            </NuxtLink>
            <span v-else class="product-buy-panel__category product-buy-panel__category--static">
              Товар
            </span>

            <!-- Title -->
            <h1
              class="product-buy-panel__title"
              data-testid="product-title"
            >
              {{ product.name }}
            </h1>

            <!-- Price -->
            <div class="product-buy-panel__price-row">
              <span
                class="product-buy-panel__price"
                data-testid="product-price"
              >
                {{ currentPrice }}
              </span>
            </div>

            <!-- Stock badge -->
            <div
              v-if="currentStock > 0"
              class="product-buy-panel__stock"
              :class="{
                'product-buy-panel__stock--in': stockStatus === 'in',
                'product-buy-panel__stock--low': stockStatus === 'low',
              }"
              data-testid="product-stock"
            >
              <span class="stock-dot" aria-hidden="true"></span>
              <span>{{ stockLabel }}</span>
            </div>
            <div
              v-else
              class="product-buy-panel__stock product-buy-panel__stock--out"
              data-testid="product-stock"
            >
              <span class="stock-dot" aria-hidden="true"></span>
              <span>{{ stockLabel }}</span>
            </div>

            <!-- Variant selector -->
            <div
              v-if="hasMultipleVariants"
              class="product-variants"
              data-testid="product-variant-selector"
            >
              <div class="product-variants__label">Вариант</div>
              <div class="product-variants__list">
                <button
                  v-for="v in product.variants"
                  :key="v.id"
                  class="variant-btn"
                  :class="{ 'is-active': selectedVariant?.id === v.id }"
                  :aria-pressed="selectedVariant?.id === v.id"
                  :aria-label="`Выбрать ${v.name} за ${formatPrice(v.price)}`"
                  @click="selectedVariant = v"
                >
                  <span class="variant-btn__name">{{ v.name }}</span>
                  <span class="variant-btn__price">{{ formatPrice(v.price) }}</span>
                </button>
              </div>
            </div>

            <!-- Options Selector -->
            <ProductOptionSelector
              v-if="hasOptions"
              v-model="selectedOptions"
              :option-groups="product.option_groups"
              :show-validation="showValidation"
            />

            <!-- Price breakdown (from calculate-price API) -->
            <div
              v-if="hasOptions && (calculatedPrice || isCalculating)"
              class="price-breakdown"
              data-testid="price-breakdown"
              aria-live="polite"
            >
              <div v-if="isCalculating" class="price-breakdown__loading">
                <span class="price-breakdown__skeleton"></span>
              </div>
              <template v-else-if="calculatedPrice && priceBreakdown.length">
                <div class="price-breakdown__list">
                  <div class="price-breakdown__row price-breakdown__row--base">
                    <span>Базовая цена</span>
                    <span>{{ formatPrice(calculatedPrice.base_price) }}</span>
                  </div>
                  <div
                    v-for="item in priceBreakdown"
                    :key="item.group_name"
                    class="price-breakdown__row"
                  >
                    <span class="price-breakdown__label">{{ item.value_name }}</span>
                    <span
                      class="price-breakdown__modifier"
                      :class="{
                        'is-positive': item.price_modifier > 0,
                        'is-negative': item.price_modifier < 0,
                      }"
                    >
                      {{ item.price_modifier > 0 ? '+' : '' }}{{ formatPrice(item.price_modifier) }}
                    </span>
                  </div>
                </div>
              </template>
            </div>

            <!-- Actions -->
            <div class="product-buy-panel__actions">
              <button
                class="product-btn product-btn--primary product-btn--lg product-btn--full"
                :disabled="isCartDisabled || isAddingToCart"
                data-testid="add-to-cart-btn"
                :aria-busy="isAddingToCart"
                @click="addToCart"
              >
                <span v-if="isAddingToCart" class="btn-spinner" aria-hidden="true"></span>
                <Icon v-else name="ph:shopping-cart-simple-bold" size="20" aria-hidden="true" />
                <span>
                  {{ currentStock <= 0 ? 'Нет в наличии' : isAddingToCart ? 'Добавляем...' : (hasOptions && !allRequiredSelected) ? 'Выберите опции' : 'В корзину' }}
                </span>
              </button>

              <button
                class="product-btn product-btn--ghost product-btn--lg"
                data-testid="btn-quick-buy"
                @click="openQuickBuy"
              >
                Быстрый заказ
              </button>
            </div>

            <!-- Trust badges -->
            <div class="product-buy-panel__trust">
              <div class="trust-badge">
                <Icon name="ph:shield-check-bold" size="20" color="var(--color-success)" aria-hidden="true" />
                <span>Гарантия 1 год</span>
              </div>
              <div class="trust-badge">
                <Icon name="ph:seal-check-bold" size="20" color="var(--color-accent)" aria-hidden="true" />
                <span>Официальный товар</span>
              </div>
              <div class="trust-badge">
                <Icon name="ph:truck-bold" size="20" color="var(--color-neon)" aria-hidden="true" />
                <span>Быстрая доставка</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Description section (full width) -->
        <section
          v-if="hasDescription"
          class="product-description"
          data-testid="product-description"
        >
          <h2 class="product-section-title">Описание</h2>
          <div class="product-description__content">
            <TipTapViewer
              v-if="product.content_json"
              :content="product.content_json"
              class="product-description__tiptap"
            />
            <div
              v-else-if="product.description_html"
              class="product-description__html prose"
              v-html="product.description_html"
            ></div>
            <p
              v-else-if="product.description"
              class="product-description__plain"
            >
              {{ product.description }}
            </p>
          </div>
        </section>

        <!-- Documentation section -->
        <section
          v-if="product.doc_iframe_url"
          class="product-documentation"
          data-testid="product-documentation"
        >
          <h2 class="product-section-title">Документация</h2>
          <ProductDocIframe :url="product.doc_iframe_url" data-testid="doc-iframe" />
        </section>

        <!-- Attributes section -->
        <section
          v-if="hasAttributes"
          class="product-attributes"
        >
          <h2 class="product-section-title">Характеристики</h2>
          <div class="attributes-table">
            <div
              v-for="(val, key) in product.attributes"
              :key="key"
              class="attributes-table__row"
            >
              <span class="attributes-table__key">{{ key }}</span>
              <span class="attributes-table__value">{{ val }}</span>
            </div>
          </div>
        </section>

      </div>
    </div>

    <!-- Sticky Buy Bar -->
    <Transition name="sticky-bar">
      <div
        v-if="showStickyBar && product"
        class="sticky-buy-bar"
        data-testid="sticky-buy-bar"
        role="complementary"
        aria-label="Быстрая покупка"
      >
        <div class="container sticky-buy-bar__inner">
          <div class="sticky-buy-bar__product">
            <NuxtImg
              v-if="hasImages"
              :src="product.images[0]?.url"
              :alt="product.name"
              width="44"
              height="44"
              fit="cover"
              format="webp"
              class="sticky-buy-bar__image"
            />
            <div class="sticky-buy-bar__info">
              <div class="sticky-buy-bar__name">{{ product.name }}</div>
              <div class="sticky-buy-bar__price">{{ currentPrice }}</div>
            </div>
          </div>
          <button
            class="product-btn product-btn--primary product-btn--md"
            :disabled="currentStock <= 0"
            aria-label="Добавить в корзину"
            @click="addToCart"
          >
            <Icon name="ph:shopping-cart-simple-bold" size="16" aria-hidden="true" />
            <span>В корзину</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Quick Buy Modal -->
    <QuickBuyModal
      :is-open="isQuickBuyOpen"
      :product-name="product?.name ?? ''"
      :product-image="product?.images[0]?.url ?? ''"
      :variant-name="selectedVariant?.name ?? ''"
      :price="currentPrice"
      :selected-options="Object.entries(selectedOptions).flatMap(([groupId, valId]) => {
        const group = product?.option_groups.find(g => g.id === groupId)
        const ids = Array.isArray(valId) ? valId : [valId]
        return ids.map(id => {
          const val = group?.values.find(v => v.id === id)
          return { group_name: group?.name || '', value_name: val?.name || '' }
        })
      }).filter(o => o.group_name && o.value_name)"
      @close="isQuickBuyOpen = false"
      @submitted="handleQuickBuySubmitted"
    />
  </div>
</template>

<style scoped>
/* ─── Page ─────────────────────────────────────────── */
.product-page {
  padding: 32px 0 80px;
}

/* ─── Layout ────────────────────────────────────────── */
.product-layout {
  display: flex;
  flex-direction: column;
  gap: 64px;
}

/* ─── HERO: 60/40 grid ──────────────────────────────── */
.product-hero {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  align-items: start;
}

@media (min-width: 768px) {
  .product-hero {
    grid-template-columns: 3fr 2fr;
    gap: 48px;
  }
}

/* ─── Gallery ───────────────────────────────────────── */
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 768px) {
  .product-gallery {
    position: sticky;
    top: 80px;
  }
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

.product-gallery__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.product-gallery__placeholder-text {
  font-size: var(--text-sm);
  color: var(--color-muted);
}

.product-gallery__thumbs {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px;
  scrollbar-width: none;
}

.product-gallery__thumbs::-webkit-scrollbar {
  display: none;
}

.product-gallery__thumb {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
  padding: 6px;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  overflow: hidden;
}

.product-gallery__thumb:hover {
  border-color: var(--color-accent);
}

.product-gallery__thumb.is-active {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* ─── Buy Panel ─────────────────────────────────────── */
.product-buy-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (min-width: 768px) {
  .product-buy-panel {
    position: sticky;
    top: 80px;
  }
}

/* Category badge */
.product-buy-panel__category {
  display: inline-flex;
  align-items: center;
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-on-accent);
  background: var(--color-accent);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  text-decoration: none;
  width: fit-content;
  transition: background var(--transition-fast), box-shadow var(--transition-fast);
}

.product-buy-panel__category:hover {
  background: var(--color-accent-hover);
  box-shadow: var(--shadow-glow-accent);
}

.product-buy-panel__category--static {
  color: var(--color-on-accent);
  background: var(--color-accent);
}

/* Title */
.product-buy-panel__title {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  line-height: 1.2;
  margin: 0;
  font-family: var(--font-sans);
}

/* Price */
.product-buy-panel__price-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.product-buy-panel__price {
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--color-accent);
  font-family: var(--font-mono);
  line-height: 1;
}

/* Stock */
.product-buy-panel__stock {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
  font-weight: 600;
  padding: 6px 12px;
  border-radius: var(--radius-full);
  width: fit-content;
}

.product-buy-panel__stock--in {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.product-buy-panel__stock--in .stock-dot {
  background: var(--color-success);
  box-shadow: 0 0 6px var(--color-success);
}

.product-buy-panel__stock--low {
  color: var(--color-warning);
  background: var(--color-warning-bg);
}

.product-buy-panel__stock--low .stock-dot {
  background: var(--color-warning);
  box-shadow: 0 0 6px var(--color-warning);
}

.product-buy-panel__stock--out {
  color: var(--color-muted);
  background: var(--color-surface-2);
}

.product-buy-panel__stock--out .stock-dot {
  background: var(--color-muted);
}

.stock-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── Variants ──────────────────────────────────────── */
.product-variants {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-variants__label {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  font-weight: 700;
}

.product-variants__list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.variant-btn {
  padding: 8px 16px;
  border: 2px solid var(--color-border);
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 80px;
}

.variant-btn:hover {
  border-color: var(--color-accent);
}

.variant-btn.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-glow);
  color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.variant-btn__name {
  font-size: var(--text-sm);
}

.variant-btn__price {
  font-size: var(--text-xs);
  color: var(--color-muted);
  font-family: var(--font-mono);
}

.variant-btn.is-active .variant-btn__price {
  color: var(--color-accent);
}

/* ─── Price breakdown ───────────────────────────────── */
.price-breakdown {
  border-top: 1px solid var(--color-border);
  padding-top: 12px;
}

.price-breakdown__loading {
  padding: 8px 0;
}

.price-breakdown__skeleton {
  display: block;
  height: 16px;
  width: 180px;
  background: var(--color-skeleton, var(--color-surface-3));
  border-radius: var(--radius-sm);
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.price-breakdown__list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-breakdown__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-xs);
  color: var(--color-text-2);
}

.price-breakdown__row--base {
  color: var(--color-muted);
  font-style: italic;
}

.price-breakdown__label {
  color: var(--color-text-2);
}

.price-breakdown__modifier {
  font-family: var(--font-mono);
  font-weight: 600;
}

.price-breakdown__modifier.is-positive { color: var(--color-success); }
.price-breakdown__modifier.is-negative { color: var(--color-error); }

/* ─── Actions ───────────────────────────────────────── */
.product-buy-panel__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 480px) {
  .product-buy-panel__actions {
    flex-direction: row;
  }
}

/* ─── Trust badges ──────────────────────────────────── */
.product-buy-panel__trust {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

@media (min-width: 480px) {
  .product-buy-panel__trust {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

.trust-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-text-2);
  font-weight: 500;
}

/* ─── Buttons ───────────────────────────────────────── */
.product-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: var(--radius-md);
  font-weight: 700;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast),
    color var(--transition-fast);
  border: none;
  font-family: var(--font-sans);
  white-space: nowrap;
  text-decoration: none;
}

.product-btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
  font-size: var(--text-sm);
  padding: 12px 20px;
}

.product-btn--primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow-accent);
}

.product-btn--primary:active:not(:disabled) {
  transform: scale(0.97);
}

.product-btn--ghost {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-2);
  font-size: var(--text-sm);
  padding: 12px 20px;
}

.product-btn--ghost:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.product-btn--lg {
  padding: 14px 24px;
  font-size: var(--text-base);
}

.product-btn--md {
  padding: 10px 18px;
  font-size: var(--text-sm);
}

.product-btn--full {
  flex: 1;
  width: 100%;
}

.product-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Button spinner */
.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--color-on-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

/* ─── Section title ─────────────────────────────────── */
.product-section-title {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 0 0 24px;
  padding-left: 14px;
  border-left: 4px solid var(--color-accent);
  font-family: var(--font-sans);
}

/* ─── Description ───────────────────────────────────── */
.product-description,
.product-documentation {
  max-width: 800px;
  margin-inline: auto;
  width: 100%;
}

.product-description__content {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--color-text-2);
}

.product-description__plain {
  white-space: pre-wrap;
  margin: 0;
}

/* Prose styles for description_html */
.product-description__html :deep(h1),
.product-description__html :deep(h2),
.product-description__html :deep(h3),
.product-description__html :deep(h4) {
  color: var(--color-text);
  font-weight: 700;
  line-height: 1.3;
  margin: 1.5em 0 0.5em;
}

.product-description__html :deep(h2) {
  font-size: var(--text-xl);
}

.product-description__html :deep(h3) {
  font-size: var(--text-lg);
}

.product-description__html :deep(p) {
  margin-bottom: 1em;
}

.product-description__html :deep(ul),
.product-description__html :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1em;
}

.product-description__html :deep(li) {
  margin-bottom: 0.4em;
}

.product-description__html :deep(img) {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  margin: 1.5em auto;
  display: block;
}

.product-description__html :deep(iframe) {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: none;
  border-radius: var(--radius-lg);
  margin: 1.5em 0;
}

.product-description__html :deep(blockquote) {
  border-left: 4px solid var(--color-accent);
  padding-left: 1.2em;
  color: var(--color-muted);
  font-style: italic;
  margin: 1.5em 0;
}

.product-description__html :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5em 0;
}

.product-description__html :deep(th),
.product-description__html :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  text-align: left;
}

.product-description__html :deep(th) {
  background: var(--color-surface-2);
  font-weight: 700;
  color: var(--color-text);
}

/* TipTap viewer override for product description */
.product-description__tiptap :deep(.tiptap-viewer) {
  font-size: 1.1rem;
  line-height: 1.8;
}

/* ─── Attributes table ──────────────────────────────── */
.product-attributes {
  max-width: 800px;
  margin-inline: auto;
  width: 100%;
}

.attributes-table {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.attributes-table__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.attributes-table__row:last-child {
  border-bottom: none;
}

.attributes-table__row:nth-child(even) {
  background: var(--color-bg-subtle);
}

.attributes-table__row:nth-child(odd) {
  background: var(--color-surface);
}

.attributes-table__key {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  font-weight: 500;
}

.attributes-table__value {
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
}

/* ─── Sticky Buy Bar ────────────────────────────────── */
.sticky-buy-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: 12px 0;
  z-index: var(--z-overlay);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(12px);
}

.sticky-buy-bar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.sticky-buy-bar__product {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.sticky-buy-bar__image {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  object-fit: cover;
  flex-shrink: 0;
}

.sticky-buy-bar__info {
  display: none;
  min-width: 0;
}

@media (min-width: 480px) {
  .sticky-buy-bar__info {
    display: block;
  }
}

.sticky-buy-bar__name {
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
}

.sticky-buy-bar__price {
  font-size: var(--text-xs);
  color: var(--color-accent);
  font-weight: 600;
  font-family: var(--font-mono);
}

/* ─── Skeleton ──────────────────────────────────────── */
.product-skeleton {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

@media (min-width: 768px) {
  .product-skeleton {
    grid-template-columns: 3fr 2fr;
  }
}

.product-skeleton__gallery {
  aspect-ratio: 1 / 1;
  border-radius: var(--radius-xl);
}

.product-skeleton__info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 28px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
}

.product-skeleton__badge {
  height: 24px;
  width: 90px;
  border-radius: var(--radius-full);
}

.product-skeleton__title {
  height: 56px;
  border-radius: var(--radius-md);
}

.product-skeleton__price {
  height: 44px;
  width: 60%;
  border-radius: var(--radius-md);
}

.product-skeleton__btn {
  height: 52px;
  border-radius: var(--radius-md);
}

/* ─── Error ─────────────────────────────────────────── */
.product-error {
  padding: 80px 0;
  display: flex;
  justify-content: center;
}

.product-error__card {
  text-align: center;
  max-width: 420px;
  background: var(--color-surface);
  padding: 48px 40px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.product-error__title {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  margin: 24px 0 12px;
}

.product-error__text {
  color: var(--color-text-2);
  margin-bottom: 32px;
  font-size: var(--text-base);
}

/* ─── Transitions ───────────────────────────────────── */
.img-fade-enter-active,
.img-fade-leave-active {
  transition: opacity var(--transition-normal);
}

.img-fade-enter-from,
.img-fade-leave-to {
  opacity: 0;
}

.sticky-bar-enter-active,
.sticky-bar-leave-active {
  transition: transform var(--transition-normal);
}

.sticky-bar-enter-from,
.sticky-bar-leave-to {
  transform: translateY(100%);
}
</style>
