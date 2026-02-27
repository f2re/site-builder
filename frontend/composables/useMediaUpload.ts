/**
 * Composable for uploading media to MinIO via presigned URLs.
 * 
 * Flow:
 * 1. Request presigned upload URL from backend
 * 2. Upload file directly to MinIO using PUT request
 * 3. Confirm upload to backend to trigger processing
 * 4. Return public URL for immediate use
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
      // 1. Request presigned upload URL
      const uploadData = await $fetch<{
        upload_url: string
        object_name: string
        public_url: string
      }>('/media/upload-url', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: useRequestHeaders(['authorization']),
        body: {
          filename: file.name,
          content_type: file.type,
          context,
        },
      })

      // 2. Upload directly to MinIO
      await $fetch(uploadData.upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      })

      // 3. Confirm upload to trigger Celery processing
      await $fetch('/media/confirm', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: useRequestHeaders(['authorization']),
        body: {
          object_name: uploadData.object_name,
          alt,
          context,
          entity_id: entityId,
        },
      })

      // 4. Return public URL (will be converted to WebP in background)
      return uploadData.public_url
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
