<script setup lang="ts">
import { useProducts } from '~/composables/useProducts'
import ProductCard from '~/components/catalog/ProductCard.vue'
import CategorySidebar from '~/components/catalog/CategorySidebar.vue'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'

const { getProducts, getCategories } = useProducts()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

// Filters state from query
const categorySlug = computed(() => route.query.category as string | undefined)

// Fetch data
const { data: categoriesData } = await getCategories()
const { data: productsData, pending, refresh } = await getProducts({
  category_slug: categorySlug.value,
  per_page: 20
})

// Watch for category change
watch(categorySlug, () => {
  refresh()
})

const handleCategorySelect = (slug: string | undefined) => {
  router.push({
    query: {
      ...route.query,
      category: slug
    }
  })
}

// SEO
useSeoMeta({
  title: 'Каталог товаров | WifiOBD',
  description: 'Широкий выбор оборудования для диагностики автомобилей в нашем каталоге. OBD2 сканеры, адаптеры и аксессуары.',
  ogTitle: 'Каталог товаров | WifiOBD',
  ogDescription: 'Широкий выбор оборудования для диагностики автомобилей.',
  ogType: 'website',
})

useHead({
  link: [
    { 
      rel: 'canonical', 
      href: () => {
        const url = new URL(`${config.public.siteUrl}/products`)
        if (categorySlug.value) {
          url.searchParams.set('category', categorySlug.value)
        }
        return url.toString()
      }
    }
  ]
})

const breadcrumbItems = computed(() => {
  const items = [{ label: 'Каталог', to: '/products' }]
  if (categorySlug.value && categoriesData.value) {
    const cat = categoriesData.value.items.find(c => c.slug === categorySlug.value)
    if (cat) {
      items.push({ label: cat.name, to: `/products?category=${cat.slug}` })
    }
  }
  return items
})
</script>

<template>
  <div class="catalog-page">
    <div class="container">
      <AppBreadcrumbs :items="breadcrumbItems" />
      
      <div class="catalog-page__layout">
        <!-- Sidebar (Desktop) -->
        <aside class="catalog-page__sidebar desktop-only">
          <CategorySidebar
            v-if="categoriesData"
            :categories="categoriesData.items"
            :active-slug="categorySlug"
            @select="handleCategorySelect"
          />
        </aside>

        <main class="catalog-page__main">
          <header class="catalog-page__header">
            <h1 class="catalog-page__title">
              {{ categorySlug ? categoriesData?.items.find(c => c.slug === categorySlug)?.name : 'Все товары' }}
            </h1>

            <div class="catalog-page__stats" v-if="productsData">
              {{ productsData.total }} товаров найдено
            </div>
          </header>

          <!-- Loading State -->
          <div v-if="pending" class="product-grid">
            <div v-for="i in 8" :key="i" class="product-card-skeleton skeleton"></div>
          </div>

          <!-- Products List -->
          <div v-else-if="productsData?.items.length" class="product-grid">
            <TransitionGroup name="list">
              <ProductCard
                v-for="product in productsData.items"
                :key="product.id"
                :product="product"
              />
            </TransitionGroup>
          </div>

          <!-- Empty State -->
          <div v-else class="catalog-page__empty">
            <div class="catalog-page__empty-icon">🔍</div>
            <h2 class="catalog-page__empty-title">Товары не найдены</h2>
            <p class="catalog-page__empty-text">Попробуйте изменить параметры поиска или фильтры.</p>
            <button class="btn btn--primary" @click="handleCategorySelect(undefined)">
              Сбросить фильтры
            </button>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-page {
  padding: 40px 0;
}

.catalog-page__layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

@media (min-width: 1024px) {
  .catalog-page__layout {
    grid-template-columns: 280px 1fr;
  }
}

.catalog-page__header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.catalog-page__title {
  font-size: var(--text-2xl);
  font-weight: 800;
  margin: 0;
  color: var(--color-text);
  border-left: 4px solid var(--color-accent);
  padding-left: 16px;
}

.catalog-page__stats {
  font-size: var(--text-sm);
  color: var(--color-muted);
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
}

.product-card-skeleton {
  aspect-ratio: 1 / 1.4;
  border-radius: var(--radius-lg);
}

.catalog-page__empty {
  text-align: center;
  padding: 80px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}

.catalog-page__empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.catalog-page__empty-title {
  font-size: var(--text-xl);
  font-weight: 700;
  margin-bottom: 8px;
}

.catalog-page__empty-text {
  color: var(--color-text-2);
  margin-bottom: 24px;
}

.desktop-only {
  display: none;
}

@media (min-width: 1024px) {
  .desktop-only {
    display: block;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  font-size: var(--text-sm);
}

.btn--primary {
  background: var(--color-accent);
  color: var(--color-on-accent);
}

.btn--primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-accent);
}

.btn--primary:active {
  transform: scale(0.98);
}
</style>
