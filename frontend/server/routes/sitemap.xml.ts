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
      { path: '', priority: '1.0', changefreq: 'daily' },
      { path: '/blog', priority: '0.8', changefreq: 'daily' },
      { path: '/products', priority: '0.8', changefreq: 'daily' },
      { path: '/cart', priority: '0.5', changefreq: 'monthly' },
    ]

    const now = new Date().toISOString()

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${staticRoutes.map(route => `
  <url>
    <loc>${siteUrl}${route.path}</loc>
    <lastmod>${now}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
  </url>`).join('').trim()}
  ${categoriesData.items.map((cat: any) => `
  <url>
    <loc>${siteUrl}/products?category=${cat.slug}</loc>
    <lastmod>${cat.updated_at || cat.created_at || now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`).join('').trim()}
  ${productsData.items.map((prod: any) => `
  <url>
    <loc>${siteUrl}/products/${prod.slug}</loc>
    <lastmod>${prod.updated_at || prod.created_at || now}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>`).join('').trim()}
  ${blogData.items.map((post: any) => `
  <url>
    <loc>${siteUrl}/blog/${post.slug}</loc>
    <lastmod>${post.updated_at || post.published_at || post.created_at || now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>`).join('').trim()}
</urlset>`

    setHeader(event, 'Content-Type', 'application/xml')
    return sitemap
  } catch (error) {
    console.error('Sitemap generation error:', error)
    return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>${siteUrl}</loc><lastmod>${new Date().toISOString()}</lastmod></url></urlset>`
  }
})
