export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl

  const robots = [
    'User-agent: *',
    'Allow: /',
    'Disallow: /admin/',
    'Disallow: /auth/',
    'Disallow: /checkout/',
    'Disallow: /profile/',
    'Disallow: /api/',
    'Disallow: /cart',
    '',
    `Sitemap: ${siteUrl}/sitemap.xml`
  ].join('\n')

  setHeader(event, 'Content-Type', 'text/plain')
  return robots
})
