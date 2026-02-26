export interface Author {
  id: string
  name: string
  avatar_url?: string
}

export interface BlogPost {
  id: string
  slug: string
  title: string
  excerpt: string
  cover_url: string
  author: Author
  tags: string[]
  published_at: string
  reading_time_min: number
  content_html?: string
  related?: BlogPost[]
}

export interface BlogListResponse {
  items: BlogPost[]
  next_cursor: string | null
  total: number
}

export const useBlog = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getPosts = (params?: {
    tag?: string
    author_id?: string
    page_cursor?: string
    per_page?: number
  }) => {
    return useFetch<BlogListResponse>(`${apiBase}/blog/posts`, {
      params,
      key: `blog-posts-${JSON.stringify(params)}`
    })
  }

  const getPost = (slug: string) => {
    return useFetch<BlogPost>(`${apiBase}/blog/posts/${slug}`, {
      key: `blog-post-${slug}`
    })
  }

  return {
    getPosts,
    getPost
  }
}
