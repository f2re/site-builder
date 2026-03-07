export interface Author {
  id: string
  name: string
  avatar_url?: string
  bio?: string
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
  summary?: string          // alias for excerpt
  cover_url: string
  cover_image?: string      // alias for cover_url
  og_image_url?: string
  carousel_images?: string[]
  author: Author
  category?: BlogCategory
  tags: Tag[] | string[]    // backend might return Tag objects or strings depending on endpoint
  published_at?: string
  reading_time_minutes: number
  reading_time?: number     // alias for reading_time_minutes
  content_html?: string
  content_json?: Record<string, unknown> // TipTap JSON
  status: 'draft' | 'published' | 'archived' | 'deleted'
  is_featured?: boolean
  views: number
  related?: BlogPost[]
  meta_title?: string
  meta_description?: string
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
  const apiFetch = useApiFetch()

  // Public/Admin list posts
  const getPosts = (params?: {
    tag?: string
    category_slug?: string
    author_id?: string
    page_cursor?: string
    per_page?: number
    status?: string
  }) => {
    // We use useApi here because if the user is an admin,
    // we want to send the token to see drafts.
    return useApi<BlogListResponse>(`/blog/posts`, {
      params,
      key: `blog-posts-${JSON.stringify(params)}`
    })
  }

  // Public/Admin get post
  const getPost = (slug: string) => {
    return useApi<BlogPost>(`/blog/posts/${slug}`, {
      key: `blog-post-${slug}`
    })
  }

  // Comments
  const getComments = (postId: string) => {
    const config = useRuntimeConfig()
    return useFetch<BlogComment[]>(`${config.public.apiBase}/blog/posts/${postId}/comments`, {
      key: `blog-comments-${postId}`
    })
  }

  const postComment = async (postId: string, data: { author_name: string, author_email: string, content: string }) => {
    return await apiFetch(`/blog/posts/${postId}/comments`, {
      method: 'POST',
      body: data
    })
  }

  // Get all tags (for tag cloud)
  const getTags = () => {
    return useApi<Tag[]>(`/blog/tags`, {
      key: 'blog-tags'
    })
  }

  // Admin mutations
  const savePost = async (slug: string | null, data: Partial<BlogPost>) => {
    const url = slug ? `/admin/blog/posts/${slug}` : `/admin/blog/posts`
    const method = slug ? 'PUT' : 'POST'
    return await apiFetch<BlogPost>(url, {
      method,
      body: data
    })
  }

  const deletePost = async (postId: string) => {
    return await apiFetch(`/admin/blog/posts/${postId}`, {
      method: 'DELETE'
    })
  }

  // Upload blog post cover image
  const uploadBlogCover = async (postId: string, file: File): Promise<{ cover_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    return await apiFetch<{ cover_url: string }>(`/admin/blog/posts/${postId}/cover`, {
      method: 'POST',
      body: formData
    })
  }

  return {
    getPosts,
    getPost,
    getComments,
    postComment,
    getTags,
    savePost,
    deletePost,
    uploadBlogCover,
  }
}
