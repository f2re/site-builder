<script setup lang="ts">
import { useProducts } from '~/composables/useProducts'
import ProductCard from '~/components/catalog/ProductCard.vue'
import CategorySidebar from '~/components/catalog/CategorySidebar.vue'
import AppBreadcrumbs from '~/components/AppBreadcrumbs.vue'
import { ref, computed, watch } from 'vue'

const { getProducts, getCategories } = useProducts()
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

// Filters state from query
const categorySlug = computed(() => route.query.category as string | undefined)

// Pagination state
const products = ref<any[]>([])
const nextCursor = ref<string | null>(null)
const total = ref(0)
const loading = ref(false)

// Fetch categories (SSR-friendly)
const { data: categoriesData } = await getCategories()

// Main fetch function
async function fetchProducts(cursor?: string) {
  loading.value = true
  try {
    const { data } = await getProducts({
      category_slug: categorySlug.value,
      page_cursor: cursor,
      per_page: 20
    })
    
    if (data.value) {
      if (cursor) {
        products.value.push(...data.value.items)
      } else {
        products.value = data.value.items
      }
      nextCursor.value = data.value.next_cursor
      total.value = data.value.total
    }
  } catch (err) {
    console.error('Error fetching products:', err)
  } finally {
    loading.value = false
  }
}

// Initial fetch on server/client
await fetchProducts()

// Watch for category change
watch(categorySlug, async () => {
  products.value = []
  nextCursor.value = null
  await fetchProducts()
})

const loadMore = () => {
  if (nextCursor.value && !loading.value) {
    fetchProducts(nextCursor.value)
  }
}

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
  ogType: 'website'
})

useHead({
  link: [
    { 
      rel: 'canonical', 
      href: () => {
        const url = new URL(`${config.public.siteBase}/products`, config.public.siteUrl)
        if (categorySlug.value) {
          url.searchParams.set('category', categorySlug.value)
        }
        return url.toString()
      }
    }
  ]
})

const breadcrumbItems = computed(() => {
  const items = [{ name: 'Каталог', path: '/products' }]
  if (categorySlug.value && categoriesData.value) {
    const cat = categoriesData.value.items.find(c => c.slug === categorySlug.value)
    if (cat) {
      items.push({ name: cat.name, path: `/products?category=${cat.slug}` })
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

            <div class="catalog-page__stats">
              {{ total }} товаров найдено
            </div>
          </header>

          <!-- Products List -->
          <div v-if="products.length" class="product-grid">
            <ProductCard
              v-for="product in products"
              :key="product.id"
              :product="product"
            />
          </div>

          <!-- Skeleton Loaders -->
          <div v-if="loading" class="product-grid mt-6">
            <div v-for="i in 4" :key="i" class="product-card-skeleton skeleton"></div>
          </div>

          <!-- Empty State -->
          <div v-if="!loading && products.length === 0" class="catalog-page__empty">
            <div class="catalog-page__empty-icon">🔍</div>
            <h2 class="catalog-page__empty-title">Товары не найдены</h2>
            <p class="catalog-page__empty-text">Попробуйте изменить параметры поиска или фильтры.</p>
            <button class="btn btn--primary" @click="handleCategorySelect(undefined)">
              Сбросить фильтры
            </button>
          </div>

          <!-- Pagination -->
          <div v-if="nextCursor" class="catalog-page__pagination">
            <button 
              class="btn btn--secondary btn--lg" 
              :disabled="loading"
              @click="loadMore"
            >
              <span v-if="loading">Загрузка...</span>
              <span v-else>Показать еще</span>
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

.catalog-page__pagination {
  margin-top: 48px;
  display: flex;
  justify-content: center;
}

.mt-6 { margin-top: 24px; }

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

.btn--lg {
  padding: 16px 32px;
  font-size: var(--text-base);
}

.btn--secondary {
  background: transparent;
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
