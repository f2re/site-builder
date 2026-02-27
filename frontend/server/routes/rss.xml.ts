export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const siteUrl = config.public.siteUrl

  const blogData = await $fetch<any>(`${apiBase}/blog/posts?per_page=20`)

  const rss = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>WifiOBD Blog</title>
    <link>${siteUrl}/blog</link>
    <description>Последние новости и статьи о диагностике авто</description>
    <language>ru-RU</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml" />
    ${blogData.items.map((post: any) => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/blog/${post.slug}</link>
      <description><![CDATA[${post.excerpt}]]></description>
      <pubDate>${new Date(post.published_at).toUTCString()}</pubDate>
      <guid isPermaLink="true">${siteUrl}/blog/${post.slug}</guid>
    </item>`).join('')}
  </channel>
</rss>`

  setHeader(event, 'Content-Type', 'application/xml')
  return rss
})
