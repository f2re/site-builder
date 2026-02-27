export interface Author {
  id: string
  name: string
  avatar_url?: string
}

export interface Tag {
  id: string
  name: string
  slug: string
}

export interface BlogCategory {
  id: string
  name: string
  slug: string
}

export interface BlogPost {
  id: string
  slug: string
  title: string
  excerpt: string
  cover_url: string
  author: Author
  category?: BlogCategory
  tags: Tag[] | string[] // backend might return Tag objects or strings depending on endpoint
  published_at?: string
  reading_time_minutes: number
  content_html?: string
  content_json?: any // TipTap JSON
  status: 'draft' | 'published' | 'archived'
  views: number
  related?: BlogPost[]
}

export interface BlogComment {
  id: string
  post_id: string
  author_name: string
  content: string
  created_at: string
  status: 'pending' | 'approved' | 'rejected'
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
    category_slug?: string
    author_id?: string
    page_cursor?: string
    per_page?: number
    status?: string
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

  const getComments = (postId: string) => {
    return useFetch<BlogComment[]>(`${apiBase}/blog/posts/${postId}/comments`, {
      key: `blog-comments-${postId}`
    })
  }

  const postComment = async (postId: string, data: { author_name: string, author_email: string, content: string }) => {
    return await $fetch(`${apiBase}/blog/posts/${postId}/comments`, {
      method: 'POST',
      body: data
    })
  }

  const savePost = async (slug: string | null, data: Partial<BlogPost>) => {
    const url = slug ? `${apiBase}/blog/posts/${slug}` : `${apiBase}/blog/posts`
    const method = slug ? 'PATCH' : 'POST'
    return await $fetch(url, {
      method,
      body: data
    })
  }

  const deletePost = async (slug: string) => {
    return await $fetch(`${apiBase}/blog/posts/${slug}`, {
      method: 'DELETE'
    })
  }

  return {
    getPosts,
    getPost,
    getComments,
    postComment,
    savePost,
    deletePost
  }
}
