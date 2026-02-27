export interface ProductCategory {
  id: string
  slug: string
  name: string
  parent_id: string | null
  product_count: number
}

export interface Product {
  id: string
  slug: string
  name: string
  price_rub: number
  price_display: number
  currency: string
  stock: number
  images: string[]
  category: ProductCategory
  description?: string
  attributes?: Record<string, any>
  related?: Product[]
}

export interface ProductListResponse {
  items: Product[]
  next_cursor: string | null
  total: number
}

export const useProducts = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getProducts = (params?: {
    category_slug?: string
    price_min?: number
    price_max?: number
    page_cursor?: string
    per_page?: number
    currency?: string
  }) => {
    return useFetch<ProductListResponse>(`${apiBase}/products`, {
      params,
      key: `products-${JSON.stringify(params)}`
    })
  }

  const getProduct = (slug: string) => {
    return useFetch<Product>(`${apiBase}/products/${slug}`, {
      key: `product-${slug}`
    })
  }

  const getCategories = () => {
    return useFetch<{ items: ProductCategory[] }>(`${apiBase}/products/categories`, {
      key: 'categories'
    })
  }

  return {
    getProducts,
    getProduct,
    getCategories
  }
}
