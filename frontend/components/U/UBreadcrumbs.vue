<script setup lang="ts">
// Pass-through к AppBreadcrumbs для обратной совместимости
defineProps<{ crumbs: Array<{ label: string; to?: string; icon?: string }> }>()
</script>

<template>
  <AppBreadcrumbs v-bind="$attrs" :crumbs="crumbs" />
</template>
