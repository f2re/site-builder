<script setup lang="ts">
import { ref } from 'vue'
import type { DeliveryAddress, CreateAddressRequest } from '~/composables/useAddresses'

const props = defineProps<{
  address?: DeliveryAddress
  pending?: boolean
}>()

const emit = defineEmits<{
  submit: [data: CreateAddressRequest]
  cancel: []
}>()

const form = ref<CreateAddressRequest>({
  name: props.address?.name || '',
  recipient_name: props.address?.recipient_name || '',
  recipient_phone: props.address?.recipient_phone || '',
  address_type: props.address?.address_type || 'home',
  full_address: props.address?.full_address || '',
  city: props.address?.city || '',
  postal_code: props.address?.postal_code || '',
  provider: props.address?.provider || 'cdek',
  pickup_point_code: props.address?.pickup_point_code || '',
  is_default: props.address?.is_default || false
})

const handleSubmit = () => {
  emit('submit', form.value)
}
</script>

<template>
  <form class="address-form" data-testid="address-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label class="form-label" for="addr-name">Название адреса</label>
      <input
        id="addr-name"
        v-model="form.name"
        type="text"
        class="form-input"
        placeholder="Дом, Офис, и т.д."
        required
        data-testid="address-name-input"
      />
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="recipient-name">Получатель</label>
        <input
          id="recipient-name"
          v-model="form.recipient_name"
          type="text"
          class="form-input"
          required
          data-testid="recipient-name-input"
        />
      </div>
      <div class="form-group">
        <label class="form-label" for="recipient-phone">Телефон</label>
        <input
          id="recipient-phone"
          v-model="form.recipient_phone"
          type="tel"
          class="form-input"
          required
          data-testid="recipient-phone-input"
        />
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="city">Город</label>
      <input
        id="city"
        v-model="form.city"
        type="text"
        class="form-input"
        required
        data-testid="city-input"
      />
    </div>

    <div class="form-group">
      <label class="form-label" for="full-address">Адрес</label>
      <input
        id="full-address"
        v-model="form.full_address"
        type="text"
        class="form-input"
        required
        data-testid="full-address-input"
      />
    </div>

    <div class="form-row">
      <div class="form-group">
        <label class="form-label" for="provider">Служба доставки</label>
        <select id="provider" v-model="form.provider" class="form-select" data-testid="provider-select">
          <option value="cdek">СДЭК</option>
          <option value="pochta">Почта РФ</option>
          <option value="ozon">Ozon</option>
          <option value="wb">Wildberries</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label" for="postal-code">Индекс</label>
        <input
          id="postal-code"
          v-model="form.postal_code"
          type="text"
          class="form-input"
          data-testid="postal-code-input"
        />
      </div>
    </div>

    <div class="form-group">
      <label class="form-checkbox">
        <input v-model="form.is_default" type="checkbox" data-testid="is-default-checkbox" />
        <span>Сделать адресом по умолчанию</span>
      </label>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn--primary" :disabled="pending" data-testid="submit-address-btn">
        <Icon v-if="pending" name="ph:spinner-gap-bold" size="16" class="spin" />
        {{ pending ? 'Сохранение...' : 'Сохранить' }}
      </button>
      <button type="button" class="btn btn--secondary" data-testid="cancel-address-btn" @click="emit('cancel')">
        Отмена
      </button>
    </div>
  </form>
</template>

<style scoped>
.address-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 16px;
  transition: border-color var(--transition-fast);
  outline: none;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text-2);
}

.form-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: var(--text-sm);
  cursor: pointer;
  border: none;
  transition: background var(--transition-fast), transform var(--transition-fast);
  min-height: 44px;
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--secondary {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-2);
}

.btn--secondary:hover {
  background: var(--color-surface-2);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
