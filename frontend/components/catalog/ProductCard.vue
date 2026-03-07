<script setup lang="ts">
import type { Product, ProductShort } from '~/composables/useProducts'
import { useCartStore } from '~/stores/cartStore'
import { useToast } from '~/composables/useToast'
import { formatPrice } from '~/composables/useFormatters'

const props = defineProps<{
  product: Product | ProductShort
}>()

const cartStore = useCartStore()
const toast = useToast()

const imageUrl = computed(() => {
  if ('images' in props.product && props.product.images?.length) {
    return props.product.images[0].url
  }
  return (props.product as ProductShort).main_image_url || '/placeholder-product.png'
})

const handleAddToCart = () => {
  if (props.product.stock <= 0) return

  const added = cartStore.addItem({
    id: props.product.id as any,
    name: props.product.name,
    price: props.product.price_display,
    image: imageUrl.value,
    maxStock: props.product.stock
  })

  if (added === false) {
    toast.warning('Недостаточно товара', `В наличии только ${props.product.stock} шт.`)
  } else {
    toast.success('Добавлено', `${props.product.name} теперь в корзине`)
  }
}
</script>

<template>
  <NuxtLink :to="`/products/${product.slug}`" class="product-card" data-testid="product-card">
    <div class="product-card__image-wrapper">
      <NuxtImg
        :src="imageUrl"
        :alt="product.name"
        class="product-card__image"
        loading="lazy"
        format="webp"
        width="300"
        height="300"
        fit="cover"
      />
      <div v-if="product.stock <= 0" class="product-card__badge product-card__badge--out-of-stock" data-testid="product-stock">
        Нет в наличии
      </div>
    </div>

    <div class="product-card__content">
      <div class="product-card__category">{{ product.category?.name }}</div>
      <h3 class="product-card__title" data-testid="product-title">{{ product.name }}</h3>

      <div class="product-card__footer">
        <div class="product-card__price">
          <span class="product-card__price-value" data-testid="product-price">{{ formatPrice(product.price_display) }}</span>
        </div>

        <button
          class="product-card__add"
          :disabled="product.stock <= 0"
          @click.prevent="handleAddToCart"
          aria-label="Добавить в корзину"
        >
          <Icon name="ph:plus-bold" size="20" />
        </button>
      </div>
    </div>
  </NuxtLink>
</template>

<style scoped>
.product-card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition:
    transform var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
  text-decoration: none;
  color: inherit;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-4px);
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.product-card__image-wrapper {
  position: relative;
  aspect-ratio: 1 / 1;
  background: var(--color-bg-subtle);
  overflow: hidden;
}

.product-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.product-card:hover .product-card__image {
  transform: scale(1.05);
}

.product-card__badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  z-index: 1;
}

.product-card__badge--out-of-stock {
  background: var(--color-surface-2);
  color: var(--color-muted);
  border: 1px solid var(--color-border);
  backdrop-filter: blur(4px);
}

.product-card__content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.product-card__category {
  font-size: var(--text-xs);
  color: var(--color-muted);
  margin-bottom: 4px;
}

.product-card__title {
  font-size: var(--text-base);
  font-weight: 600;
  line-height: 1.4;
  margin: 0 0 16px;
  color: var(--color-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card__footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.product-card__price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.product-card__price-value {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
}

.product-card__price-currency {
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.product-card__add {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: var(--color-on-accent);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    background var(--transition-fast),
    transform var(--transition-fast);
}

.product-card__add:hover {
  background: var(--color-accent-hover);
  transform: scale(1.1);
}

.product-card__add:active {
  transform: scale(0.95);
}

.product-card__add:disabled {
  background: var(--color-surface-3);
  color: var(--color-muted);
  cursor: not-allowed;
  transform: none;
}
</style>
