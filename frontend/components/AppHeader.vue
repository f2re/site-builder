<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '~/stores/cartStore'
import { useAuthStore } from '~/stores/authStore'
import { useUserStore } from '~/stores/userStore'

const route = useRoute()
const cartStore = useCartStore()
const authStore = useAuthStore()
const userStore = useUserStore()
const userName = computed(() => userStore.user?.full_name)
watch(() => userStore.user, (u) => {
  console.log('[DEBUG] AppHeader: user changed', JSON.stringify(u))
}, { immediate: true, deep: true })
const isMenuOpen = ref(false)
const isSearchOpen = ref(false)

const cartCount = computed(() => cartStore.totalCount)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAdmin = computed(() => userStore.isAdmin)

const navLinks = [
  { to: '/products', label: 'Каталог', icon: 'ph:shopping-bag-bold' },
  { to: '/blog',     label: 'Блог',    icon: 'ph:article-bold' },
]

const closeMenu = () => { 
  isMenuOpen.value = false 
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

// Lock body scroll when menu is open
watch(isMenuOpen, (val) => {
  if (import.meta.client) {
    document.body.style.overflow = val ? 'hidden' : ''
  }
})

const handleLogout = () => {
  authStore.logout()
  closeMenu()
}

// Close menu on route change
watch(() => route.fullPath, () => {
  closeMenu()
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

          <!-- Account (Desktop) -->
          <div class="account-actions hide-mobile">
            <template v-if="isAuthenticated">
              <div class="auth-group">
                <div v-if="userName" class="user-greeting" data-testid="user-name">
                  <span>{{ userName }}</span>
                </div>
                <!-- Admin Dashboard Link -->
                <UButton
                  v-if="isAdmin"
                  variant="ghost"
                  size="sm"
                  to="/admin"
                  aria-label="Панель управления"
                  class="action-btn admin-btn"
                  title="Админ-панель"
                >
                  <template #icon>
                    <Icon name="ph:gauge-bold" size="20" />
                  </template>
                </UButton>

                <UButton
                  variant="ghost"
                  size="sm"
                  to="/profile"
                  aria-label="Личный кабинет"
                  class="action-btn profile-btn"
                  data-testid="user-menu"
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
                  data-testid="logout-btn"
                  @click="handleLogout"
                >
                  <template #icon>
                    <Icon name="ph:sign-out-bold" size="20" />
                  </template>
                </UButton>
              </div>
            </template>
            <div v-else class="auth-links">
              <UButton to="/auth/login" variant="ghost" size="sm" data-testid="login-link">Войти</UButton>
              <UButton to="/auth/register" variant="primary" size="sm">Регистрация</UButton>
            </div>
          </div>

          <!-- Theme toggle (Desktop) -->
          <div class="hide-mobile">
            <UThemeToggle />
          </div>

          <!-- Burger (mobile) -->
          <button
            class="burger-btn"
            :class="{ 'burger-btn--open': isMenuOpen }"
            :aria-expanded="isMenuOpen"
            aria-controls="mobile-menu"
            aria-label="Открыть меню"
            @click="toggleMenu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Search modal -->
    <USearchModal v-if="isSearchOpen" @close="isSearchOpen = false" />

    <!-- Mobile menu teleported to body -->
    <Teleport to="body">
      <!-- Overlay -->
      <Transition name="fade">
        <div v-if="isMenuOpen" class="mobile-nav-overlay" @click="closeMenu"></div>
      </Transition>

      <!-- Drawer -->
      <Transition name="mobile-menu">
        <nav
          v-if="isMenuOpen"
          id="mobile-menu"
          class="mobile-nav"
          aria-label="Мобильная навигация"
        >
          <div class="mobile-nav-content">
            <div class="mobile-nav-header">
               <span class="mobile-nav-title">Навигация</span>
               <UThemeToggle />
            </div>
            
            <div class="mobile-nav-links">
              <NuxtLink
                v-for="link in navLinks"
                :key="link.to"
                :to="link.to"
                class="mobile-nav-link"
                @click="closeMenu"
              >
                <div class="link-label">
                  <Icon :name="link.icon" size="24" />
                  <span>{{ link.label }}</span>
                </div>
                <Icon name="ph:caret-right-bold" size="16" class="caret" />
              </NuxtLink>
              
              <NuxtLink to="/cart" class="mobile-nav-link" @click="closeMenu">
                <div class="link-label">
                  <Icon name="ph:shopping-cart-bold" size="24" />
                  <span>Корзина</span>
                </div>
                <span v-if="cartCount > 0" class="cart-badge-inline">{{ cartCount }}</span>
              </NuxtLink>

              <div v-if="isAdmin" class="admin-divider">Администрирование</div>
              <NuxtLink v-if="isAdmin" to="/admin" class="mobile-nav-link admin-link" @click="closeMenu">
                <div class="link-label">
                  <Icon name="ph:gauge-bold" size="24" />
                  <span>Панель управления</span>
                </div>
                <Icon name="ph:caret-right-bold" size="16" class="caret" />
              </NuxtLink>
            </div>
            
            <div class="mobile-nav-footer">
              <template v-if="isAuthenticated">
                <NuxtLink to="/profile" class="mobile-auth-btn profile-btn" @click="closeMenu">
                  <Icon name="ph:user-circle-bold" size="24" />
                  <span>Личный кабинет</span>
                </NuxtLink>
                <button @click="handleLogout" class="mobile-auth-btn logout-btn">
                  <Icon name="ph:sign-out-bold" size="24" />
                  <span>Выйти из аккаунта</span>
                </button>
              </template>
              <template v-else>
                <div class="auth-grid">
                  <UButton to="/auth/login" variant="secondary" size="lg" class="w-full">Войти</UButton>
                  <UButton to="/auth/register" variant="primary" size="lg" class="w-full">Регистрация</UButton>
                </div>
              </template>
            </div>
          </div>
        </nav>
      </Transition>
    </Teleport>
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
  z-index: 50;
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
}

.logo-indicator {
  height: 3px;
  width: 100%;
  background: linear-gradient(90deg, var(--color-accent), var(--color-neon));
  border-radius: var(--radius-full);
  margin-top: -2px;
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
}

.admin-btn:hover {
  color: var(--color-accent);
}

/* Burger Button */
.burger-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  width: 40px;
  height: 40px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  padding: 0 10px;
  z-index: var(--z-modal);
  transition: all var(--transition-fast);
}

.burger-btn span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--color-text);
  border-radius: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.burger-btn--open {
  background: var(--color-surface-3);
  border-color: var(--color-accent);
}

