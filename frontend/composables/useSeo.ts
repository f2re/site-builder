/**
 * SEO composable for dynamic meta tag management.
 * Provides helpers for common SEO patterns: pages, articles, products.
 */

interface SeoOptions {
  title: string
  description: string
  image?: string
  url?: string
  type?: 'website' | 'article' | 'product'
  article?: {
    publishedTime?: string
    modifiedTime?: string
    author?: string
    tags?: string[]
  }
  product?: {
    price?: number
    currency?: string
    availability?: 'in stock' | 'out of stock'
  }
}

export const useSeo = (options: SeoOptions) => {
  const config = useRuntimeConfig()
  const route = useRoute()
  const siteUrl = config.public.siteUrl
  const currentUrl = options.url || `${siteUrl}${route.path}`

  // Base meta tags
  const meta: any[] = [
    { name: 'description', content: options.description },
    { property: 'og:title', content: options.title },
    { property: 'og:description', content: options.description },
    { property: 'og:url', content: currentUrl },
    { property: 'og:type', content: options.type || 'website' },
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: options.title },
    { name: 'twitter:description', content: options.description },
  ]

  // Image
  if (options.image) {
    const imageUrl = options.image.startsWith('http') 
      ? options.image 
      : `${siteUrl}${options.image}`
    meta.push(
      { property: 'og:image', content: imageUrl },
      { name: 'twitter:image', content: imageUrl }
    )
  }

  // Article-specific
  if (options.type === 'article' && options.article) {
    if (options.article.publishedTime) {
      meta.push({ property: 'article:published_time', content: options.article.publishedTime })
    }
    if (options.article.modifiedTime) {
      meta.push({ property: 'article:modified_time', content: options.article.modifiedTime })
    }
    if (options.article.author) {
      meta.push({ property: 'article:author', content: options.article.author })
    }
    if (options.article.tags) {
      options.article.tags.forEach(tag => {
        meta.push({ property: 'article:tag', content: tag })
      })
    }
  }

  // Product-specific
  if (options.type === 'product' && options.product) {
    if (options.product.price && options.product.currency) {
      meta.push(
        { property: 'product:price:amount', content: options.product.price.toString() },
        { property: 'product:price:currency', content: options.product.currency }
      )
    }
    if (options.product.availability) {
      meta.push({ property: 'product:availability', content: options.product.availability })
    }
  }

  // Set meta tags
  useHead({
    title: options.title,
    meta,
    link: [
      { rel: 'canonical', href: currentUrl }
    ]
  })
}

/**
 * SEO for blog articles with automatic Schema.org
 */
export const useArticleSeo = (article: {
  title: string
  description: string
  image?: string
  publishedAt: string
  updatedAt?: string
  author: string
  slug: string
  tags?: string[]
}) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl
  const url = `${siteUrl}/blog/${article.slug}`

  // Set SEO meta
  useSeo({
    title: `${article.title} — WifiOBD`,
    description: article.description,
    image: article.image,
    url,
    type: 'article',
    article: {
      publishedTime: article.publishedAt,
      modifiedTime: article.updatedAt,
      author: article.author,
      tags: article.tags,
    },
  })

  // Add Schema.org
  useArticleSchema({
    title: article.title,
    cover_url: article.image,
    published_at: article.publishedAt,
    author: { name: article.author },
  })
}

/**
 * SEO for product pages with automatic Schema.org
 */
export const useProductSeo = (product: {
  name: string
  description: string
  images: string[]
  price_rub: number
  stock: number
  slug: string
  id: number
}) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl
  const url = `${siteUrl}/products/${product.slug}`

  useSeo({
    title: `${product.name} — WifiOBD Shop`,
    description: product.description,
    image: product.images[0],
    url,
    type: 'product',
    product: {
      price: product.price_rub,
      currency: 'RUB',
      availability: product.stock > 0 ? 'in stock' : 'out of stock',
    },
  })

  // Add Schema.org
  useProductSchema(product)
}
