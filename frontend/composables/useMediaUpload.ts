/**
 * Composable for uploading media to backend.
 */

export const useMediaUpload = () => {
  const config = useRuntimeConfig()
  const toast = useToast()

  async function uploadImage(
    file: File,
    alt: string,
    context: 'blog' | 'product',
    entityId?: number
  ): Promise<string> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('context', context)
      formData.append('alt', alt)
      if (entityId) {
        formData.append('entity_id', entityId.toString())
      }

      const data = await $fetch<{
        id: number
        public_url: string
      }>('/media/upload', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: useRequestHeaders(['authorization']),
        body: formData,
      })

      return data.public_url
    } catch (error: any) {
      console.error('Image upload failed:', error)
      toast.error('Ошибка загрузки изображения')
      throw new Error('Не удалось загрузить изображение')
    }
  }

  return {
    uploadImage,
  }
}
