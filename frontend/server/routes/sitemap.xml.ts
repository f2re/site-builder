export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  let apiBase = config.public.apiBase
  const siteUrl = config.public.siteUrl

  // Ensure apiBase includes /api/v1 if not present
  if (!apiBase.includes('/api/v1')) {
    apiBase = apiBase.endsWith('/') ? `${apiBase}api/v1` : `${apiBase}/api/v1`
  }

  try {
    const [productsData, blogData, categoriesData] = await Promise.all([
      $fetch<any>(`${apiBase}/products?per_page=1000`),
      $fetch<any>(`${apiBase}/blog/posts?per_page=1000`),
      $fetch<any>(`${apiBase}/products/categories`)
    ])

    const staticRoutes = [
      '',
      '/blog',
      '/products',
      '/cart',
    ]

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${staticRoutes.map(route => `
  <url>
    <loc>${siteUrl}${route}</loc>
    <changefreq>daily</changefreq>
    <priority>${route === '' ? '1.0' : '0.8'}</priority>
  </url>`).join('').trim()}
  ${categoriesData.items.map((cat: any) => `
  <url>
    <loc>${siteUrl}/products?category=${cat.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`).join('').trim()}
  ${productsData.items.map((prod: any) => `
  <url>
    <loc>${siteUrl}/products/${prod.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>`).join('').trim()}
  ${blogData.items.map((post: any) => `
  <url>
    <loc>${siteUrl}/blog/${post.slug}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>`).join('').trim()}
</urlset>`

    setHeader(event, 'Content-Type', 'application/xml')
    return sitemap
  } catch (error) {
    console.error('Sitemap generation error:', error)
    return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>${siteUrl}</loc></url></urlset>`
  }
})
