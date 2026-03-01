<script setup lang="ts">
const navItems = [
  { label: 'Дашборд', icon: 'ph:chart-line-bold', to: '/admin' },
  { label: 'Пользователи', icon: 'ph:users-bold', to: '/admin/users' },
  { label: 'Товары', icon: 'ph:package-bold', to: '/admin/products' },
  { label: 'Заказы', icon: 'ph:shopping-cart-bold', to: '/admin/orders' },
  { label: 'Блог', icon: 'ph:article-bold', to: '/admin/blog' },
  { label: 'Страницы', icon: 'ph:files-bold', to: '/admin/pages' },
  { label: 'Назад на сайт', icon: 'ph:arrow-left-bold', to: '/' },
]
</script>

<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
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
    
    <main class="admin-main">
      <header class="admin-header">
        <div class="header-left">
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
}

@media (max-width: 768px) {
  .admin-sidebar {
    display: none;
  }
}

.logo {
  padding: 24px;
  font-family: var(--font-mono);
  font-weight: 800;
  font-size: var(--text-xl);
  letter-spacing: -1px;
}

.logo-text { color: var(--color-text); }
.dot { color: var(--color-accent); }

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
}

.admin-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: var(--z-raised);
}

.admin-content {
  padding: 24px;
  flex: 1;
}
</style>
