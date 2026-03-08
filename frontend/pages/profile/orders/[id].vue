<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useIntervalFn } from '@vueuse/core'
import { useOrders, type Order } from '~/composables/useOrders'
import { useProducts } from '~/composables/useProducts'
import { useCartStore } from '~/stores/cartStore'
import OrderStatus from '~/components/shop/OrderStatus.vue'
import { useConfirm } from '~/composables/useConfirm'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id as string
const { getOrder, cancelOrder } = useOrders()
const { getProductBySlug } = useProducts()
const cartStore = useCartStore()
const { confirm } = useConfirm()

const { data: order, refresh, error, pending } = await getOrder(orderId)

const isCancelling = ref(false)
const isRepeating = ref(false)

// Polling every 30s to check for status updates (e.g. PAID)
const { pause, resume } = useIntervalFn(() => {
  if (order.value && !['delivered', 'cancelled', 'refunded'].includes(order.value.status)) {
    refresh()
  }
}, 30000)

useHead({
  title: `Заказ #${orderId.split('-')[0].toUpperCase()} — WifiOBD`,
  meta: [
    { name: 'robots', content: 'noindex' }
  ]
})

const breadcrumbs = computed(() => [
  { label: 'Главная', to: '/' },
  { label: 'Мои заказы', to: '/profile/orders' },
  { label: `Заказ #${orderId.split('-')[0].toUpperCase()}`, to: `/profile/orders/${orderId}` },
])

const handleCancel = async () => {
  if (!await confirm({ title: 'Отменить заказ?', message: 'Вы уверены, что хотите отменить этот заказ?', confirmLabel: 'Да, отменить', variant: 'danger' })) return
  
  isCancelling.value = true
  try {
    await cancelOrder(orderId)
    await refresh()
  } catch (err) {
    console.error('Failed to cancel order:', err)
  } finally {
    isCancelling.value = false
  }
}

const handleRepeatOrder = async () => {
  if (!order.value) return
  
  isRepeating.value = true
  try {
    for (const item of order.value.items) {
      const { data: product } = await getProductBySlug(item.slug)
      if (product.value) {
        const cartItem = {
          id: product.value.id,
          name: product.value.name,
          price: product.value.variants[0]?.price || 0,
          image: product.value.images.find(img => img.is_cover)?.url || product.value.images[0]?.url
        }
        for (let i = 0; i < item.quantity; i++) {
          cartStore.addItem(cartItem)
        }
      }
    }
    router.push('/cart')
  } catch (err) {
    console.error('Failed to repeat order:', err)
  } finally {
    isRepeating.value = false
  }
}
</script>

<template>
  <div class="order-detail-page">
    <div class="container">
      <AppBreadcrumbs :crumbs="breadcrumbs" />
      
      <h1 class="page-title mt-4">Заказ #{{ orderId.split('-')[0].toUpperCase() }}</h1>
      <ProfileNav />

      <div v-if="pending && !order" class="loading-state">
        <USkeleton height="400px" style="border-radius: var(--radius-lg)" />
      </div>

      <div v-else-if="error" class="error-state">
        <h1 class="page-title">Заказ не найден</h1>
        <p>К сожалению, мы не смогли найти информацию о заказе #{{ orderId }}</p>
        <UButton to="/profile/orders" variant="primary" class="mt-8">К моим заказам</UButton>
      </div>

      <div v-else-if="order" class="order-content">
        <div class="order-header-flex">
          <div class="order-header">
            <div class="order-date">от {{ new Date(order.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }) }}</div>
          </div>
          <div class="header-actions">
            <UButton 
              v-if="order.status === 'pending' || order.status === 'awaiting_payment'" 
              variant="ghost" 
              color="error" 
              size="sm"
              :loading="isCancelling"
              @click="handleCancel"
            >
              Отменить заказ
            </UButton>
            <UButton 
              variant="ghost" 
              size="sm"
              :loading="isRepeating"
              @click="handleRepeatOrder"
            >
              Повторить заказ
            </UButton>
          </div>
        </div>

        <UCard class="status-card">
          <OrderStatus :status="order.status" />
          
          <div v-if="order.status === 'pending' && order.payment_url" class="payment-prompt mt-6">
            <div class="prompt-text">
              <p>Заказ ожидает оплаты. Пожалуйста, оплатите его, чтобы мы могли приступить к обработке.</p>
            </div>
            <UButton :to="order.payment_url" variant="primary" external class="pay-btn">
              Оплатить {{ order.total_rub }} ₽
            </UButton>
          </div>
        </UCard>

        <div class="order-grid">
          <div class="order-info-col">
            <UCard class="items-card">
              <h2 class="section-title">Состав заказа</h2>
              <div class="items-list">
                <div v-for="item in order.items" :key="item.product_id" class="order-item">
                  <div class="item-details">
                    <div class="item-name">{{ item.name }}</div>
                    <div class="item-meta">Количество: {{ item.quantity }}</div>
                  </div>
                  <div class="item-price">{{ item.price_rub * item.quantity }} ₽</div>
                </div>
              </div>
              <div class="order-total-row">
                <span>Итого к оплате</span>
                <span class="total-value">{{ order.total_rub }} ₽</span>
              </div>
            </UCard>
          </div>

          <div class="order-sidebar-col">
            <UCard class="delivery-card">
              <h2 class="section-title">Доставка</h2>
              <div class="delivery-info">
                <div class="info-group">
                  <div class="info-label">Способ:</div>
                  <div class="info-value">{{ order.delivery.type === 'cdek_pvz' ? 'Пункт выдачи СДЭК' : 'Доставка курьером' }}</div>
                </div>
                
                <div class="info-group">
                  <div class="info-label">Адрес:</div>
                  <div class="info-value">{{ order.delivery.address || '—' }}</div>
                </div>
                
                <div v-if="order.delivery.pvz_code" class="info-group">
                  <div class="info-label">Пункт выдачи:</div>
                  <div class="info-value">Код: {{ order.delivery.pvz_code }}</div>
                </div>
              </div>
            </UCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-detail-page {
  padding: 40px 0;
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
  letter-spacing: -1px;
}

.order-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  margin-top: 24px;
}

.order-date {
  color: var(--color-muted);
  font-size: var(--text-sm);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.status-card {
  margin-bottom: 32px;
  padding: 32px;
}

.payment-prompt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.prompt-text p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.order-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 32px;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 24px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.item-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.item-meta {
  font-size: var(--text-xs);
  color: var(--color-muted);
}

.item-price {
  font-weight: 700;
}

.order-total-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xl);
  font-weight: 800;
}

.total-value {
  color: var(--color-accent);
}

.delivery-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-label {
  font-size: var(--text-xs);
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 600;
}

.mt-4 { margin-top: 16px; }
.mt-6 { margin-top: 24px; }
.mt-8 { margin-top: 32px; }

@media (max-width: 1200px) {
  .order-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .order-header-flex {
    flex-direction: column;
    gap: 20px;
  }
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  .header-actions > * {
    flex: 1;
  }
  .payment-prompt {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  .pay-btn {
    width: 100%;
  }
}
</style>
