export default defineEventHandler((event) => {
  const siteUrl = 'https://wifiobd.ru'
  
  const robots = `User-agent: *
Disallow: /admin
Disallow: /cart
Disallow: /checkout
Disallow: /profile
Disallow: /*?*

Sitemap: ${siteUrl}/sitemap.xml`

  event.node.res.setHeader('Content-Type', 'text/plain')
  return robots
})
