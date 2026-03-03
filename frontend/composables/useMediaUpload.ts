/**
 * Composable for uploading media to backend.
 */

export const useMediaUpload = () => {
  const toast = useToast()
  const apiFetch = useApiFetch()

  async function uploadImage(
    file: File,
    alt: string,
    context: 'blog' | 'product' | 'content',
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

      const data = await apiFetch<{
        url: string
      }>('/media/upload', {
        method: 'POST',
        body: formData,
      })

      // The backend returns { url: string } according to api_contracts.md section 11
      return data.url
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
