export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const siteUrl = 'https://wifiobd.ru'
  
  try {
    const postsResponse = await $fetch<any>(`${apiBase}/blog/posts?per_page=20`)
    const posts = postsResponse.items || []
    
    const rss = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>WifiOBD Blog</title>
  <link>${siteUrl}/blog</link>
  <description>Свежие новости и обзоры OBD2 сканеров</description>
  <language>ru</language>
  <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
  <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml" />
  ${posts.map((post: any) => `
  <item>
    <title>${post.title}</title>
    <link>${siteUrl}/blog/${post.slug}</link>
    <description>${post.excerpt || ''}</description>
    <pubDate>${new Date(post.published_at).toUTCString()}</pubDate>
    <guid>${siteUrl}/blog/${post.slug}</guid>
  </item>`).join('')}
</channel>
</rss>`

    event.node.res.setHeader('Content-Type', 'application/xml')
    return rss
  } catch (err) {
    console.error('RSS generation error:', err)
    return 'Error generating RSS'
  }
})
