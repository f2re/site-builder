/**
 * Schema.org composables for structured data (JSON-LD).
 * Provides helpers for common patterns: articles, products, breadcrumbs.
 */

export const useBreadcrumbSchema = (crumbs: { name: string; url: string }[]) => {
  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: crumbs.map((c, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          name: c.name,
          item: c.url,
        })),
      }),
    }],
  })
}

export const useArticleSchema = (post: {
  title: string
  excerpt?: string
  cover_url?: string
  published_at: string
  updated_at?: string
  author: { name: string }
}) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl
  const route = useRoute()

  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        headline: post.title,
        description: post.excerpt,
        image: post.cover_url,
        datePublished: post.published_at,
        dateModified: post.updated_at || post.published_at,
        author: {
          '@type': 'Person',
          name: post.author.name,
        },
        publisher: {
          '@type': 'Organization',
          name: 'WifiOBD Shop',
          logo: {
            '@type': 'ImageObject',
            url: `${siteUrl}/logo.png`,
          },
        },
        mainEntityOfPage: {
          '@type': 'WebPage',
          '@id': `${siteUrl}${route.path}`,
        },
      }),
    }],
  })
}

export const useProductSchema = (product: {
  name: string
  description?: string
  images: string[]
  price_rub: number
  stock: number
  sku?: string
}) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl
  const route = useRoute()

  useHead({
    script: [{
      type: 'application/ld+json',
      children: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Product',
        name: product.name,
        description: product.description,
        image: product.images,
        sku: product.sku,
        offers: {
          '@type': 'Offer',
          price: product.price_rub,
          priceCurrency: 'RUB',
          availability: product.stock > 0
            ? 'https://schema.org/InStock'
            : 'https://schema.org/OutOfStock',
          url: `${siteUrl}${route.path}`,
          seller: {
            '@type': 'Organization',
            name: 'WifiOBD Shop',
          },
        },
      }),
    }],
  })
}
