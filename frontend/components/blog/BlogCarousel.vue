<script setup lang="ts">
const props = withDefaults(defineProps<{
  images: string[]
  alt?: string
  autoplay?: boolean
  interval?: number
  aspectRatio?: string
}>(), {
  alt: '',
  autoplay: true,
  interval: 3500,
  aspectRatio: '16/9',
})

const activeIndex = ref(0)
const isHovered = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const hasMultiple = computed(() => props.images.length > 1)

function next() {
  if (props.images.length === 0) return
  activeIndex.value = (activeIndex.value + 1) % props.images.length
}

function prev() {
  if (props.images.length === 0) return
  activeIndex.value = (activeIndex.value - 1 + props.images.length) % props.images.length
}

function goTo(i: number) {
  activeIndex.value = i
}

function startTimer() {
  if (!props.autoplay || !hasMultiple.value) return
  timer = setInterval(() => {
    if (!isHovered.value) next()
  }, props.interval)
}

function stopTimer() {
  if (timer !== null) {
    clearInterval(timer)
    timer = null
  }
}

function onMouseEnter() {
  isHovered.value = true
}

function onMouseLeave() {
  isHovered.value = false
}

onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  stopTimer()
})

watch(() => props.images.length, () => {
  stopTimer()
  activeIndex.value = 0
  startTimer()
})
</script>

<template>
  <div
    v-if="images.length > 0"
    class="blog-carousel"
    :style="{ aspectRatio }"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <div class="blog-carousel__slides">
      <transition-group name="carousel-fade" tag="div" class="blog-carousel__track">
        <div
          v-for="(src, i) in images"
          v-show="i === activeIndex"
          :key="src"
          class="blog-carousel__slide"
        >
          <NuxtImg
            :src="src"
            :alt="alt"
            :loading="i === 0 ? 'eager' : 'lazy'"
            class="blog-carousel__img"
            width="800"
            height="450"
            fit="cover"
          />
        </div>
      </transition-group>
    </div>

    <!-- Arrows — always visible on mobile if multiple, hover-only on desktop -->
    <template v-if="hasMultiple">
      <button
        type="button"
        class="blog-carousel__arrow blog-carousel__arrow--prev"
        aria-label="Предыдущий слайд"
        @click.prevent="prev"
      >
        <Icon name="ph:caret-left-bold" size="20" />
      </button>
      <button
        type="button"
        class="blog-carousel__arrow blog-carousel__arrow--next"
        aria-label="Следующий слайд"
        @click.prevent="next"
      >
        <Icon name="ph:caret-right-bold" size="20" />
      </button>

      <!-- Dots -->
      <div class="blog-carousel__dots">
        <button
          v-for="(_, i) in images"
          :key="i"
          type="button"
          class="blog-carousel__dot"
          :class="{ 'blog-carousel__dot--active': i === activeIndex }"
          :aria-label="`Слайд ${i + 1}`"
          @click.prevent="goTo(i)"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.blog-carousel {
  position: relative;
  width: 100%;
  overflow: hidden;
  background: var(--color-surface-2);
  border-radius: inherit;
}

.blog-carousel__slides {
  position: relative;
  width: 100%;
  height: 100%;
}

.blog-carousel__track {
  position: relative;
  width: 100%;
  height: 100%;
}

.blog-carousel__slide {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.blog-carousel__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Arrows */
.blog-carousel__arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--color-overlay);
  color: var(--color-text);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast), opacity var(--transition-fast);
  opacity: 1;
}

.blog-carousel__arrow--prev { left: 8px; }
.blog-carousel__arrow--next { right: 8px; }

.blog-carousel__arrow:hover {
  background: var(--color-accent);
}

/* Desktop: arrows visible only on hover */
@media (min-width: 768px) {
  .blog-carousel__arrow {
    opacity: 0;
  }
  .blog-carousel:hover .blog-carousel__arrow {
    opacity: 1;
  }
}

/* Dots */
.blog-carousel__dots {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  z-index: 10;
}

.blog-carousel__dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  border: none;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: background var(--transition-fast), transform var(--transition-fast);
  padding: 0;
}

.blog-carousel__dot--active {
  background: var(--color-accent);
  transform: scale(1.3);
}

/* Fade transition */
.carousel-fade-enter-active,
.carousel-fade-leave-active {
  transition: opacity 300ms ease;
  position: absolute;
  inset: 0;
}

.carousel-fade-enter-from,
.carousel-fade-leave-to {
  opacity: 0;
}

.carousel-fade-enter-to,
.carousel-fade-leave-from {
  opacity: 1;
}
</style>
