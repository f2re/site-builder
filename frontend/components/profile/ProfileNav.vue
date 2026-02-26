<script setup lang="ts">
const route = useRoute()

const navItems = [
  { label: 'Профиль', to: '/profile', icon: 'ph:user-bold' },
  { label: 'Мои заказы', to: '/profile/orders', icon: 'ph:shopping-bag-bold' },
  { label: 'Мои устройства', to: '/profile/devices', icon: 'ph:cpu-bold' },
]
</script>

<template>
  <nav class="profile-nav">
    <NuxtLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      class="nav-item"
      :class="{ active: route.path === item.to }"
    >
      <Icon :name="item.icon" size="20" />
      <span>{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<style scoped>
.profile-nav {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
  overflow-x: auto;
  scrollbar-width: none;
}

.profile-nav::-webkit-scrollbar {
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

@media (max-width: 768px) {
  .profile-nav {
    border-radius: 0;
    border-inline: none;
    margin-inline: calc(var(--padding-inline) * -1);
    padding-inline: var(--padding-inline);
  }
}
</style>
