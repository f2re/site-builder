export const useSchemaOrg = (schema: any) => {
  useHead({
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(schema)
      }
    ]
  })
}

export const useBreadcrumbSchema = (items: { name: string, item: string }[]) => {
  // Try to get site URL from runtime config, otherwise fallback
  const siteUrl = 'https://wifiobd.ru'
  
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.item.startsWith('http') ? item.item : `${siteUrl}${item.item}`
    }))
  }
  
  useSchemaOrg(schema)
}

export const useProductSchema = (product: any) => {
  const siteUrl = 'https://wifiobd.ru'
  
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    image: product.images,
    description: product.description,
    sku: product.id,
    offers: {
      '@type': 'Offer',
      url: `${siteUrl}/products/${product.slug}`,
      priceCurrency: product.currency || 'RUB',
      price: product.price_rub || product.price_display,
      availability: product.stock > 0 ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock'
    }
  }
  
  useSchemaOrg(schema)
}

export const useArticleSchema = (post: any) => {
  const siteUrl = 'https://wifiobd.ru'
  
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.title,
    image: [post.cover_url],
    datePublished: post.published_at,
    author: [{
      '@type': 'Person',
      name: post.author?.name || 'Admin',
      url: `${siteUrl}/blog`
    }]
  }
  
  useSchemaOrg(schema)
}
