<script setup lang="ts">
import { computed } from 'vue'

interface DailyStat {
  date: string
  revenue: number
  orders: number
}

const props = defineProps<{
  stats: DailyStat[]
  pending?: boolean
}>()

const width = 800
const height = 300
const padding = 40

const maxRevenue = computed(() => {
  if (!props.stats?.length) return 100
  return Math.max(...props.stats.map(s => s.revenue), 100) * 1.2
})

const points = computed(() => {
  if (!props.stats?.length) return ''
  
  const step = (width - padding * 2) / (props.stats.length - 1)
  
  return props.stats.map((s, i) => {
    const x = padding + i * step
    const y = height - padding - (s.revenue / maxRevenue.value) * (height - padding * 2)
    return `${x},${y}`
  }).join(' ')
})

const areaPoints = computed(() => {
  if (!props.stats?.length || !points.value) return ''
  const firstX = padding
  const lastX = width - padding
  const baseline = height - padding
  return `${firstX},${baseline} ${points.value} ${lastX},${baseline}`
})

const yTicks = computed(() => {
  const ticks = []
  for (let i = 0; i <= 4; i++) {
    const val = (maxRevenue.value / 4) * i
    ticks.push({
      label: `${Math.round(val).toLocaleString()}`,
      y: height - padding - (val / maxRevenue.value) * (height - padding * 2)
    })
  }
  return ticks
})

const xTicks = computed(() => {
  if (!props.stats?.length) return []
  const count = 5
  const step = Math.floor(props.stats.length / (count - 1))
  const ticks = []
  
  for (let i = 0; i < count; i++) {
    const index = Math.min(i * step, props.stats.length - 1)
    const s = props.stats[index]
    const xStep = (width - padding * 2) / (props.stats.length - 1)
    ticks.push({
      label: new Date(s.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
      x: padding + index * xStep
    })
  }
  return ticks
})
</script>

<template>
  <div class="sales-chart" data-testid="sales-chart">
    <div v-if="pending" class="chart-loading">
      <div class="skeleton-chart" />
    </div>
    
    <div v-else-if="!stats?.length" class="chart-empty">
      <Icon name="ph:chart-line-bold" size="48" class="empty-icon" />
      <p>Нет данных для отображения графика</p>
    </div>

    <div v-else class="chart-container">
      <svg :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="xMidYMid meet" class="svg-chart">
        <!-- Grid lines -->
        <g class="grid-lines">
          <line 
            v-for="tick in yTicks" 
            :key="tick.y" 
            :x1="padding" 
            :y1="tick.y" 
            :x2="width - padding" 
            :y2="tick.y" 
            stroke="var(--color-border)" 
            stroke-dasharray="4,4" 
          />
        </g>

        <!-- Area fill -->
        <polyline
          :points="areaPoints"
          fill="var(--color-accent-10)"
          stroke="none"
        />

        <!-- Line path -->
        <polyline
          :points="points"
          fill="none"
          stroke="var(--color-accent)"
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Data points -->
        <circle
          v-for="(s, i) in stats"
          :key="i"
          :cx="padding + i * ((width - padding * 2) / (stats.length - 1))"
          :cy="height - padding - (s.revenue / maxRevenue) * (height - padding * 2)"
          r="4"
          fill="var(--color-bg)"
          stroke="var(--color-accent)"
          stroke-width="2"
          class="chart-dot"
        >
          <title>{{ new Date(s.date).toLocaleDateString() }}: {{ s.revenue.toLocaleString() }} ₽</title>
        </circle>

        <!-- Y Axis labels -->
        <g class="axis-labels">
          <text 
            v-for="tick in yTicks" 
            :key="tick.y" 
            :x="padding - 10" 
            :y="tick.y" 
            text-anchor="end" 
            alignment-baseline="middle"
            class="axis-text"
          >
            {{ tick.label }}
          </text>
        </g>

        <!-- X Axis labels -->
        <g class="axis-labels">
          <text 
            v-for="tick in xTicks" 
            :key="tick.x" 
            :x="tick.x" 
            :y="height - padding + 20" 
            text-anchor="middle"
            class="axis-text"
          >
            {{ tick.label }}
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.sales-chart {
  width: 100%;
  height: 100%;
  min-height: 250px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.svg-chart {
  width: 100%;
  height: auto;
  overflow: visible;
}

.axis-text {
  font-size: 12px;
  fill: var(--color-text-2);
  font-family: inherit;
}

.chart-dot:hover {
  r: 6;
  fill: var(--color-accent);
  cursor: pointer;
}

.chart-loading, .chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 250px;
  gap: 16px;
}

.skeleton-chart {
  width: 100%;
  height: 200px;
  background: linear-gradient(90deg, var(--color-bg-2) 25%, var(--color-bg-3) 50%, var(--color-bg-2) 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: var(--radius-md);
}

.empty-icon {
  color: var(--color-text-3);
  opacity: 0.5;
}

.chart-empty p {
  color: var(--color-text-2);
  font-size: var(--text-sm);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
