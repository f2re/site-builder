export interface Page {
  id: string
  slug: string
  title: string
  content: string
  meta_title?: string
  meta_description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PageCreate {
  slug: string
  title: string
  content: string
  meta_title?: string
  meta_description?: string
  is_active?: boolean
}

export interface PageUpdate {
  slug?: string
  title?: string
  content?: string
  meta_title?: string
  meta_description?: string
  is_active?: boolean
}

export function usePages() {
  const config = useRuntimeConfig()

  // Public: Get page by slug
  const getPageBySlug = (slug: string) => {
    return useFetch<Page>(`${config.public.apiBase}/v1/pages/${slug}`, {
      key: `page-${slug}`
    })
  }

  // Admin: List all pages
  const getPages = () => {
    return useFetch<Page[]>(`${config.public.apiBase}/v1/admin/pages/`, {
      key: 'admin-pages-list',
      watch: false
    })
  }

  // Admin: Get page by ID
  const getPageById = (id: string) => {
    return useFetch<Page>(`${config.public.apiBase}/v1/admin/pages/${id}`, {
      key: `admin-page-${id}`
    })
  }

  // Admin: Create page
  const createPage = async (data: PageCreate) => {
    return await $fetch<Page>(`${config.public.apiBase}/v1/admin/pages/`, {
      method: 'POST',
      body: data
    })
  }

  // Admin: Update page
  const updatePage = async (id: string, data: PageUpdate) => {
    return await $fetch<Page>(`${config.public.apiBase}/v1/admin/pages/${id}`, {
      method: 'PATCH',
      body: data
    })
  }

  // Admin: Delete page
  const deletePage = async (id: string) => {
    return await $fetch(`${config.public.apiBase}/v1/admin/pages/${id}`, {
      method: 'DELETE'
    })
  }

  return {
    getPageBySlug,
    getPages,
    getPageById,
    createPage,
    updatePage,
    deletePage
  }
}
