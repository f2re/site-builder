export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const siteUrl = config.public.siteUrl

  const robots = [
    'User-agent: *',
    'Allow: /',
    'Disallow: /admin/',
    'Disallow: /checkout/',
    'Disallow: /profile/',
    'Disallow: /api/',
    '',
    `Sitemap: ${siteUrl}/sitemap.xml`
  ].join('\n')

  setHeader(event, 'Content-Type', 'text/plain')
  return robots
})
