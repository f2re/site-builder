<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '~/stores/cartStore'
import { useAuthStore } from '~/stores/authStore'
import UButton from './U/UButton.vue'
import UThemeToggle from './U/UThemeToggle.vue'
import USearchModal from './U/USearchModal.vue'

const route = useRoute()
const cartStore = useCartStore()
const authStore = useAuthStore()
const isMenuOpen = ref(false)
const isSearchOpen = ref(false)

const cartCount = computed(() => cartStore.totalCount)
const isAuthenticated = computed(() => authStore.isAuthenticated)

const navLinks = [
  { to: '/products', label: 'Каталог' },
  { to: '/blog',     label: 'Блог'    },
]

const closeMenu = () => { isMenuOpen.value = false }

const handleLogout = () => {
  authStore.logout()
  closeMenu()
  navigateTo('/')
}

// Watch for route changes to close menu
watch(() => route.path, () => {
  closeMenu()
})

// Body scroll lock
watch(isMenuOpen, (val) => {
  if (import.meta.client) {
    document.body.style.overflow = val ? 'hidden' : ''
  }
})
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
              <Icon name="ph:magnifying-glass-bold" size="20" />
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
              <Icon name="ph:shopping-cart-simple-bold" size="20" />
            </template>
            <span v-if="cartCount > 0" class="cart-badge">
              {{ cartCount > 99 ? '99+' : cartCount }}
            </span>
          </UButton>

          <!-- Account -->
          <div class="account-actions hide-mobile">
            <template v-if="isAuthenticated">
              <div class="auth-group">
                <UButton
                  variant="ghost"
                  size="sm"
                  to="/profile"
                  aria-label="Личный кабинет"
                  class="action-btn profile-btn"
                >
                  <template #icon>
                    <Icon name="ph:user-bold" size="20" />
                  </template>
                </UButton>
                <UButton
                  variant="ghost"
                  size="sm"
                  aria-label="Выйти"
                  class="action-btn logout-btn"
                  @click="handleLogout"
                >
                  <template #icon>
                    <Icon name="ph:sign-out-bold" size="20" />
                  </template>
                </UButton>
              </div>
            </template>
            <div v-else class="auth-links">
              <UButton to="/auth/login" variant="ghost" size="sm">Войти</UButton>
              <UButton to="/auth/register" variant="primary" size="sm">Регистрация</UButton>
            </div>
          </div>

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
    <Teleport to="body">
      <Transition name="mobile-menu-overlay">
        <div v-if="isMenuOpen" class="mobile-nav-overlay" @click="closeMenu"></div>
      </Transition>
      
      <Transition name="mobile-menu">
        <nav
          v-if="isMenuOpen"
          id="mobile-menu"
          class="mobile-nav"
          aria-label="Мобильная навигация"
        >
          <div class="mobile-nav-header">
            <span class="logo-text">WIFI<span class="logo-accent">OBD</span></span>
            <button class="close-menu-btn" @click="closeMenu" aria-label="Закрыть меню">
              <Icon name="ph:x-bold" size="24" />
            </button>
          </div>

          <div class="container mobile-nav-container">
            <NuxtLink
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to"
              class="mobile-nav-link"
              @click="closeMenu"
            >
              {{ link.label }}
              <Icon name="ph:caret-right-bold" size="18" class="link-arrow" />
            </NuxtLink>
            <NuxtLink to="/cart" class="mobile-nav-link" @click="closeMenu">
              <div class="link-label-with-badge">
                Корзина
                <span v-if="cartCount > 0" class="cart-badge-inline">{{ cartCount }}</span>
              </div>
              <Icon name="ph:caret-right-bold" size="18" class="link-arrow" />
            </NuxtLink>
            
            <div class="mobile-auth-section">
              <template v-if="isAuthenticated">
                <NuxtLink to="/profile" class="mobile-nav-link" @click="closeMenu">
                  Личный кабинет
                  <Icon name="ph:caret-right-bold" size="18" class="link-arrow" />
                </NuxtLink>
                <button @click="handleLogout" class="mobile-nav-link logout-link">
                  Выйти
                  <Icon name="ph:sign-out-bold" size="18" class="link-arrow" />
                </button>
              </template>
              <template v-else>
                <NuxtLink to="/auth/login" class="mobile-nav-link" @click="closeMenu">
                  Войти
                  <Icon name="ph:sign-in-bold" size="18" class="link-arrow" />
                </NuxtLink>
                <NuxtLink to="/auth/register" class="mobile-nav-link" @click="closeMenu">
                  Регистрация
                  <Icon name="ph:user-plus-bold" size="18" class="link-arrow" />
                </NuxtLink>
              </template>
            </div>
          </div>
          
          <div class="mobile-nav-footer">
            <UThemeToggle />
            <span class="theme-label">Сменить тему</span>
          </div>
        </nav>
      </Transition>
    </Teleport>

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

.auth-links {
  display: flex;
  gap: 8px;
  align-items: center;
}

.auth-group {
  display: flex;
  gap: 4px;
  align-items: center;
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

.logout-btn:hover {
  color: var(--color-error);
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
.mobile-nav-overlay {
  position: fixed;
  inset: 0;
  background-color: var(--color-overlay);
  backdrop-filter: blur(4px);
  z-index: calc(var(--z-overlay) + 10);
}

.mobile-nav {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 85%;
  max-width: 400px;
  background-color: var(--color-bg);
  z-index: calc(var(--z-overlay) + 20);
  box-shadow: -10px 0 30px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--color-border);
}

.mobile-nav-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-menu-btn {
  background: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  padding: 4px;
}

.mobile-nav-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
}

.mobile-nav-link {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border-strong);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color var(--transition-fast);
}

.mobile-nav-link:active {
  background-color: var(--color-surface-2);
}

.link-arrow {
  color: var(--color-muted);
  opacity: 0.5;
}

.link-label-with-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-auth-section {
  margin-top: 24px;
  border-top: 8px solid var(--color-surface-2);
}

.logout-link {
  color: var(--color-error);
  text-align: left;
  background: none;
  width: 100%;
}

.cart-badge-inline {
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 800;
}

.mobile-nav-footer {
  padding: 24px;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-2);
}

/* Transitions */
.mobile-menu-enter-active, .mobile-menu-leave-active {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu-enter-from, .mobile-menu-leave-to {
  transform: translateX(100%);
}

.mobile-menu-overlay-enter-active, .mobile-menu-overlay-leave-active {
  transition: opacity 0.3s ease;
}
.mobile-menu-overlay-enter-from, .mobile-menu-overlay-leave-to {
  opacity: 0;
}

@media (max-width: 900px) {
  .hide-mobile { display: none; }
}

@media (max-width: 768px) {
  .nav { display: none; }
  .burger-btn { display: flex; }
}
</style>
