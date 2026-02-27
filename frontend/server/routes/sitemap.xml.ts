export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const siteUrl = config.public.siteUrl

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
  </url>`).join('')}
  ${categoriesData.items.map((cat: any) => `
  <url>
    <loc>${siteUrl}/products?category_slug=${cat.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`).join('')}
  ${productsData.items.map((prod: any) => `
  <url>
    <loc>${siteUrl}/products/${prod.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>`).join('')}
  ${blogData.items.map((post: any) => `
  <url>
    <loc>${siteUrl}/blog/${post.slug}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>`).join('')}
</urlset>`

  setHeader(event, 'Content-Type', 'application/xml')
  return sitemap
})
