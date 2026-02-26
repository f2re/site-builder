export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const siteUrl = 'https://wifiobd.ru'
  
  try {
    const [productsResponse, postsResponse] = await Promise.all([
      $fetch<any>(`${apiBase}/products`),
      $fetch<any>(`${apiBase}/blog/posts`)
    ])
    
    const products = productsResponse.items || []
    const posts = postsResponse.items || []
    
    const staticRoutes = [
      '/',
      '/products',
      '/blog',
      '/about',
      '/contact'
    ]
    
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${staticRoutes.map(route => `
  <url>
    <loc>${siteUrl}${route}</loc>
    <changefreq>daily</changefreq>
    <priority>${route === '/' ? '1.0' : '0.8'}</priority>
  </url>`).join('')}
${products.map((p: any) => `
  <url>
    <loc>${siteUrl}/products/${p.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`).join('')}
${posts.map((post: any) => `
  <url>
    <loc>${siteUrl}/blog/${post.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>`).join('')}
</urlset>`

    event.node.res.setHeader('Content-Type', 'application/xml')
    return sitemap
  } catch (err) {
    console.error('Sitemap generation error:', err)
    return 'Error generating sitemap'
  }
})
