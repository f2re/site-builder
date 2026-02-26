<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '~/stores/cartStore'

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
          <NuxtLink to="/" @click="closeMenu">
            <span class="logo-text">WifiOBD<span class="logo-accent">.shop</span></span>
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
          <button
            class="btn btn-icon btn-ghost icon-btn"
            aria-label="Поиск"
            @click="isSearchOpen = true"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </button>

          <!-- Cart -->
          <NuxtLink to="/cart" class="cart-btn btn btn-icon btn-ghost icon-btn" aria-label="Корзина">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <path d="M16 10a4 4 0 0 1-8 0"/>
            </svg>
            <span v-if="cartCount > 0" class="cart-badge" aria-label="Товаров в корзине: {{ cartCount }}">
              {{ cartCount > 99 ? '99+' : cartCount }}
            </span>
          </NuxtLink>

          <!-- Theme toggle -->
          <UThemeToggle />

          <!-- Burger (mobile) -->
          <button
            class="burger btn btn-icon btn-ghost"
            :aria-expanded="isMenuOpen"
            aria-controls="mobile-menu"
            aria-label="Открыть меню"
            @click="isMenuOpen = !isMenuOpen"
          >
            <svg v-if="!isMenuOpen" xmlns="http://www.w3.org/2000/svg" width="22" height="22"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="6"  x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="22" height="22"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
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
        <div class="container">
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
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  height: 64px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: sticky;
  top: 0;
  z-index: var(--z-overlay);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo */
.logo-text {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
  transition: opacity var(--transition-fast);
}
.logo-text:hover { opacity: .8; }
.logo-accent { color: var(--color-accent); }

/* Desktop nav */
.nav {
  display: flex;
  gap: 4px;
}

.nav-link {
  color: var(--color-text-2);
  font-weight: 500;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  transition:
    color            var(--transition-fast),
    background-color var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text);
  background-color: var(--color-surface-2);
}

.nav-link.router-link-active {
  color: var(--color-accent);
  background-color: var(--color-surface-2);
}

/* Actions */
.actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-btn {
  position: relative;
  color: var(--color-text-2);
  transition:
    color            var(--transition-fast),
    background-color var(--transition-fast);
}
.icon-btn:hover { color: var(--color-text); }

/* Cart badge */
.cart-btn { position: relative; }

.cart-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  font-size: 10px;
  font-weight: 700;
  line-height: 1;
  padding: 2px 4px;
  border-radius: var(--radius-full);
  min-width: 16px;
  text-align: center;
  pointer-events: none;
}

/* Burger — visible only on mobile */
.burger { display: none; }

/* Mobile nav */
.mobile-nav {
  background-color: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: 12px 0 16px;
  position: absolute;
  top: 64px;
  left: 0;
  right: 0;
  z-index: var(--z-overlay);
  box-shadow: var(--shadow-card);
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  color: var(--color-text);
  font-weight: 500;
  font-size: var(--text-lg);
  border-bottom: 1px solid var(--color-border);
  transition: color var(--transition-fast);
}

.mobile-nav-link:last-child { border-bottom: none; }
.mobile-nav-link:hover { color: var(--color-accent); }

.cart-badge-inline {
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

/* Mobile menu transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Responsive */
@media (max-width: 768px) {
  .nav  { display: none; }
  .burger { display: flex; }
}
</style>
