<script setup lang="ts">
import { useAuthStore } from '~/stores/authStore'

const route = useRoute()
const authStore = useAuthStore()

const navItems = [
  { label: 'Профиль', to: '/profile', icon: 'ph:user-bold' },
  { label: 'Мои заказы', to: '/profile/orders', icon: 'ph:shopping-bag-bold' },
  { label: 'Мои устройства', to: '/profile/devices', icon: 'ph:cpu-bold' },
]

const handleLogout = () => {
  authStore.logout()
  navigateTo('/')
}

const isLinkActive = (path: string) => {
  if (path === '/profile/orders') {
    return route.path.startsWith(path)
  }
  return route.path === path
}
</script>

<template>
  <nav class="profile-nav">
    <div class="nav-links">
      <NuxtLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isLinkActive(item.to) }"
      >
        <Icon :name="item.icon" size="20" />
        <span>{{ item.label }}</span>
      </NuxtLink>
    </div>
    
    <button @click="handleLogout" class="nav-item logout-btn">
      <Icon name="ph:sign-out-bold" size="20" />
      <span>Выйти</span>
    </button>
  </nav>
</template>

<style scoped>
.profile-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 4px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
}

.nav-links {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-links::-webkit-scrollbar {
  display: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  color: var(--color-text-2);
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  transition: all var(--transition-fast);
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: var(--text-sm);
}

.nav-item:hover {
  background: var(--color-surface-3);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-accent);
  color: var(--color-on-accent);
  box-shadow: var(--shadow-glow-accent);
}

.logout-btn:hover {
  color: var(--color-error);
  background: var(--color-error-bg);
}

@media (max-width: 768px) {
  .profile-nav {
    border-radius: 0;
    border-inline: none;
    margin-inline: calc(var(--padding-inline) * -1);
    padding-inline: var(--padding-inline);
    flex-direction: column;
    align-items: stretch;
  }
  
  .nav-links {
    flex-direction: column;
  }
  
  .logout-btn {
    border-top: 1px solid var(--color-border);
    margin-top: 4px;
    padding-top: 14px;
    border-radius: 0;
  }
}
</style>
