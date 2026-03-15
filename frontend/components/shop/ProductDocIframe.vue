<template>
  <div v-if="url" class="product-doc-iframe-container" ref="containerRef">
    <div v-if="isLoading && isIntersecting" class="iframe-loading">
      <div class="spinner"></div>
      <span>Loading documentation...</span>
    </div>
    
    <iframe
      v-if="isIntersecting"
      ref="iframeRef"
      :src="url"
      :style="{ height: iframeHeightCss, opacity: isLoading ? 0 : 1 }"
      frameborder="0"
      scrolling="no"
      width="100%"
      @load="onIframeLoad"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
    ></iframe>

    <div v-if="hasError" class="iframe-error">
      <p>Failed to load documentation inline.</p>
      <a :href="url" target="_blank" rel="noopener noreferrer" class="btn btn-outline">
        Open in new tab
      </a>
    </div>

    <!-- Fallback link for mobile or if iframe is too constrained -->
    <div class="iframe-fallback-link">
      <a :href="url" target="_blank" rel="noopener noreferrer">
        Open documentation in new tab
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  url: string | null
}>()

const containerRef = ref<HTMLElement | null>(null)
const iframeRef = ref<HTMLIFrameElement | null>(null)
const isIntersecting = ref(false)
const isLoading = ref(true)
const hasError = ref(false)
// Height as CSS string (e.g. '2033px') — supports both numeric and string values from postMessage
const iframeHeightCss = ref('600px')

let observer: IntersectionObserver | null = null

const onIframeLoad = () => {
  isLoading.value = false
}

const handleMessage = (event: MessageEvent) => {
  if (typeof event.data !== 'object' || event.data === null) {
    // iframeResizer string format: "[iFrameSizer]id:height:..."
    if (typeof event.data === 'string' && event.data.includes('[iFrameSizer]')) {
      const parts = event.data.split(':')
      if (parts.length > 2 && !isNaN(Number(parts[1]))) {
        iframeHeightCss.value = `${parts[1]}px`
      }
    }
    return
  }

  const data = event.data as Record<string, unknown>

  // Format used by mad-auto.ru and similar docs: { docIframeHeight: '2033px' } or { docIframeHeight: 2033 }
  if (data.docIframeHeight !== undefined) {
    const h = data.docIframeHeight
    iframeHeightCss.value = typeof h === 'number' ? `${h}px` : String(h)
    return
  }

  // Generic resize: { type: 'resize', height: 500 }
  if (data.type === 'resize' && typeof data.height === 'number') {
    iframeHeightCss.value = `${data.height}px`
    return
  }

  // iframeResizer object format: { iframe: ..., height: 500 }
  if (typeof data.height === 'number' && data.height > 0) {
    iframeHeightCss.value = `${data.height}px`
  }
}

onMounted(() => {
  if (!props.url) return

  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      isIntersecting.value = true
      if (observer && containerRef.value) {
        observer.unobserve(containerRef.value)
      }
    }
  }, { rootMargin: '200px' }) // Load slightly before it comes into view

  if (containerRef.value) {
    observer.observe(containerRef.value)
  }

  window.addEventListener('message', handleMessage)
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
  window.removeEventListener('message', handleMessage)
})
</script>

<style scoped>
.product-doc-iframe-container {
  position: relative;
  width: 100%;
  margin: 2rem 0;
  border-radius: var(--radius-md, 8px);
  /* No overflow:hidden — iframe must grow to full height seamlessly */
  background: var(--color-surface, #f9f9f9);
}

.iframe-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface, #f9f9f9);
  z-index: 1;
}

.spinner {
  border: 3px solid rgba(0,0,0,0.1);
  border-top-color: var(--primary-color, #e00000);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

iframe {
  display: block;
  transition: opacity 0.3s ease;
  /* No min-height — height is driven entirely by postMessage from the document */
  overflow: hidden;
}

.iframe-error {
  text-align: center;
  padding: 2rem;
}

.iframe-fallback-link {
  display: none;
  text-align: center;
  padding: 1rem;
  background: var(--bg-surface-alt, #eee);
}

/* Mobile-first Race-style UI adjustments */
@media (max-width: 768px) {
  .product-doc-iframe-container {
    border-radius: 0;
    margin: 1rem -1rem; /* Full bleed on mobile */
    width: calc(100% + 2rem);
  }
  
  .iframe-fallback-link {
    display: block; /* Always show fallback on mobile as scrolling iframes is painful */
  }
}
</style>
