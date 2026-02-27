---
id: FE-04
status: TODO
agent: frontend-agent
stage: 9 (SEO и Core Web Vitals)
priority: MEDIUM
depends_on: [FE-02, FE-03]
blocks: [QA-01]
---

# FE-04 — SEO и Core Web Vitals

> ⚠️ Отдельный этап. Не совмещать с разработкой фич. Требует внимательного тестирования.

## Цель

Цели: Lighthouse SEO = 100, Performance ≥ 90, LCP < 2.5s, CLS < 0.1.

## ⚠️ Перед началом

```bash
list_directory frontend/composables/
list_directory frontend/server/routes/
# Проверить наличие useSeo.ts, useSchemaOrg.ts, sitemap.xml.ts
```

## Задачи

### 1. Composable `useSeo.ts`

Если отсутствует — создать `frontend/composables/useSeo.ts`:

```typescript
export const usePageSeo = (opts: {
  title: string
  description: string
  image?: string
  type?: 'website' | 'article'
  publishedAt?: string
  modifiedAt?: string
  author?: string
}) => {
  const { public: { siteUrl } } = useRuntimeConfig()
  useSeoMeta({
    title: opts.title,
    description: opts.description,
    ogTitle: opts.title,
    ogDescription: opts.description,
    ogImage: opts.image ?? `${siteUrl}/og-default.png`,
    ogType: opts.type ?? 'website',
    ogLocale: 'ru_RU',
    ogSiteName: 'WifiOBD Shop',
    twitterCard: 'summary_large_image',
    ...(opts.publishedAt && { articlePublishedTime: opts.publishedAt }),
    ...(opts.modifiedAt && { articleModifiedTime: opts.modifiedAt }),
  })
  useHead({
    link: [{ rel: 'canonical', href: `${siteUrl}${useRoute().path}` }]
  })
}
```

### 2. Composable `useSchemaOrg.ts`

```typescript
export const useArticleSchema = (post: BlogPost) => { ... }    // BlogPosting
export const useProductSchema = (product: Product) => { ... }  // Product + Offer
export const useBreadcrumbSchema = (crumbs: Crumb[]) => { ... } // BreadcrumbList
```

Вставлять через `useHead({ script: [{ type: 'application/ld+json', ... }] })`.

### 3. Динамический sitemap.xml

`frontend/server/routes/sitemap.xml.ts`:
- Запрашивает из API все активные товары и опубликованные статьи
- `lastmod` из `updated_at`
- `Cache-Control: public, max-age=3600`
- Формат W3C: `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`

### 4. robots.txt

`frontend/server/routes/robots.txt.ts`:
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart
Disallow: /checkout
Disallow: /profile
Disallow: /api/
Disallow: /products?*
Allow: /products/$
Sitemap: https://wifiobd.shop/sitemap.xml
```

### 5. Canonical с фильтрами

В `/products` — canonical без `sort` и `page`, только с `category`:
```typescript
const canonicalPath = computed(() => {
  const params = new URLSearchParams()
  if (route.query.category) params.set('category', String(route.query.category))
  return params.toString() ? `/products?${params}` : '/products'
})
```

### 6. RSS feed

`frontend/server/routes/rss.xml.ts` — последние 20 статей блога.

### 7. error.vue

Проверить/создать `frontend/error.vue` с:
```typescript
useSeoMeta({ robots: 'noindex,nofollow' })
```

### 8. Изображения CWV

Аудит всех `<img>` во всех компонентах:
- Обязательные атрибуты: `src` (WebP), `alt`, `width`, `height`, `loading="lazy"`
- Hero: `loading="eager" fetchpriority="high"`
- `srcset` — 480w, 800w, 1200w (генерирует Celery на бэке)

## Критерии готовности

- [ ] `curl https://wifiobd.shop/sitemap.xml` → валидный XML с товарами и статьями
- [ ] `curl https://wifiobd.shop/robots.txt` → `Sitemap:` и `Disallow: /admin/`
- [ ] Google Rich Results Test — товар и статья проходят валидацию
- [ ] Lighthouse SEO = 100 на `/products/[slug]` и `/blog/[slug]`
- [ ] LCP < 2.5s, CLS < 0.1 в PageSpeed Insights
- [ ] `/404` страница имеет `robots: noindex`

## Отчёт

`.gemini/agents/reports/frontend/FE-04.md`