.burger-btn--open span:nth-child(1) { transform: translateY(8px) rotate(45deg); }
.burger-btn--open span:nth-child(2) { opacity: 0; transform: translateX(10px); }
.burger-btn--open span:nth-child(3) { transform: translateY(-8px) rotate(-45deg); }

/* Mobile nav */
.mobile-nav-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-overlay);
  backdrop-filter: blur(8px);
  z-index: 10000;
}

.mobile-nav {
  position: fixed;
  top: 0;
  right: 0;
  width: 85%;
  max-width: 320px;
  height: 100vh;
  background-color: var(--color-bg);
  z-index: 10001;
  box-shadow: -10px 0 30px rgba(0,0,0,0.3);
  border-left: 1px solid var(--color-border);
}

.mobile-nav-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 80px 20px 40px;
}

.mobile-nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.mobile-nav-title {
  font-size: var(--text-xs);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-muted);
}

.mobile-nav-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text);
  text-decoration: none;
  font-weight: 700;
  transition: all var(--transition-fast);
}

.mobile-nav-link:active {
  transform: scale(0.98);
  border-color: var(--color-accent);
}

.link-label {
  display: flex;
  align-items: center;
  gap: 16px;
}

.caret {
  color: var(--color-muted);
  transition: transform var(--transition-fast);
}

.mobile-nav-link:hover .caret {
  color: var(--color-accent);
  transform: translateX(4px);
}

.admin-divider {
  margin: 24px 0 8px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--color-accent);
  letter-spacing: 0.1em;
}

.admin-link {
  border-color: var(--color-accent-glow);
}

.mobile-nav-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-auth-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-lg);
  font-weight: 700;
  text-decoration: none;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.profile-btn {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.logout-btn {
  background: var(--color-error-bg);
  color: var(--color-error);
  border-color: var(--color-error-bg);
}

.auth-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.cart-badge-inline {
  background-color: var(--color-accent);
  color: var(--color-on-accent);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 800;
}

/* Transitions */
.mobile-menu-enter-active, .mobile-menu-leave-active {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu-enter-from, .mobile-menu-leave-to {
  transform: translateX(100%);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 900px) {
  .hide-mobile { display: none; }
}

@media (max-width: 768px) {
  .nav { display: none; }
  .burger-btn { display: flex; }
}

.w-full { width: 100%; }
</style>
