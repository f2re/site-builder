import { ref, onMounted, onUnmounted, type Ref } from 'vue'

/**
 * useIntersection - Composable for lazy loading or infinite scroll
 * @param target Ref of the target element to observe
 * @param callback Function to execute when target is visible
 * @param options IntersectionObserverInit options
 */
export function useIntersection(
  target: Ref<HTMLElement | null>,
  callback: (entry: IntersectionObserverEntry) => void,
  options: IntersectionObserverInit = {
    root: null,
    rootMargin: '100px',
    threshold: 0
  }
) {
  const observer = ref<IntersectionObserver | null>(null)
  const isIntersecting = ref(false)

  onMounted(() => {
    if (!target.value) return

    observer.value = new IntersectionObserver(([entry]) => {
      isIntersecting.value = entry.isIntersecting
      if (entry.isIntersecting) {
        callback(entry)
      }
    }, options)

    observer.value.observe(target.value)
  })

  onUnmounted(() => {
    if (observer.value) {
      observer.value.disconnect()
    }
  })

  return { 
    observer,
    isIntersecting
  }
}
