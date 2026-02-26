<template>
  <header class="header">
    <div class="container">
      <div class="header-inner">
        <div class="logo">
          <NuxtLink to="/">
            <span class="logo-text">WifiOBD<span class="logo-accent">.shop</span></span>
          </NuxtLink>
        </div>
        
        <nav class="nav">
          <NuxtLink to="/products" class="nav-link">Каталог</NuxtLink>
          <NuxtLink to="/blog" class="nav-link">Блог</NuxtLink>
        </nav>
        
        <div class="actions">
          <UThemeToggle />
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  height: 64px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: var(--z-overlay);
  backdrop-filter: blur(8px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-text {
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--color-text);
  letter-spacing: -0.5px;
}

.logo-accent {
  color: var(--color-accent);
}

.nav {
  display: flex;
  gap: 24px;
}

.nav-link {
  color: var(--color-text-2);
  font-weight: 500;
  transition: color var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-accent);
}

.nav-link.router-link-active {
  color: var(--color-text);
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
