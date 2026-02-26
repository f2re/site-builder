<script setup lang="ts">
import { onMounted } from 'vue'
import { useCartStore } from '~/stores/cartStore'

useSeoMeta({
  title: 'Корзина — WifiOBD Shop',
})

const cartStore = useCartStore()
onMounted(() => cartStore.init())

const formatPrice = (p: number) =>
  p.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 })
</script>

<template>
  <div class="cart-page">
    <h1 class="page-title">Корзина</h1>

    <!-- Empty state -->
    <div v-if="cartStore.items.length === 0" class="empty-state">
      <div class="empty-icon" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <path d="M16 10a4 4 0 0 1-8 0"/>
        </svg>
      </div>
      <h2 class="empty-title">Корзина пуста</h2>
      <p class="empty-sub">Добавьте товары из каталога, чтобы оформить заказ</p>
      <NuxtLink to="/products" class="btn btn-primary">Перейти в каталог</NuxtLink>
    </div>

    <!-- Cart items -->
    <div v-else class="cart-layout">
      <div class="cart-items">
        <div
          v-for="item in cartStore.items"
          :key="item.id"
          class="cart-item"
        >
          <div class="item-info">
            <p class="item-name">{{ item.name }}</p>
            <p class="item-price">{{ formatPrice(item.price) }}</p>
          </div>
          <div class="item-controls">
            <button
              class="btn btn-icon btn-ghost qty-btn"
              aria-label="Уменьшить количество"
              @click="cartStore.updateQuantity(item.id, item.quantity - 1)"
            >−</button>
            <span class="item-qty">{{ item.quantity }}</span>
            <button
              class="btn btn-icon btn-ghost qty-btn"
              aria-label="Увеличить количество"
              @click="cartStore.updateQuantity(item.id, item.quantity + 1)"
            >+</button>
            <button
              class="btn btn-icon btn-ghost remove-btn"
              aria-label="Удалить товар"
              @click="cartStore.removeItem(item.id)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                aria-hidden="true">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6l-1 14H6L5 6"/>
                <path d="M10 11v6M14 11v6"/>
                <path d="M9 6V4h6v2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="cart-summary">
        <h2 class="summary-title">Итого</h2>
        <div class="summary-row">
          <span>Товары ({{ cartStore.totalCount }} шт.)</span>
          <span>{{ formatPrice(cartStore.totalPrice) }}</span>
        </div>
        <div class="summary-row">
          <span>Доставка</span>
          <span class="text-accent">Бесплатно</span>
        </div>
        <div class="summary-total">
          <span>К оплате</span>
          <span>{{ formatPrice(cartStore.totalPrice) }}</span>
        </div>
        <button class="btn btn-primary btn-full" @click="() => {}">
          Оформить заказ
        </button>
        <button class="btn btn-ghost btn-full clear-btn" @click="cartStore.clearCart()">
          Очистить корзину
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-bottom: 32px;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  color: var(--color-muted);
  opacity: .5;
}

.empty-title {
  font-size: var(--text-xl);
  font-weight: 700;
}

.empty-sub {
  color: var(--color-text-2);
  font-size: var(--text-base);
}

/* Cart layout */
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
  align-items: start;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cart-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
}
.cart-item:hover { border-color: var(--color-border-strong); }

.item-name {
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.item-price {
  color: var(--color-accent);
  font-weight: 700;
  font-family: var(--font-mono);
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.qty-btn {
  font-size: var(--text-lg);
  font-weight: 700;
}

.item-qty {
  min-width: 28px;
  text-align: center;
  font-weight: 600;
}

.remove-btn { color: var(--color-error); }
.remove-btn:hover { background-color: var(--color-error-bg); }

/* Summary */
.cart-summary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  position: sticky;
  top: 80px;
}

.summary-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--color-text-2);
  margin-bottom: 10px;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--color-text);
  margin: 16px 0 20px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.btn-full {
  width: 100%;
  margin-bottom: 8px;
  justify-content: center;
}

.clear-btn { color: var(--color-muted); font-size: var(--text-sm); }

@media (max-width: 768px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .cart-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
