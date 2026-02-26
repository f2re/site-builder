<template>
  <div class="layout">
    <AppHeader />
    <main class="main">
      <div class="container">
        <slot />
      </div>
    </main>
    <footer class="footer">
      <div class="container">
        <div class="footer-inner">
          <p class="copyright">&copy; 2026 WifiOBD Shop. Все права защищены.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main {
  flex-grow: 1;
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

.footer {
  border-top: 1px solid var(--color-border);
  background-color: var(--color-surface);
  padding: 40px 0;
  margin-top: 80px;
}

.footer-inner {
  text-align: center;
}

.copyright {
  color: var(--color-text-2);
  font-size: var(--text-sm);
  margin: 0;
}
</style>
