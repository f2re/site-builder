<script setup lang="ts">
interface Props {
  width?: string
  height?: string
  radius?: string
  circle?: boolean
}

withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '20px',
  radius: 'var(--radius-md)',
  circle: false
})
</script>

<template>
  <div
    class="skeleton"
    :style="{
      width: width,
      height: height,
      borderRadius: circle ? '50%' : radius
    }"
  ></div>
</template>

<style scoped>
/* See tokens.css for .skeleton styles */
</style>
