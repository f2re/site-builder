export interface ProductCategory {
  id: string
  slug: string
  name: string
  parent_id?: string | null
  product_count: number
  is_active?: boolean
}

export interface ProductVariant {
  id: string
  name: string
  sku: string
  price: number
  stock_quantity: number
  attributes: Record<string, any>
}

export interface ProductImage {
  id: string
  url: string
  alt: string
  is_cover: boolean
  sort_order: number
}

export interface Product {
  id: string
  slug: string
  name: string
  description?: string
  description_html?: string
  content_json?: any // TipTap JSON content
  meta_title?: string
  meta_description?: string
  og_image_url?: string
  is_active: boolean
  is_featured: boolean
  category_id?: string | null
  category?: ProductCategory
  images: ProductImage[]
  variants: ProductVariant[]
  attributes: Record<string, any>
  created_at: string
  updated_at: string
  
  // Dynamic fields added by backend / computed
  price_display: string
  currency: string
  stock: number
  price_rub?: number // for Schema.org
}

export interface ProductShort {
  id: string
  name: string
  slug: string
  category_id?: string | null
  category_name?: string
  main_image_url?: string
  min_price: number
  is_active: boolean
  is_featured: boolean
  created_at: string
  updated_at: string

  // Dynamic fields
  price_display: string
  currency: string
  stock: number
}

export interface ProductListResponse {
  items: ProductShort[]
  next_cursor: string | null
  total?: number
}

export interface ProductCreate {
  name: string
  slug: string
  category_id?: string | null
  description?: string
  description_html?: string
  content_json?: any // TipTap JSON content
  meta_title?: string
  meta_description?: string
  is_active?: boolean
  is_featured?: boolean
  images?: Array<{ url: string, alt: string, is_cover?: boolean, sort_order?: number }>
  variants?: Array<{ id?: string, name: string, sku: string, price: number, stock_quantity?: number, attributes?: Record<string, any> }>
}

export const useProducts = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase
  const apiFetch = useApiFetch()

  // Public: Get products list
  const getProducts = (params?: {
    category_slug?: string
    price_min?: number
    price_max?: number
    page_cursor?: string
    per_page?: number
    currency?: string
    search?: string
  }) => {
    const query: Record<string, string | number | undefined> = { ...params }
    if (params?.search) {
      query.q = params.search
      delete query.search
    }
    return useFetch<ProductListResponse>(`${apiBase}/products`, {
      params: query,
      key: `products-${JSON.stringify(params)}`
    })
  }

  // Public: Get product by slug
  const getProductBySlug = (slug: string) => {
    return useFetch<Product>(`${apiBase}/products/${slug}`, {
      key: `product-${slug}`
    })
  }

  // Admin: Get all products (active & inactive)
  const adminGetProducts = (cursor?: string, per_page: number = 20) => {
    return useApi<ProductListResponse>(`/admin/products`, {
      params: { cursor, per_page },
      key: 'admin-products-list'
    })
  }

  // Admin: Get product by ID
  const adminGetProductById = (id: string) => {
    return useApi<Product>(`/admin/products/${id}`, {
      key: `admin-product-${id}`
    })
  }

  // Admin: Create product
  const createProduct = async (data: ProductCreate) => {
    return await apiFetch<Product>('/admin/products', {
      method: 'POST',
      body: data
    })
  }

  // Admin: Update product
  const updateProduct = async (id: string, data: Partial<ProductCreate>) => {
    return await apiFetch<Product>(`/admin/products/${id}`, {
      method: 'PUT',
      body: data
    })
  }

  // Admin: Delete product
  const deleteProduct = async (id: string) => {
    return await apiFetch(`/admin/products/${id}`, {
      method: 'DELETE'
    })
  }

  // Admin: Upload product image
  const adminUploadProductImage = async (productId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return await apiFetch<ProductImage>(`/admin/products/${productId}/images`, {
      method: 'POST',
      body: formData
    })
  }

  // Admin: Delete product image
  const adminDeleteProductImage = async (imageId: string) => {
    return await apiFetch(`/admin/products/images/${imageId}`, {
      method: 'DELETE'
    })
  }

  // Admin: Set product cover image
  const adminSetProductCoverImage = async (productId: string, image_id: string) => {
    return await apiFetch<ProductImage>(`/admin/products/${productId}/images/${image_id}/cover`, {
      method: 'PUT'
    })
  }

  // Public: Get categories
  const getCategories = () => {
    return useFetch<{ items: ProductCategory[] }>(`${apiBase}/products/categories`, {
      key: 'categories'
    })
  }

  // Admin: CRUD categories
  const adminGetCategories = () => {
    return useApi<ProductCategory[]>('/admin/categories', {
      key: 'admin-categories'
    })
  }

  const adminCreateCategory = async (data: any) => {
    return await apiFetch<ProductCategory>('/admin/categories', {
      method: 'POST',
      body: data
    })
  }

  const adminUpdateCategory = async (id: string, data: any) => {
    return await apiFetch<ProductCategory>(`/admin/categories/${id}`, {
      method: 'PUT',
      body: data
    })
  }

  const adminDeleteCategory = async (id: string) => {
    return await apiFetch(`/admin/categories/${id}`, {
      method: 'DELETE'
    })
  }

  return {
    getProducts,
    getProductBySlug,
    adminGetProducts,
    adminGetProductById,
    createProduct,
    updateProduct,
    deleteProduct,
    adminUploadProductImage,
    adminDeleteProductImage,
    adminSetProductCoverImage,
    getCategories,
    adminGetCategories,
    adminCreateCategory,
    adminUpdateCategory,
    adminDeleteCategory
  }
}
