<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '~/stores/cartStore'
import UButton from './U/UButton.vue'
import UThemeToggle from './U/UThemeToggle.vue'
import USearchModal from './U/USearchModal.vue'

const route = useRoute()
const cartStore = useCartStore()
const isMenuOpen = ref(false)
const isSearchOpen = ref(false)

const cartCount = computed(() => cartStore.totalCount)

const navLinks = [
  { to: '/products', label: 'Каталог' },
  { to: '/blog',     label: 'Блог'    },
]

const closeMenu = () => { isMenuOpen.value = false }
</script>

<template>
  <header class="header">
    <div class="container">
      <div class="header-inner">

        <!-- Logo -->
        <div class="logo">
          <NuxtLink to="/" @click="closeMenu" class="logo-link">
            <span class="logo-text">WIFI<span class="logo-accent">OBD</span></span>
            <div class="logo-indicator"></div>
          </NuxtLink>
        </div>

        <!-- Desktop nav -->
        <nav class="nav" aria-label="Основная навигация">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="nav-link"
          >
            {{ link.label }}
          </NuxtLink>
        </nav>

        <!-- Actions -->
        <div class="actions">
          <!-- Search -->
          <UButton
            variant="ghost"
            size="sm"
            aria-label="Поиск"
            class="action-btn"
            @click="isSearchOpen = true"
          >
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </template>
          </UButton>

          <!-- Cart -->
          <UButton
            variant="ghost"
            size="sm"
            to="/cart"
            aria-label="Корзина"
            class="action-btn cart-btn"
          >
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                <line x1="3" y1="6" x2="21" y2="6"/>
                <path d="M16 10a4 4 0 0 1-8 0"/>
              </svg>
            </template>
            <span v-if="cartCount > 0" class="cart-badge">
              {{ cartCount > 99 ? '99+' : cartCount }}
            </span>
          </UButton>

          <!-- Theme toggle -->
          <UThemeToggle />

          <!-- Burger (mobile) -->
          <button
            class="burger-btn"
            :class="{ 'burger-btn--open': isMenuOpen }"
            :aria-expanded="isMenuOpen"
            aria-controls="mobile-menu"
            aria-label="Открыть меню"
            @click="isMenuOpen = !isMenuOpen"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <Transition name="mobile-menu">
      <nav
        v-if="isMenuOpen"
        id="mobile-menu"
        class="mobile-nav"
        aria-label="Мобильная навигация"
      >
        <div class="container mobile-nav-container">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="mobile-nav-link"
            @click="closeMenu"
          >
            {{ link.label }}
          </NuxtLink>
          <NuxtLink to="/cart" class="mobile-nav-link" @click="closeMenu">
            Корзина
            <span v-if="cartCount > 0" class="cart-badge-inline">{{ cartCount }}</span>
          </NuxtLink>
        </div>
      </nav>
    </Transition>

    <!-- Search modal -->
    <USearchModal v-if="isSearchOpen" @close="isSearchOpen = false" />
  </header>
</template>

<style scoped>
.header {
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  height: 72px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: var(--z-overlay);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo */
.logo-link {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  position: relative;
}

.logo-text {
  font-size: 24px;
  font-weight: 900;
  color: var(--color-text);
  letter-spacing: -1px;
  font-family: var(--font-sans);
}

.logo-accent {
  color: var(--color-accent);
  text-shadow: 0 0 10px var(--color-accent-glow);
}

.logo-indicator {
  height: 3px;
  width: 100%;
  background: linear-gradient(90deg, var(--color-accent), var(--color-neon));
  border-radius: var(--radius-full);
  margin-top: -2px;
  box-shadow: 0 2px 8px var(--color-accent-glow);
}

/* Desktop nav */
.nav {
  display: flex;
  gap: 8px;
  background-color: var(--color-surface-2);
  padding: 4px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.nav-link {
  color: var(--color-text-2);
  font-weight: 600;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
  font-size: var(--text-sm);
}

.nav-link:hover {
  color: var(--color-text);
  background-color: var(--color-surface-3);
}

.nav-link.router-link-active {
  color: var(--color-on-accent);
  background-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* Actions */
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cart-btn {
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  font-size: 10px;
  font-weight: 800;
  padding: 2px 5px;
  border-radius: var(--radius-full);
  min-width: 18px;
  border: 2px solid var(--color-bg);
  box-shadow: 0 0 10px var(--color-accent-glow);
}

/* Burger Button */
.burger-btn {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 32px;
  height: 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 10;
}

.burger-btn span {
  width: 32px;
  height: 3px;
  background: var(--color-text);
  border-radius: 10px;
  transition: all 0.3s linear;
  position: relative;
  transform-origin: 1px;
}

.burger-btn--open span:first-child { transform: rotate(45deg); }
.burger-btn--open span:nth-child(2) { opacity: 0; transform: translateX(20px); }
.burger-btn--open span:last-child { transform: rotate(-45deg); }

/* Mobile nav */
.mobile-nav {
  position: fixed;
  top: 72px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-bg);
  z-index: var(--z-overlay);
  padding: 24px 0;
}

.mobile-nav-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mobile-nav-link {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text);
  text-decoration: none;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mobile-nav-link:hover {
  color: var(--color-accent);
}

.cart-badge-inline {
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
}

/* Transitions */
.mobile-menu-enter-active, .mobile-menu-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu-enter-from, .mobile-menu-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 768px) {
  .nav { display: none; }
  .burger-btn { display: flex; }
}
</style>
