<template>
  <div class="layout">
    <AppHeader />
    <main class="main">
      <div class="container">
        <slot />
      </div>
    </main>
    <AppFooter />
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
  position: relative;
  z-index: 1;
}
</style>
