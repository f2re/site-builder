<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMobileMenuOpen = ref(false)

const navItems = [
  { label: 'Дашборд', icon: 'ph:chart-line-bold', to: '/admin' },
  { label: 'Пользователи', icon: 'ph:users-bold', to: '/admin/users' },
  { label: 'Товары', icon: 'ph:package-bold', to: '/admin/products' },
  { label: 'Категории', icon: 'ph:folders-bold', to: '/admin/products/categories' },
  { label: 'Заказы', icon: 'ph:shopping-cart-bold', to: '/admin/orders' },
  { label: 'Блог', icon: 'ph:article-bold', to: '/admin/blog' },
  { label: 'Страницы', icon: 'ph:files-bold', to: '/admin/pages' },
  { label: 'Миграция', icon: 'ph:database-bold', to: '/admin/migration' },
  { label: 'Назад на сайт', icon: 'ph:arrow-left-bold', to: '/' },
]

// Close mobile menu on route change
watch(() => route.fullPath, () => {
  isMobileMenuOpen.value = false
})

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
</script>

<template>
  <div class="admin-layout">
    <!-- Desktop Sidebar -->
    <aside class="admin-sidebar desktop-only">
      <div class="logo">
        <span class="logo-text">ADMIN<span class="dot">.</span></span>
      </div>
      
      <nav class="admin-nav">
        <NuxtLink 
          v-for="item in navItems" 
          :key="item.to" 
          :to="item.to" 
          class="nav-item"
          active-class="active"
          :exact="item.to === '/admin'"
        >
          <Icon :name="item.icon" size="20" />
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>
      
      <div class="admin-footer">
        <UThemeToggle />
      </div>
    </aside>

    <!-- Mobile Drawer Overlay -->
    <Transition name="fade">
      <div v-if="isMobileMenuOpen" class="mobile-overlay" @click="isMobileMenuOpen = false" />
    </Transition>

    <!-- Mobile Drawer -->
    <Transition name="slide">
      <aside v-if="isMobileMenuOpen" class="admin-sidebar mobile-drawer">
        <div class="logo">
          <span class="logo-text">ADMIN<span class="dot">.</span></span>
          <button class="close-btn" @click="isMobileMenuOpen = false">
            <Icon name="ph:x-bold" size="24" />
          </button>
        </div>
        
        <nav class="admin-nav">
          <NuxtLink 
            v-for="item in navItems" 
            :key="item.to" 
            :to="item.to" 
            class="nav-item"
            active-class="active"
            :exact="item.to === '/admin'"
          >
            <Icon :name="item.icon" size="20" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>
        
        <div class="admin-footer">
          <UThemeToggle />
        </div>
      </aside>
    </Transition>
    
    <main class="admin-main">
      <header class="admin-header">
        <div class="header-left">
          <button class="menu-btn mobile-only" @click="toggleMobileMenu">
            <Icon name="ph:list-bold" size="24" />
          </button>
          <slot name="header-title" />
        </div>
        <div class="header-right">
          <slot name="header-actions" />
        </div>
      </header>
      
      <div class="admin-content">
        <slot />
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

.admin-sidebar {
  width: 260px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: var(--z-modal);
}

.desktop-only {
  display: flex;
}

@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }
}

.mobile-drawer {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  box-shadow: var(--shadow-modal);
}

.mobile-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-overlay);
  backdrop-filter: blur(4px);
  z-index: calc(var(--z-modal) - 1);
}

.logo {
  padding: 24px;
  font-family: var(--font-mono);
  font-weight: 800;
  font-size: var(--text-xl);
  letter-spacing: -1px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-text { color: var(--color-text); }
.dot { color: var(--color-accent); }

.close-btn, .menu-btn {
  background: none;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-fast);
}

.close-btn:hover, .menu-btn:hover {
  color: var(--color-accent);
}

.admin-nav {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--color-text-2);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav-item:hover {
  background: var(--color-surface-2);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.admin-footer {
  padding: 16px;
  border-top: 1px solid var(--color-border);
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* Important for overflow containment */
}

.admin-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: var(--z-raised);
}

@media (min-width: 769px) {
  .admin-header {
    padding: 0 24px;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-content {
  padding: 16px;
  flex: 1;
}

@media (min-width: 769px) {
  .admin-content {
    padding: 24px;
  }
}

.mobile-only {
  display: none;
}

@media (max-width: 768px) {
  .mobile-only {
    display: flex;
  }
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity var(--transition-normal);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform var(--transition-normal);
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(-100%);
}
</style>
